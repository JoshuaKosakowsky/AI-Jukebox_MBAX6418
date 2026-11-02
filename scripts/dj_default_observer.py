"""Private observational guard for one default-only run; never stores credentials."""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from unittest.mock import patch
import hashlib, io, json, os, wave
from uuid import UUID


def initial(path, source):
    value={'source_commit':source,'mode':'default voice only','limits':{'text':3,'speech':3,'art':0,'music':0},'attempts':{'text':0,'speech':0,'art':0,'music':0},'events':[],'jobs':[],'stop':None,'prevented_requests':0,'guard_pids':[]}
    with Path(path).open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2)


def install(path):
    from jukebox.providers import ClassProviders, ProviderFailure
    from jukebox.contracts import SafeError
    from jukebox.sessions import SessionStore
    state=Path(path);lock=RLock();stack=ExitStack()
    def update(fn):
        with lock:
            value=json.loads(state.read_text(encoding='utf-8'));fn(value)
            temp=state.with_suffix('.tmp');temp.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');temp.replace(state)
    def event(kind,**data):update(lambda v:v['events'].append({'kind':kind,'at_utc':datetime.now(timezone.utc).isoformat(),**data}))
    def stopped(role,error):
        safe=error.error.model_dump(mode='json') if isinstance(error,ProviderFailure) else {'exception_type':type(error).__name__}
        def mark(v):
            if v['stop'] is None:v['stop']={'stage':role,'error':safe,'at_utc':datetime.now(timezone.utc).isoformat()}
        update(mark)
    update(lambda v:v['guard_pids'].append(os.getpid()) if os.getpid() not in v['guard_pids'] else None)
    constructor=ClassProviders.__init__
    def observed_init(self,*args,**kwargs):
        constructor(self,*args,**kwargs)
        def response_seen(response):
            port=response.request.url.port
            event('provider_http_response',role='text' if port==9001 else 'speech' if port==9008 else 'unexpected',status=response.status_code,route=response.request.url.path)
        self.client.event_hooks['response'].append(response_seen)
    stack.enter_context(patch.object(ClassProviders,'__init__',observed_init))
    request=ClassProviders._request
    def counted(self,role,route,payload=None):
        def reserve(v):
            invalid=(v['stop'] is not None or role not in ('text','speech') or v['attempts'].get(role,0)>=v['limits'].get(role,0) or (role=='speech' and payload is not None and 'ref_audio' in payload))
            if invalid:
                v['prevented_requests']+=1
            else:
                v['attempts'][role]+=1;v['events'].append({'kind':'provider_attempt','role':role,'route':route,'attempt':v['attempts'][role],'at_utc':datetime.now(timezone.utc).isoformat(),'default_voice':role=='speech'})
            reserve.allowed=not invalid
        update(reserve)
        if not reserve.allowed:raise ProviderFailure(SafeError(code='generation_failed',message='The bounded default-DJ test stopped before an additional provider request.',retryable=False))
        return request(self,role,route,payload)
    stack.enter_context(patch.object(ClassProviders,'_request',counted))
    text=ClassProviders.text
    def observed_text(self,prompt,*,thinking=None):
        try:
            result=text(self,prompt,thinking=thinking);event('text_completed',prompt=prompt,commentary=result);return result
        except Exception as error:stopped('text',error);raise
    stack.enter_context(patch.object(ClassProviders,'text',observed_text))
    speech=ClassProviders.speech
    def observed_speech(self,text,*,reference=None):
        try:
            if reference is not None:raise ProviderFailure(SafeError(code='rejected',message='Reference voices are outside this default-DJ test.',retryable=False))
            result=speech(self,text)
            with wave.open(io.BytesIO(result.content),'rb') as wav:
                frames=wav.getnframes();rate=wav.getframerate();width=wav.getsampwidth();channels=wav.getnchannels();assert len(wav.readframes(frames))==frames*width*channels
            event('speech_completed',bytes=len(result.content),sha256=hashlib.sha256(result.content).hexdigest(),duration_seconds=frames/rate,default_voice=True)
            return result
        except Exception as error:stopped('speech',error);raise
    stack.enter_context(patch.object(ClassProviders,'speech',observed_speech))
    generate=SessionStore.generate_dj_speech
    def observed_job(self,session,job_id,providers):
        event('job_started',job_id=str(job_id),track_id=str(session.jobs[job_id].track_id),reference_present=job_id in session.speech_references)
        try:return generate(self,session,job_id,providers)
        finally:
            snapshot=self.snapshot(session).model_dump(mode='json');job=next(j for j in snapshot['jobs'] if j['id']==str(job_id));track=next(t for t in snapshot['tracks'] if t['id']==job['track_id'])
            def retain(v):
                v['jobs'].append(job);v['last_snapshot']=snapshot
                if job['state']=='failed' and v['stop'] is None:v['stop']={'stage':'application','error':job['error']}
            update(retain)
            if track['speech'] is not None:
                media=self.get_media(session,UUID(track['speech']['id']));folder=state.parent/'media';folder.mkdir(exist_ok=True);(folder/(str(job_id)+'.wav')).write_bytes(media.content)
            event('job_finished',job=job,title=track['title'])
    stack.enter_context(patch.object(SessionStore,'generate_dj_speech',observed_job))
    for name in ['queue_playback','start_playback','advance_playback','set_phase','pause_playback','resume_playback']:
        method=getattr(SessionStore,name)
        def observe(self,session,*args,_method=method,_name=name,**kwargs):
            result=_method(self,session,*args,**kwargs)
            event('playback_action',action=_name,playback=self.snapshot(session).playback.model_dump(mode='json'))
            return result
        stack.enter_context(patch.object(SessionStore,name,observe))
    return stack
