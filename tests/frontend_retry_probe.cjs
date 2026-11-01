// Behavioral checks of the production click handlers; no DOM package or network.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[2], 'utf8');
const cardSource = source.slice(source.indexOf('function buildTrackCard('), source.indexOf('function renderLibrary('));
const statusSource = source.slice(source.indexOf('function musicStatusText('), source.indexOf('function trackCardInput('));
function element(tag, text) {
  return {tag, textContent: text, children: [], dataset: {}, events: {},
    append(...children) { this.children.push(...children); },
    setAttribute(name, value) { this[name] = value; },
    addEventListener(name, handler) { this.events[name] = handler; }};
}
function descendants(node) { return [node, ...node.children.flatMap(descendants)]; }
async function check(label, endpoint, configured) {
  let rejected = true;
  const requests = [];
  let refreshes = 0;
  const context = vm.createContext({node: element, artConfigured: configured,
    musicConfigured: configured, textConfigured: true, notice: {},
    // DJ availability is outside this focused cover/music/resume probe.
    djReady: () => false,
    request: async path => { requests.push(path); if (rejected) throw new Error('Busy'); return {}; },
    syncAfterMutation: async () => { refreshes++; }});
  vm.runInContext(statusSource + cardSource + ';globalThis.build = buildTrackCard;', context);
  const track = {id:'track-a', title:'A', settings:{mode:'instrumental', style:'Test', mood:'Test'},
    cover:{url:'/cover-a'}, audio:{url:'/audio-a'}};
  const jobs = [{id:'art-job', track_id:track.id, kind:'art', state:'failed', error:{message:'Art failed'}},
    {id:'music-job', track_id:track.id, kind:'music', state:'failed', error:{message:'Timed out',retryable:true}}];
  const card = context.build(track, jobs);
  const nodes = descendants(card);
  const button = nodes.find(n => n.tag === 'button' && n.textContent === label);
  const audio = nodes.find(n => n.tag === 'audio');
  assert.ok(button, label);
  if (!configured) { assert.equal(Boolean(button.disabled), true, label+' configuration guard'); return; }
  assert.equal(Boolean(button.disabled), false);
  const pending = button.events.click();
  assert.equal(button.disabled, true, label+' blocks duplicate click while requesting');
  await pending;
  assert.equal(Boolean(button.disabled), false, label+' recovers after rejected POST with unchanged snapshot');
  assert.deepEqual(requests, [endpoint], label+' no automatic resubmission');
  assert.equal(refreshes, 1);
  assert.equal(descendants(card).find(n => n.tag === 'audio'), audio, 'existing audio retained');
  rejected = false;
  await button.events.click();
  assert.deepEqual(requests, [endpoint, endpoint], label+' explicit retry uses same route/ticket');
  assert.equal(refreshes, 2);
  assert.equal(button.disabled, true, label+' accepted request waits for job snapshot');
}
(async () => {
  for (const [label, route] of [['Retry cover','/api/tracks/track-a/cover'],
    ['Resume check','/api/tracks/track-a/music/resume?from=music-job'],
    ['Generate new instrumental','/api/tracks/track-a/music']]) {
    await check(label, route, true);
    await check(label, route, false);
  }
  console.log('PASS: 3 rejection/retry/audio/duplicate guards and 3 configuration guards');
})().catch(error => { console.error(error); process.exitCode = 1; });
