// Execute the production preference controller without a browser or network.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[2], 'utf8');
function load({query = '', saved = {}, blocked = false} = {}) {
  const values = new Map(Object.entries(saved));
  const dataset = {}, controls = {}, writes = [];
  const studio = {open:false};
  let ready, focusHandler;
  const scrolls = [];
  const location = {search: query, href: `http://localhost:8000/${query}#library`};
  const context = vm.createContext({URL, URLSearchParams,
    document: {documentElement: {dataset},
      addEventListener(event, fn) { assert.equal(event, 'DOMContentLoaded'); ready = fn; },
      querySelector(id) {
        if (id === '.create-panel') return studio;
        if (id === '#tracks') return {addEventListener(event, fn) {
          assert.equal(event, 'focusin'); focusHandler = fn;
        }};
        assert.ok(['#design-choice', '#theme-choice'].includes(id), 'Must never rebuild track/audio nodes');
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
  return {dataset, controls, values, writes, location, studio, scrolls, focusCard: () => focusHandler({target:{closest: () => ({scrollIntoView: args => scrolls.push(args)})}}), ready: () => ready(),
    change(key, value) { const control = controls[`#${key}-choice`]; control.value = value; control.change(); }};
}
let app = load();
assert.deepEqual(app.dataset, {design:'sleeve', theme:'dark'}, 'Dark default applies before DOM ready');
app.ready();
for (const design of ['gallery', 'console', 'sleeve', 'room', 'shop', 'workbench']) {
  app.change('design', design);
  for (const theme of ['light', 'dark']) {
    app.change('theme', theme);
    assert.equal(app.dataset.design, design);
    assert.equal(app.dataset.theme, theme);
    assert.equal(new URL(app.location.href).hash, '#library');
    assert.equal(new URL(app.location.href).searchParams.get('design'), design);
    assert.equal(new URL(app.location.href).searchParams.get('theme'), theme);
  }
}
app.focusCard(); assert.equal(app.scrolls.length, 0, 'No rack scrolling in other layouts');
app.change('design', 'shop'); app.focusCard();
assert.equal(app.scrolls.length, 1, 'Keyboard focus reveals the record');
assert.equal(app.scrolls[0].inline, 'nearest');
assert.equal(app.scrolls[0].behavior, 'instant', 'No motion is required to reveal focus');
app.change('design', 'workbench');
assert.equal(app.studio.open, true, 'Workbench opens the studio without submitting');
app.change('design', 'sleeve');
assert.equal(app.studio.open, false, 'Leaving Workbench restores the previous disclosure');
app.studio.open = true;
app.change('design', 'workbench'); app.change('design', 'gallery');
assert.equal(app.studio.open, true, 'An already-open studio stays open after Workbench');
assert.ok(app.writes.every(key => ['jukebox.design', 'jukebox.theme'].includes(key)));
app = load({saved: {'jukebox.design':'console', 'jukebox.theme':'light'}});
assert.deepEqual(app.dataset, {design:'console', theme:'light'}, 'Reload restores preferences');
app = load({query:'?design=gallery&theme=dark', saved:{'jukebox.design':'console','jukebox.theme':'light'}});
assert.deepEqual(app.dataset, {design:'gallery', theme:'dark'}, 'Share link overrides local preference');
app = load({query:'?design=workbench&theme=light'}); app.ready();
assert.equal(app.studio.open, true, 'Direct Workbench link opens the studio');
app.change('design', 'sleeve'); assert.equal(app.studio.open, false);
app = load({query:'?design=arbitrary&theme=unknown', saved:{'jukebox.design':'invalid','jukebox.theme':'invalid'}});
assert.deepEqual(app.dataset, {design:'sleeve', theme:'dark'}, 'Untrusted choices fall back safely');
app.ready(); app.change('design', 'invalid'); assert.equal(app.dataset.design, 'sleeve');
app = load({blocked:true}); app.ready(); app.change('theme','light'); app.change('design','gallery');
assert.deepEqual(app.dataset, {design:'gallery', theme:'light'}, 'Blocked browser storage/history is nonfatal');
console.log('PASS: twelve layout/theme pairs and Workbench disclosure restoration, early dark default, persistence, URL priority/hash, allowlists, blocked storage/history; rack keyboard visibility, no network or media mutations');
