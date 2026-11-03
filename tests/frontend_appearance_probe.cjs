// Execute the production preference controller without a browser or network.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[2], 'utf8');
function load({query = '', saved = {}, blocked = false} = {}) {
  const values = new Map(Object.entries(saved));
  const dataset = {}, controls = {}, writes = [];
  let ready;
  const location = {search: query, href: `http://localhost:8000/${query}#library`};
  const context = vm.createContext({URL, URLSearchParams,
    document: {documentElement: {dataset},
      addEventListener(event, fn) { assert.equal(event, 'DOMContentLoaded'); ready = fn; },
      querySelector(id) {
        assert.equal(id, '#theme-choice', 'Must not query layout, draft or media nodes');
        return controls[id] ||= {value: '', addEventListener(event, fn) {
          assert.equal(event, 'change'); this.change = fn;
        }};
      }},
    window: {location, history: {replaceState(_, __, url) {
      if (blocked) throw Error('History blocked');
      location.href = String(url);
    }}},
    localStorage: {
      getItem(key) { if (blocked) throw Error('Storage blocked'); return values.get(key); },
      setItem(key, value) { if (blocked) throw Error('Storage blocked'); writes.push(key); values.set(key, value); }
    },
    fetch() { throw Error('Appearance changes must never request data or generation'); }
  });
  vm.runInContext(source, context);
  return {dataset, controls, values, writes, location, ready: () => ready(),
    change(key, value) { const control = controls[`#${key}-choice`]; control.value = value; control.change(); }};
}
let app = load();
assert.deepEqual(app.dataset, {design:'gallery', theme:'dark'}, 'Submission layout and dark default apply before paint');
app.ready();
for (const theme of ['light', 'dark']) {
  app.change('theme', theme);
  assert.equal(app.dataset.design, 'gallery');
  assert.equal(app.dataset.theme, theme);
  assert.equal(new URL(app.location.href).hash, '#library');
  assert.equal(new URL(app.location.href).searchParams.has('design'), false);
  assert.equal(new URL(app.location.href).searchParams.get('theme'), theme);
}
assert.ok(app.writes.every(key => key === 'jukebox.theme'));
assert.deepEqual(Object.keys(app.controls), ['#theme-choice'], 'No layout chooser remains');
for (const legacy of ['sleeve','console','room','shop','workbench','arbitrary']) {
  app = load({query:`?design=${legacy}&theme=dark`, saved:{'jukebox.design':legacy,'jukebox.theme':'light'}});
  assert.deepEqual(app.dataset, {design:'gallery', theme:'dark'}, 'Old links and stored layouts cannot override Gallery');
  app.ready();
  assert.equal(new URL(app.location.href).searchParams.has('design'), false);
  assert.equal(new URL(app.location.href).hash, '#library');
}
app = load({saved:{'jukebox.theme':'light'}});
assert.deepEqual(app.dataset, {design:'gallery', theme:'light'}, 'Reload restores theme');
app = load({query:'?design=arbitrary&theme=unknown', saved:{'jukebox.design':'invalid','jukebox.theme':'invalid'}});
assert.deepEqual(app.dataset, {design:'gallery', theme:'dark'}, 'Untrusted theme falls back safely');
app.ready(); app.change('theme','invalid'); assert.equal(app.dataset.theme, 'dark');
app = load({blocked:true,query:'?design=workbench'}); app.ready(); app.change('theme','light');
assert.deepEqual(app.dataset, {design:'gallery', theme:'light'}, 'Blocked browser storage/history is nonfatal');
console.log('PASS: Gallery only; theme persistence, URL priority/hash, legacy-layout rejection, invalid/blocked storage safety; no network or draft/media mutations');
