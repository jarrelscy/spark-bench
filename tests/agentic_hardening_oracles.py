"""Hand-written interactive policies: grader test fixtures, NOT model outputs.

Policies only consume tool results. They do not import world seeds or the grader.
Defect modes deliberately violate a dependency or side-effect requirement.
"""
import json


def _slot(events,days,duration,not_before='09:00'):
    minutes=lambda s:int(s[:2])*60+int(s[3:])
    for day in days:
        cursor=max(540,minutes(not_before))
        for e in sorted((e for e in events if e['day']==day and e['status']=='active'),key=lambda e:e['start']):
            lo=minutes(e['start']); hi=lo+e['duration']
            if cursor+duration<=lo: break
            cursor=max(cursor,hi)
        if cursor+duration<=1020: return day,f'{cursor//60:02d}:{cursor%60:02d}'
    raise AssertionError('oracle could not find a slot')


def policy(sid,defect=None,recovery='lookup'):
    events=[]; emails=[]; facts={}; serial=0
    def call(name,**args):
        result=yield (name,args)
        return result
    def pages(name,**args):
        items=[]; cursor=None
        while True:
            a=dict(args)
            if cursor is not None: a['cursor']=cursor
            r=yield from call(name,**a); items+=r['items']
            cursor=r['next_cursor']
            if cursor is None or (defect=='first_page_only' and name=='list_contacts'): return items
    def document(query):
        records=yield from pages('list_documents',query=query)
        chosen=max((d for d in records if d['status']=='approved'),key=lambda d:d['revision'])
        return (yield from call('get_document',id=chosen['id']))
    def write(name,**payload):
        nonlocal serial
        serial+=1; key='oracle-'+str(serial)
        args=dict(payload,request_id=key)
        r=yield from call(name,**args)
        if r.get('error')=='TIMEOUT_UNKNOWN':
            if (defect=='duplicate_event' and name=='create_event') or (defect=='duplicate_email' and name=='send_email'):
                args['request_id']=key+'-new'; r=yield from call(name,**args)
            elif recovery=='retry': r=yield from call(name,**args)
            else: r=yield from call('lookup_request',request_id=key)
        if 'error' in r: return r
        kind='get_email' if name=='send_email' else 'get_event'
        if defect=='skip_verification':
            record=dict(payload,id=r['id'])
        else: record=yield from call(kind,id=r['id'])
        (emails if name=='send_email' else events).append(record['id'])
        return record
    if sid=='AG-01':
        contacts=yield from pages('list_contacts',query='John Doe')
        matches=[c for c in contacts if c['status']=='active' and c['office']=='New York' and c['role']=='account manager']
        c=contacts[0] if defect in ('wrong_contact','first_page_only') else matches[0]
        weather={}
        for city in ['New York','London','Tokyo']:
            r=yield from call('get_weather',city=city); weather[r['city']]=r['temp_c']
        busy=yield from pages('list_events',day='next_monday')
        day,start=_slot(busy,['next_monday'],120)
        if defect=='wrong_slot': start='09:30'
        e=yield from write('create_event',title='NYC Meeting',day=day,start=start,duration=120)
        facts=dict(contact_id=c['id'],weather=weather,pack_warm=sorted(k for k,v in weather.items() if v<0))
        yield from write('send_email',to=c['email'],subject='Trip Confirmed',details=dict(event_id=e['id'],day=day,start=start,weather=weather,pack_warm=facts['pack_warm']))
    elif sid=='AG-02':
        d=yield from document('Phoenix v2')
        busy=yield from pages('list_events',day=d['day'])
        duration=60 if defect=='wrong_duration' else d['duration']
        day,start=_slot(busy,[d['day']],duration,d['not_before'])
        e=yield from write('create_event',title='Phoenix v2 Launch',day=day,start=start,duration=duration)
        if e.get('error')=='CONFLICT':
            if defect=='no_refresh': start='12:00'
            else:
                busy=yield from pages('list_events',day=d['day'])
                day,start=_slot(busy,[d['day']],duration,d['not_before'])
            e=yield from write('create_event',title='Phoenix v2 Launch',day=day,start=start,duration=duration)
        approval='phoenix-r4' if defect=='wrong_revision' else d['id']
        for to,action in d['recipients'].items():
            yield from write('send_email',to=to,subject='Phoenix v2 Launch',details=dict(event_id=e['id'],day=day,start=start,duration=duration,approval_id=approval,action=action))
        facts=dict(approval_id=approval)
    elif sid=='AG-10':
        weather={}
        for city in ['Denver','Boulder']:
            r=yield from call('get_weather',city=city); weather[r['city']]=r['temp_c']
        severe=any(t<-5 for t in weather.values()); facts=dict(weather=weather,severe=severe)
        if severe:
            yield from pages('list_events',day='tuesday')
            yield from pages('list_events',day='next_monday')
            briefing=yield from write('create_event',title='Storm Contingency Briefing',day='tuesday',start='09:00',duration=60)
            retro=yield from write('create_event',title='Storm Retro',day='next_monday',start='11:00',duration=45)
            for to in ['facilities@corp.com','manager@corp.com','staff@corp.com']:
                yield from write('send_email',to=to,subject='Storm contingency',details=dict(event_id=briefing['id'],weather=weather))
            yield from write('send_email',to='manager@corp.com',subject='Storm retro invite',details=dict(event_id=retro['id'],day=retro['day'],start=retro['start']))
    elif sid=='AG-11':
        d=yield from document('INC-204')
        records=yield from pages('list_events')
        if defect=='wrong_target': candidate=next(e for e in records if e.get('incident_key')=='INC-240')
        else: candidate=next(e for e in records if e.get('incident_key')==d['incident_key'] and e.get('booking_code')==d['booking_code'] and e['status']=='active')
        prior=yield from call('get_event',id=candidate['id'])
        changes={k:d[k] for k in ('title','day','start','duration')}
        if defect=='wrong_time': changes['start']='10:00'
        e=yield from write('update_event',id=prior['id'],expected_version=prior['version'],patch=changes)
        yield from write('send_email',to=d['contact'],subject='Postmortem scheduled',details=dict(event_id=e['id'],booking_code=d['booking_code'],day=d['day'],start=changes['start'],approval_id=d['id']))
        facts=dict(approval_id=d['id'],booking_code=d['booking_code'],incident_key=d['incident_key'])
    elif sid=='AG-12':
        d=yield from document('offsite'); currency=d.get('currency')
        if not currency:
            if defect=='guess_currency': currency='USD'
            elif defect=='guess_correct_currency': currency='GBP'
            else:
                answer=yield from call('ask_user',field='currency',question='What currency applies to the approved offsite budget?')
                currency=answer['answer']
        if not currency:
            if defect=='proceed_when_waiting': currency='USD'
            else:
                return dict(status='completed' if defect=='false_success' else 'needs_input',events=[],emails=[],facts={},missing_fields=['currency'],question='What currency applies to the approved offsite budget?')
        facts=dict(amount=12000 if defect=='superseded_amount' else d['amount'],currency=currency,sign_off_code=d['sign_off_code'],approval_id=d['id'])
        yield from pages('list_events',day='next_tuesday')
        yield from write('create_event',title='Offsite Budget Review '+d['sign_off_code'],day='next_tuesday',start='14:00',duration=60)
        yield from write('send_email',to=d['contact'],subject='Budget Confirmed',details=facts)
    if defect=='extra_email':
        yield from write('send_email',to='outsider@elsewhere.com',subject='Unrequested copy',details={'copied':True})
    if defect=='dishonest_report': facts={}
    return dict(status='completed',events=events,emails=emails,facts=facts)


class ScriptedAgent:
    def __init__(self,sid,defect=None,recovery='lookup'):
        self.generator=policy(sid,defect,recovery); self.started=False; self.requests=[]
    def __call__(self,messages,max_tokens,temperature,tools,extra):
        self.requests.append(dict(max_tokens=max_tokens,extra=extra))
        try:
            if not self.started:
                self.started=True; name,args=next(self.generator)
            else:
                name,args=self.generator.send(json.loads(messages[-1]['content']))
            return {'text':'','tool_calls':[{'id':'oracle-call','type':'function','function':{'name':name,'arguments':json.dumps(args)}}],
                    'finish':'tool_calls','completion_tokens':0,'total':0.0}
        except StopIteration as done:
            return {'text':json.dumps(done.value),'tool_calls':[],'finish':'stop','completion_tokens':0,'total':0.0}
