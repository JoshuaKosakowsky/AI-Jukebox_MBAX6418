"""OFFLINE manual browser probes: reserved-slot injection, no .env or external HTTP.
Usage: python audit_retry_variants.py --source PATH --case cover|resume --port 8171
Requires sibling audit_fault_harness.py from PR #22. Not application/CI code.
"""
import argparse
from contextlib import asynccontextmanager
from audit_fault_harness import Wire, app_context, load_source

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--case', choices=['cover','resume'], required=True)
    parser.add_argument('--port', type=int, default=8171)
    args = parser.parse_args()
    load_source(args.source)
    from fastapi.responses import RedirectResponse
    from jukebox.contracts import SongSettings
    import uvicorn
    wire = Wire()
    with app_context(wire) as app:
        store = app.state.sessions
        original = app.router.lifespan_context
        state = {}
        @asynccontextmanager
        async def lifespan(app):
            async with original(app):
                session = store.resolve(None)
                state['session'] = session
                tracks = []
                for title in ('OFFLINE blocker A','OFFLINE blocker B','OFFLINE target'):
                    job = store.create_cover_track(session, title, SongSettings(style='Offline fixture',mood='Audit',duration_seconds=10,mode='instrumental'))
                    store.generate_cover(session,job.id,app.state.providers)
                    tracks.append(job.track_id)
                target = tracks[-1]
                if args.case == 'cover':
                    wire.options = {'cover_fail':True}
                    job = store.queue_cover(session,target)
                    store.generate_cover(session,job.id,app.state.providers)
                    wire.options = {}
                    blockers = [store.queue_cover(session,t) for t in tracks[:2]]
                else:
                    wire.options = {'poll_timeouts':1}
                    job = store.queue_music(session,target)
                    store.generate_music(session,job.id,app.state.providers)
                    wire.options = {}
                    blockers = [store.queue_music(session,t) for t in tracks[:2]]
                state.update(blockers=blockers,target=target,released=False)
                yield
        app.router.lifespan_context = lifespan
        @app.get('/audit/enter')
        def enter():
            response = RedirectResponse('/')
            from jukebox.sessions import SESSION_COOKIE
            response.set_cookie(SESSION_COOKIE,state['session'].token,httponly=True,samesite='strict')
            return response
        @app.get('/audit/state')
        def audit_state():
            s=state['session']
            return {'case':args.case,'released':state['released'],'counts':dict(wire.counts),
                    'jobs':len(s.jobs),'active':len(s.active),'target':str(state['target'])}
        @app.post('/audit/release')
        def release():
            if not state['released']:
                for job in state['blockers']:
                    run = store.generate_cover if args.case == 'cover' else store.generate_music
                    run(state['session'],job.id,app.state.providers)
                state['released']=True
            return audit_state()
        uvicorn.run(app,host='127.0.0.1',port=args.port,access_log=False)

if __name__=='__main__':
    main()
