"""Linux sandbox: permit pthreads without permitting subprocess creation.

RLIMIT_NPROC=0 prevents CODE-12's required threads on unprivileged Linux.
Use an inherited seccomp filter instead. Fail closed if unavailable.
"""
import ctypes
import errno


def restrict_process_creation():
    lib = ctypes.CDLL('libseccomp.so.2', use_errno=True)
    class Cmp(ctypes.Structure):
        _fields_ = [('arg', ctypes.c_uint), ('op', ctypes.c_int),
                    ('datum_a', ctypes.c_uint64), ('datum_b', ctypes.c_uint64)]
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    lib.seccomp_rule_add_array.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                                          ctypes.c_int, ctypes.c_uint, ctypes.POINTER(Cmp)]
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    ctx = lib.seccomp_init(0x7fff0000)  # SCMP_ACT_ALLOW
    if not ctx:
        raise RuntimeError('seccomp_init failed')
    def rule(name, error, cmp=None):
        nr = lib.seccomp_syscall_resolve_name(name.encode())
        if nr < 0:
            return
        rc = lib.seccomp_rule_add_array(ctx, 0x50000 | error, nr,
                                        int(cmp is not None), ctypes.byref(cmp) if cmp else None)
        if rc:
            raise RuntimeError(f'seccomp rule {name} failed: {rc}')
    try:
        for name in ('fork', 'vfork', 'execve', 'execveat'):
            rule(name, errno.EPERM)
        # glibc retries pthread creation with clone when clone3 is unavailable.
        # Pointer-based clone3 flags cannot be filtered safely by classic BPF.
        rule('clone3', errno.ENOSYS)
        rule('clone', errno.EPERM, Cmp(0, 7, 0x10000, 0))  # MASKED_EQ: no CLONE_THREAD
        rc = lib.seccomp_load(ctx)
        if rc:
            raise RuntimeError(f'seccomp_load failed: {rc}')
    finally:
        lib.seccomp_release(ctx)
