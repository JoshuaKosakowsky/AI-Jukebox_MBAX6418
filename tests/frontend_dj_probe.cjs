// Actual playback functions with synthetic media and deterministic timers; no browser/network.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[2], 'utf8');
const playSource = source.slice(source.indexOf('function djPlayOnce('), source.indexOf('async function djAdvanceOnce('));
const guardStart = source.indexOf('document.addEventListener("play"');
const guardSource = guardStart < 0 ? '' : source.slice(guardStart, source.indexOf('async function djStart(', guardStart));
const flush = async () => { for (let i = 0; i < 6; i++) await Promise.resolve(); };

function setup(error) {
  let plays = 0;
  const timers = [], listeners = {}, status = {}, notice = {};
  const manual = {tagName: 'AUDIO', paused: false, pause() { this.paused = true; }};
  const audio = {
    tagName: 'AUDIO', paused: true, src: '',
    addEventListener(name, callback) { listeners[name] = callback; },
    getAttribute() { return this.src; },
    pause() { this.paused = true; },
    play() {
      plays++;
      if (error) return Promise.reject({name: error});
      this.paused = false;
      return Promise.resolve();
    }
  };
  const document = {
    querySelectorAll() { return [audio, manual]; },
    querySelector() { return status; },
    addEventListener(_, callback) { document.guard = callback; }
  };
  const context = vm.createContext({djEpoch: 0, djAudio: audio, djActive: true, document,
    notice, setTimeout: callback => timers.push(callback)});
  vm.runInContext(playSource + ';globalThis.run = djPlayOnce;', context);
  return {context, manual, audio, timers, listeners, status, document, plays: () => plays};
}

(async () => {
  const results = [];
  let test = setup('AbortError'), done = false;
  test.context.run(0, '/clip').then(() => { done = true; });
  await flush();
  assert.equal(test.timers.length, 1);
  test.context.djEpoch++;
  test.audio.pause();
  test.listeners['dj-interrupt']();
  test.timers.shift()();
  await flush();
  assert.equal(test.plays(), 1, 'stale timer must not start paused audio');
  assert.equal(test.audio.paused, true);
  assert.equal(done, true);
  results.push('stale retry after pause ignored');

  test = setup('NotAllowedError');
  done = false;
  test.context.run(0, '/clip').then(() => { done = true; });
  await flush();
  assert.equal(test.plays(), 1);
  assert.equal(test.timers.length, 0);
  assert.equal(done, false, 'unplayed permission-blocked audio must not complete the segment');
  assert.match(test.status.textContent, /blocked/);
  test.context.djEpoch++;
  test.listeners['dj-interrupt']();
  await flush();
  assert.equal(done, true);
  results.push('permission rejection remains pending until user interrupt');

  test = setup();
  test.context.run(0, '/clip');
  await flush();
  assert.equal(test.manual.paused, true);
  assert.equal(test.audio.paused, false);
  results.push('DJ start pauses an already-playing manual player');

  assert.ok(guardSource, 'capture-phase manual-player guard exists');
  vm.runInContext(guardSource, test.context);
  test.manual.paused = false;
  test.document.guard({target: test.manual});
  assert.equal(test.manual.paused, true);
  results.push('manual start blocked during DJ ownership');
  test.context.djActive = false;
  test.manual.paused = false;
  test.document.guard({target: test.manual});
  assert.equal(test.manual.paused, false);
  results.push('manual start available while DJ idle');
  console.log(JSON.stringify({scope: 'Actual-function Node VM checks, not browser/listening acceptance', passed: results}, null, 2));
})().catch(error => { console.error(error.message); process.exitCode = 1; });
