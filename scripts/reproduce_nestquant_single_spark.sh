#!/usr/bin/env bash
# Reproduce the published NestQuant single-DGX-Spark benchmark from a scorer host.
set -Eeuo pipefail

IMAGE='docker.io/jarrelscy/nestquant@sha256:3859a4e0018ec915ca0d4a3f9488158026fc2525534051433e2b37a729102364'
MODEL_REV='4023870a6f2c6097e37fa5d2e54040db64b011e9'
RECIPE_REV='43d971547409b645a2ffd9ae610c8b0d44781b9d'
GRADER_REV='f2ac7876c1782047fe4ac37290a1466daa3a1c05'
REASONING=on
SPARK_TARGET=${SPARK_SSH:-}
SSH_IDENTITY=${SPARK_SSH_IDENTITY:-}
KNOWN_HOSTS=${SPARK_KNOWN_HOSTS:-$HOME/.ssh/known_hosts}
OUT_DIR=${OUT_DIR:-"$PWD/nestquant-spark-bench"}
REMOTE_DATA=${REMOTE_DATA:-'$HOME/nq-flash'}
REUSE=0
SMOKE=0
KEEP=0
LOCAL_PORT=${LOCAL_PORT:-}
STARTED=0
TUNNEL_PID=
TMP=

usage() {
  cat <<'EOF'
Usage: reproduce_nestquant_single_spark.sh --spark [user@]host [options]

Downloads and prepares the pinned model/image on a native ARM64 DGX Spark,
starts the accepted 2630-slot 20%-fixed 75/25 sampled-ahead server, and runs
the official 80-task x 2-repeat Spark Bench scorer on this machine.

  --reasoning on|off   Benchmark mode (default: on)
  --reuse-serving      Use an already healthy service on Spark port 8001
  --smoke-test         Run IF-01 repeat 1 through the official scorer
  --keep-serving       Leave a service started by this command running
  --out-dir PATH       Local evidence directory
  --identity PATH      SSH private-key path
  --known-hosts PATH   SSH known_hosts file
  --local-port PORT    Local tunnel port (default: choose a free port)
  -h, --help           Show this help

Set VLLM_API_KEY in the environment or enter it at the hidden prompt. An
optional HF_TOKEN raises Hugging Face download rate limits and is sent only
through protected standard input to the remote process.
EOF
}

while (($#)); do
  case "$1" in
    --spark) SPARK_TARGET=${2:?missing Spark SSH target}; shift 2 ;;
    --reasoning) REASONING=${2:?missing reasoning mode}; shift 2 ;;
    --reuse-serving) REUSE=1; shift ;;
    --smoke-test) SMOKE=1; shift ;;
    --keep-serving) KEEP=1; shift ;;
    --out-dir) OUT_DIR=${2:?missing output path}; shift 2 ;;
    --identity) SSH_IDENTITY=${2:?missing identity path}; shift 2 ;;
    --known-hosts) KNOWN_HOSTS=${2:?missing known_hosts path}; shift 2 ;;
    --local-port) LOCAL_PORT=${2:?missing port}; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$SPARK_TARGET" ]] || { echo 'Pass --spark [user@]host (or set SPARK_SSH).' >&2; exit 2; }
[[ "$REASONING" == on || "$REASONING" == off ]] || { echo '--reasoning must be on or off.' >&2; exit 2; }
for command in ssh git curl python3; do command -v "$command" >/dev/null || { echo "Missing local command: $command" >&2; exit 1; }; done

if [[ -z ${VLLM_API_KEY:-} ]]; then
  [[ -t 0 ]] || { echo 'Set VLLM_API_KEY when standard input is not interactive.' >&2; exit 2; }
  read -rsp 'Private serving API key: ' VLLM_API_KEY
  echo
  export VLLM_API_KEY
fi
[[ -n "$VLLM_API_KEY" ]] || { echo 'The serving API key cannot be empty.' >&2; exit 2; }

SSH=(ssh -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes
  -o "UserKnownHostsFile=$KNOWN_HOSTS" -o ConnectTimeout=20
  -o ServerAliveInterval=30 -o ServerAliveCountMax=6)
[[ -z "$SSH_IDENTITY" ]] || SSH+=(-i "$SSH_IDENTITY")

cleanup() {
  local rc=$?
  [[ -z "$TUNNEL_PID" ]] || kill "$TUNNEL_PID" 2>/dev/null || true
  if ((STARTED)) && ((!KEEP)); then
    "${SSH[@]}" "$SPARK_TARGET" \
      "cd \"\$HOME/nestquant-spark-bench-reproduce\" && NQ_FLASH_DATA=\"\$HOME/nq-flash\" NQ_FLASH_CONTAINER=nq-spark-bench-${REASONING} NQ_THINKING=${REASONING} python3 spark/flash/sampled_ahead_sentinel/recipe.py down" \
      >/dev/null 2>&1 || true
  fi
  [[ -z "$TMP" ]] || rm -rf "$TMP"
  exit "$rc"
}
trap cleanup EXIT INT TERM

echo "Checking native Spark target and SSH host key..."
arch=$("${SSH[@]}" "$SPARK_TARGET" uname -m)
[[ "$arch" == aarch64 ]] || { echo "Expected native aarch64 Spark; got $arch" >&2; exit 1; }

if ((!REUSE)); then
  echo "Preparing pinned image/model and starting reasoning=$REASONING (this can take hours on first use)..."
  remote_script=$(cat <<'REMOTE'
set -Eeuo pipefail
reasoning=$1
phase=$2
repo="$HOME/nestquant-spark-bench-reproduce"
data="$HOME/nq-flash"
if [[ ! -d "$repo/.git" ]]; then
  git clone --filter=blob:none https://github.com/jarrelscy/nestquant.git "$repo"
fi
git -C "$repo" fetch --force origin 43d971547409b645a2ffd9ae610c8b0d44781b9d
git -C "$repo" checkout --detach --force 43d971547409b645a2ffd9ae610c8b0d44781b9d
export NQ_SOURCE_ROOT="$repo"
export NQ_FLASH_DATA="$data"
export NQ_FLASH_IMAGE='docker.io/jarrelscy/nestquant@sha256:3859a4e0018ec915ca0d4a3f9488158026fc2525534051433e2b37a729102364'
export NQ_FLASH_CONTAINER="nq-spark-bench-${reasoning}"
export NQ_THINKING="$reasoning"
export VLLM_API_KEY
docker pull "$NQ_FLASH_IMAGE"
runner="$repo/spark/flash/sampled_ahead_sentinel/run_spark_kld.sh"
bash "$runner" fetch
if [[ "$phase" == prepare ]]; then
  if [[ ! -f "$data/fp8-backbone/config.json" || ! -f "$data/repack-tp1/rank0.json" ]]; then
    bash "$runner" prepare
    exit 75
  fi
  exit 0
fi
[[ "$phase" == up ]] || { echo 'Invalid remote phase.' >&2; exit 2; }
python3 "$repo/spark/flash/sampled_ahead_sentinel/recipe.py" stage
python3 "$repo/spark/flash/sampled_ahead_sentinel/recipe.py" up
for ((i=0; i<720; i++)); do
  if curl -fsS -H "Authorization: Bearer $VLLM_API_KEY" http://127.0.0.1:8001/v1/models >/dev/null; then
    exit 0
  fi
  sleep 10
done
echo 'Spark service did not become ready within two hours.' >&2
exit 1
REMOTE
)
  run_remote_phase() {
    local phase=$1
    { printf '%s\n' "$VLLM_API_KEY"; printf '%s\n' "${HF_TOKEN:-}"; printf '%s\n' "$remote_script"; } | \
      "${SSH[@]}" "$SPARK_TARGET" 'IFS= read -r VLLM_API_KEY; IFS= read -r HF_TOKEN; export VLLM_API_KEY HF_TOKEN; bash -s --' "$REASONING" "$phase"
  }
  set +e
  run_remote_phase prepare
  prepare_rc=$?
  set -e
  if ((prepare_rc == 75)); then
    echo 'Preparation completed; rebooting the idle Spark to release unified-memory file cache...'
    "${SSH[@]}" "$SPARK_TARGET" 'sudo -n reboot' >/dev/null 2>&1 || true
    ready=0
    for ((i=0; i<90; i++)); do
      sleep 10
      if "${SSH[@]}" "$SPARK_TARGET" true >/dev/null 2>&1; then ready=1; break; fi
    done
    ((ready)) || { echo 'Spark did not return after the preparation reboot.' >&2; exit 1; }
  elif ((prepare_rc != 0)); then
    exit "$prepare_rc"
  fi
  run_remote_phase up
  STARTED=1
fi

if [[ -z "$LOCAL_PORT" ]]; then
  LOCAL_PORT=$(python3 - <<'PY'
import socket
s=socket.socket(); s.bind(('127.0.0.1', 0)); print(s.getsockname()[1]); s.close()
PY
)
fi
echo "Opening authenticated local tunnel on port $LOCAL_PORT..."
"${SSH[@]}" -N -L "127.0.0.1:${LOCAL_PORT}:127.0.0.1:8001" "$SPARK_TARGET" &
TUNNEL_PID=$!
for ((i=0; i<60; i++)); do
  if curl -fsS -H "Authorization: Bearer $VLLM_API_KEY" "http://127.0.0.1:${LOCAL_PORT}/v1/models" >/dev/null 2>&1; then break; fi
  kill -0 "$TUNNEL_PID" 2>/dev/null || { echo 'SSH tunnel exited before readiness.' >&2; exit 1; }
  sleep 1
done
curl -fsS -H "Authorization: Bearer $VLLM_API_KEY" "http://127.0.0.1:${LOCAL_PORT}/v1/models" >/dev/null || { echo 'Serving API is unavailable through the tunnel.' >&2; exit 1; }

TMP=$(mktemp -d)
echo "Installing the pinned official scorer in an isolated environment..."
git clone -q https://github.com/jarrelscy/spark-bench.git "$TMP/spark-bench"
git -C "$TMP/spark-bench" checkout -q --detach "$GRADER_REV"
python3 -m venv "$TMP/venv"
"$TMP/venv/bin/python" -m pip -q install --upgrade pip
"$TMP/venv/bin/python" -m pip -q install pillow playwright
if ! command -v chromium >/dev/null && ! command -v google-chrome >/dev/null; then
  "$TMP/venv/bin/python" -m playwright install chromium
fi

mkdir -p "$OUT_DIR"
export SPARK_BENCH_API_KEY="$VLLM_API_KEY"
export SPARK_BENCH_FORCE_TEMPERATURE=0.7
export SPARK_BENCH_CONTEXT=262144
export SPARK_BENCH_SEED_PER_REPEAT=42
unset SPARK_BENCH_REASONING_EFFORT
if [[ "$REASONING" == on ]]; then
  export SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"chat_template_kwargs":{"enable_thinking":true}}'
else
  export SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"chat_template_kwargs":{"enable_thinking":false}}'
fi

args=(eval --endpoint "http://127.0.0.1:${LOCAL_PORT}/v1" --model glm-5.3-flash-nq
  --label "nestquant-single-spark-reasoning-${REASONING}" --topology single-dgx-spark-gb10
  --parallelism TP1 --spec-decode mtp2-probabilistic --repeats 2 --temperature 0.7
  --thinking "$REASONING" --uncapped --tier all --skip-throughput --timeout 7200
  --out-dir "$OUT_DIR")
if ((SMOKE)); then args+=(--scenario-ids IF-01 --repeat-indices 1); fi

cat >"$OUT_DIR/reproduction.json" <<EOF
{"image":"$IMAGE","model_revision":"$MODEL_REV","recipe_revision":"$RECIPE_REV","grader_revision":"$GRADER_REV","reasoning":"$REASONING","smoke_test":$SMOKE}
EOF
echo "Running official scorer (reasoning=$REASONING, smoke=$SMOKE)..."
cd "$TMP/spark-bench"
"$TMP/venv/bin/python" -u spark_bench.py "${args[@]}" 2>&1 | tee "$OUT_DIR/benchmark.log"
echo "Complete. Evidence: $OUT_DIR"
