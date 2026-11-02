"""Opt-in default-DJ audit launcher. Starts normally; browser actions generate intros."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',type=Path,required=True,help='New JSON path OUTSIDE the checkout; do not reuse a spent run')
    parser.add_argument('--env-file',type=Path,help='Optional existing private class configuration; values are never printed')
    parser.add_argument('--port',type=int,default=8028)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    state=args.state.resolve()
    if state.is_relative_to(root.resolve()):parser.error('Keep diagnostic state/audio outside the checkout')
    if not state.parent.is_dir():parser.error('Create the private state directory first')
    if state.exists():parser.error('Existing run state: inspect it; do not reset/repeat generation')
    if not 1024<=args.port<=65535:parser.error('Use a loopback development port1024-65535')
    from dotenv import dotenv_values
    from dj_default_observer import initial
    config=args.env_file or root/'.env'
    values=dict(dotenv_values(config,interpolate=False)) if config.is_file() else {}
    values.update(os.environ)
    env={k:v for k,v in os.environ.items() if not k.startswith('JUKEBOX_')}
    for role in ('TEXT','SPEECH'):
        for suffix in ('ENDPOINT','API_KEY'):
            key=f'JUKEBOX_{role}_{suffix}'
            if not values.get(key):parser.error('Missing '+key)
            env[key]=values[key]
    # Explicit empty overrides also mask music/art values in a checkout .env.
    for role in ('ART','MUSIC'):
        for suffix in ('ENDPOINT','API_KEY'):
            env[f'JUKEBOX_{role}_{suffix}']=''
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    initial(state,source)
    with tempfile.TemporaryDirectory(prefix='jukebox-default-dj-guard-') as folder:
        guard=Path(folder).resolve()
        assert guard.is_relative_to(Path(tempfile.gettempdir()).resolve())
        (guard/'sitecustomize.py').write_text("import os\nfrom dj_default_observer import install\n_guard=install(os.environ['DJ_DEFAULT_STATE'])\n",encoding='utf-8')
        env.update(DJ_DEFAULT_STATE=str(state),PYTHONPATH=os.pathsep.join([str(guard),str(root/'scripts'),str(root)]),PYTHONDONTWRITEBYTECODE='1')
        print('Normal launcher; default-only cap text3/speech3, art0/music0. Stop on first failure; no retries.',flush=True)
        try:return subprocess.run([sys.executable,'scripts/dev.py','--port',str(args.port)],cwd=root,env=env).returncode
        except KeyboardInterrupt:return 130


if __name__=='__main__':
    raise SystemExit(main())
