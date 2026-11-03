// Execute production chooser/request/FIFO functions with synthetic files; no network.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[2], 'utf8');
const functions = source.slice(source.indexOf('async function request('), source.indexOf('function node('));
const advances = source.slice(source.indexOf('async function djAdvanceOnce('), source.indexOf('async function djEngine('));
function setup() {
  const calls = [], elements = {};
  let number = 0, failUpload = false, failIntent = false, holdUpload;
  const context = vm.createContext({
    djVoiceFile: null, djAdvanceInFlight: null,
    latestSession: {tracks: [{id:'a'}, {id:'b'}], jobs: [],
      playback: {queue:['a','b'], index:0, state:'playing'}},
    document: {querySelector(id) { return elements[id] ||= {files: [], value:'', disabled:false}; }},
    FormData: class { append(...args) { this.file = args; } },
    syncAfterMutation: async () => {},
    fetch: async (path, options = {}) => {
      calls.push({path, ...options});
      if (path === '/api/references/speech') {
        if (holdUpload) await holdUpload;
        return {ok: !failUpload, json: async () => failUpload
          ? {error:{message:'Invalid clip'}} : {id:`ref-${++number}`}};
      }
      if (options.method === 'DELETE') return {ok:false, status:404};
      return {ok: !failIntent, json: async () => failIntent
        ? {error:{message:'Busy'}} : {state:'speaking'}};
    }
  });
  vm.runInContext(functions + advances, context);
  return {context, calls, elements,
    choose(file) {
      context.document.querySelector('#dj-voice').files = [file];
      context.selectDjVoice();
    },
    failUpload(value) { failUpload = value; },
    failIntent(value) { failIntent = value; },
    hold(value) { holdUpload = value; }};
}
const flush = async () => { for (let i=0; i<10; i++) await Promise.resolve(); };
(async () => {
  const passed = [];
  let t = setup();
  await t.context.request('/api/playback/start', {});
  assert.equal(t.calls.length, 1);
  assert.equal(t.calls[0].body, '{}');
  passed.push('default voice preserves existing request');

  const clip = {size:100, name:'private-recording.mp3'};
  t.choose(clip);
  assert.equal(t.calls.length, 1, 'selecting a file never generates or uploads');
  await t.context.request('/api/playback/start', {});
  assert.equal(t.calls[1].body.file[1], clip);
  assert.equal(t.calls[1].body.file[2], 'reference', 'local filename not transmitted');
  assert.equal(JSON.parse(t.calls[2].body).reference_id, 'ref-1');
  assert.equal(t.calls[3].method, 'DELETE');
  await t.context.request('/api/playback/advance', {});
  assert.equal(JSON.parse(t.calls[5].body).reference_id, 'ref-2');
  passed.push('selected MP3/WAV file reused through fresh one-shot uploads');

  t.context.clearDjVoice();
  await t.context.request('/api/playback/speech', {track_id:'a'});
  assert.equal(t.calls.length, 8);
  assert.deepEqual(JSON.parse(t.calls.at(-1).body), {track_id:'a'});
  assert.equal(t.context.djVoiceFile, null);
  passed.push('clear returns future introductions to default');

  t = setup();
  t.choose(clip);
  t.context.latestSession.tracks[0].speech = {url:'/cached'};
  await t.context.request('/api/playback/start', {});
  assert.equal(t.calls.length, 1);
  t.context.latestSession.jobs = [{track_id:'b',kind:'speech',state:'failed'}];
  await t.context.request('/api/playback/advance', {});
  assert.equal(t.calls.length, 2);
  await t.context.request('/api/playback/speech', {track_id:'b'});
  assert.equal(t.calls.length, 5);
  passed.push('cached and failed intros not regenerated; explicit retry uses reference');

  t = setup(); t.choose(clip); t.failUpload(true);
  await assert.rejects(t.context.request('/api/playback/start', {}), /Invalid clip/);
  assert.equal(t.calls.length, 1, 'invalid upload never submits a default-voice intent');
  assert.match(t.context.document.querySelector('#dj-voice-status').textContent, /No other voice was substituted/);
  t.failUpload(false); t.failIntent(true);
  await assert.rejects(t.context.request('/api/playback/start', {}), /Busy/);
  assert.equal(t.calls.at(-1).method, 'DELETE', 'rejected intent discards unused upload');
  t.failIntent(false);
  await t.context.request('/api/playback/start', {});
  passed.push('rejections clean up and recover only on another request');

  t = setup(); t.choose(clip);
  let release;
  t.hold(new Promise(resolve => { release = resolve; }));
  const automatic = t.context.djAdvanceOnce('a', true);
  const skip = t.context.djAdvanceOnce('a', false);
  await flush();
  assert.equal(t.calls.length, 1);
  t.context.clearDjVoice();
  release(); await Promise.all([automatic, skip]);
  assert.equal(t.calls.length, 3);
  assert.equal(JSON.parse(t.calls[1].body).reference_id, 'ref-1');
  await t.context.request('/api/playback/speech', {track_id:'a'});
  assert.equal(t.calls.length, 4, 'clear during upload affects only subsequent requests');
  passed.push('automatic advance and Skip coalesce, even during reference upload');

  t = setup(); t.choose({size:5000001});
  assert.equal(t.context.djVoiceFile, null);
  assert.equal(t.context.document.querySelector('#dj-voice-clear').disabled, true);
  assert.equal(t.calls.length, 0);
  t.choose({size:0});
  assert.equal(t.context.djVoiceFile, null);
  await t.context.request('/api/session');
  assert.equal(t.calls.length, 1, 'poll/reload reads never upload a reference');
  passed.push('invalid local sizes and passive reads do not upload');

  t = setup(); t.choose(clip); t.failUpload(true);
  t.context.latestSession.tracks[0].audio = {url:'/synthetic-song'};
  t.context.latestSession.playback.current_track_id = 'a';
  Object.assign(t.context, {djHalted:false, djEpoch:0, djPhase:'playing',
    djPlayOnce:async () => {}, djInterrupt:() => {},
    djSleep:() => new Promise(() => {}), renderDj:() => {}});
  const engine = source.slice(source.indexOf('async function djEngine('), source.indexOf('\ndjEngine();'));
  const resume = source.slice(source.indexOf('async function djResume('), source.indexOf('async function djSkip('));
  vm.runInContext(engine + resume + ';djEngine();', t.context);
  await flush(); await flush();
  assert.equal(t.context.djHalted, true, 'failed natural advance waits for user recovery');
  assert.equal(t.calls.length, 1, 'halted engine does not re-upload or request default speech');
  t.context.clearDjVoice();
  await t.context.djResume();
  assert.equal(t.context.djHalted, false);
  assert.equal(t.calls.length, 1, 'local recovery does not send invalid server resume for an unpaused queue');
  passed.push('failed natural advance halts once; clear and Resume release local halt');
  console.log(JSON.stringify({scope:'Synthetic production-function checks, not live voice acceptance', passed}, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; });
