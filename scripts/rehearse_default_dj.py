"""Explicit offline rehearsal: real bundled songs, synthetic DJ transport only."""
from pathlib import Path
from tempfile import TemporaryDirectory
import io,json,sys,wave,tempfile,argparse
import httpx
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from jukebox.app import create_app
from jukebox.config import Settings
from jukebox.providers import ClassProviders,PROBES
from dj_default_observer import initial,install

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",help="Optional safe JSON result path; no raw audio retained")
    args=parser.parse_args()
    root=Path(tempfile.gettempdir()).resolve()
    settings=Settings.load(None,{f'JUKEBOX_{role}_{suffix}':value for role,port in [('TEXT',9001),('SPEECH',9008)] for suffix,value in [('ENDPOINT',f'http://dobolyi.com:{port}/v1'),('API_KEY','synthetic-offline-only')]})
    stream=io.BytesIO()
    with wave.open(stream,'wb') as wav:wav.setparams((1,2,16000,0,'NONE','not compressed'));wav.writeframes(b'\x10\x00'*16000)
    results=[]
    for mode in ['success','text_failure','speech_failure']:
     with TemporaryDirectory(prefix='rehearsal-',dir=root) as temp:
      assert Path(temp).resolve().is_relative_to(root.resolve());state=Path(temp)/'state.json';initial(state,'offline-rehearsal')
      wire=[]
      def respond(request):
       wire.append(request.url.port);payload=json.loads(request.content)
       if request.url.port==9001:
        if mode=='text_failure':return httpx.Response(200,json={'model':PROBES['text']['request']['model'],'choices':[{'message':{'content':''},'finish_reason':'length'}]})
        return httpx.Response(200,json={'model':PROBES['text']['request']['model'],'choices':[{'message':{'content':'A synthetic introduction for our next bundled song.'},'finish_reason':'stop'}]})
       assert request.url.port==9008 and 'ref_audio' not in payload
       if mode=='speech_failure':return httpx.Response(503,text='PRIVATE-SYNTHETIC-MARKER')
       return httpx.Response(200,content=stream.getvalue(),headers={'content-type':'audio/wav'})
      with install(state):
       app=create_app(settings)
       with TestClient(app,base_url='http://localhost') as client:
        app.state.providers.close();app.state.providers=ClassProviders(settings,transport=httpx.MockTransport(respond))
        tracks=client.get('/api/session').json()['tracks'];assert len(tracks)==3
        for track in tracks:assert client.post('/api/playback/queue',json={'track_id':track['id']}).status_code==200
        for index,track in enumerate(tracks):
         response=client.post('/api/playback/start' if index==0 else '/api/playback/advance',json={});assert response.status_code==200
         snap=client.get('/api/session').json();jobs=snap['jobs'];job=jobs[-1];assert job['track_id']==track['id']
         if mode!='success':
          assert job['state']=='failed' and job['error'] is not None
          value=json.loads(state.read_text());assert value['stop']['stage']==('text' if mode=='text_failure' else 'speech');assert value['stop']['error']==job['error']
          assert len(jobs)==1 and wire==([9001] if mode=='text_failure' else [9001,9008]);assert 'PRIVATE-SYNTHETIC-MARKER' not in state.read_text()
          client.post('/api/playback/advance',json={})
          guarded=json.loads(state.read_text());assert guarded['attempts']==value['attempts'] and guarded['prevented_requests']==1
          break
         assert job['state']=='succeeded' and len(jobs)==index+1
        if mode=='success':
         before=json.loads(state.read_text())['attempts'];assert before=={'text':3,'speech':3,'art':0,'music':0}
         client.post('/api/playback/start',json={})
         assert json.loads(state.read_text())['attempts']==before
        value=json.loads(state.read_text());results.append({'mode':mode,'result':'PASS','attempts':value['attempts'],'captured_failure':value['stop'],'prevented_requests':value['prevented_requests']})
    if args.output:
     Path(args.output).write_text(json.dumps({'real_class_calls':0,'results':results},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'real_class_calls':0,'results':results},indent=2))

if __name__=="__main__":
    main()
