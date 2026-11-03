const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[2], 'utf8');
const handler = source.slice(source.indexOf('function djSpeakerLabel()'), source.indexOf('function selectDjVoice()'));
function setup(fail = false) {
  const elements = {'#dj-speaker': {value: 'female', disabled: false}, '#dj-speaker-status': {textContent: ''}};
  const calls = [];
  let release, clears = 0;
  const gate = new Promise(resolve => release = resolve);
  const clip = {syntheticOnly: true};
  const context = vm.createContext({djVoiceSaving: false, djVoiceFile: clip, latestSession: {dj_voice: 'alternate'},
    document: {querySelector: id => elements[id]}, djUserQueue: callback => callback(), syncAfterMutation: async () => {},
    clearDjVoice: () => {clears++; context.djVoiceFile = null;},
    renderDj: session => {elements['#dj-speaker'].value = session.dj_voice;},
    request: async (path, data, withVoice) => {
      calls.push({path, data, withVoice}); await gate;
      if (fail) throw new Error('Voice could not be saved');
      return {dj_voice: data.voice};
    }
  });
  vm.runInContext(handler, context);
  return {context, elements, calls, release, clip, clears: () => clears};
}
(async () => {
  const good = setup(), pending = good.context.changeDjSpeaker();
  assert.equal(good.elements['#dj-speaker'].disabled, true);
  await good.context.changeDjSpeaker(); assert.equal(good.calls.length, 1);
  assert.equal(good.calls[0].path, '/api/playback/voice');
  assert.equal(good.calls[0].data.voice, 'female'); assert.equal(good.calls[0].withVoice, false);
  good.release(); await pending;
  assert.equal(good.context.latestSession.dj_voice, 'female');
  assert.equal(good.elements['#dj-speaker'].disabled, false);
  assert.equal(good.clears(), 1); assert.equal(good.context.djVoiceFile, null);
  assert.equal(good.context.djSpeakerLabel(), 'Female DJ voice');
  assert.match(good.elements['#dj-speaker-status'].textContent, /new introductions/);
  const bad = setup(true), failed = bad.context.changeDjSpeaker(); bad.release(); await failed;
  assert.equal(bad.context.latestSession.dj_voice, 'alternate');
  assert.equal(bad.elements['#dj-speaker'].value, 'alternate'); assert.equal(bad.elements['#dj-speaker'].disabled, false);
  assert.equal(bad.context.djVoiceFile, bad.clip); assert.equal(bad.clears(), 0);
  assert.match(bad.elements['#dj-speaker-status'].textContent, /could not be saved/);
  const newer = setup(), choosing = newer.context.changeDjSpeaker();
  const newClip = {chosenWhileSaving:true}; newer.context.djVoiceFile = newClip;
  newer.release(); await choosing;
  assert.equal(newer.context.djVoiceFile, newClip); assert.equal(newer.clears(), 0);
  console.log('PASS: speaker preference saves once, clears reference only on success, rolls back and never generates');
})().catch(error => {console.error(error); process.exitCode = 1;});
