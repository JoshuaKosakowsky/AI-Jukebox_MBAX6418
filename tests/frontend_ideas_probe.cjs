// Execute the actual idea button/Enter handlers, with no network or submission.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[2], 'utf8');
function setup(random) {
  const fields = Object.fromEntries(['title','style','mood','duration'].map(name => [name, {value:name === 'duration' ? '47' : ''}]));
  const events = {}, changed = [];
  const vocal = {checked:false, dispatchEvent(event) { changed.push(event.type); }};
  const seed = {value:'', addEventListener(type, fn) { events[type] = fn; }};
  const keep = {checked:false}, status = {textContent:''};
  const form = {elements:{namedItem:name => fields[name]},
    querySelector(selector) { assert.equal(selector, 'input[name="mode"][value="vocal"]'); return vocal; },
    addEventListener(type, fn) { assert.equal(type,'reset'); events.reset = fn; },
    submit() { throw Error('Unexpected form submission'); },
    requestSubmit() { throw Error('Unexpected form submission'); }};
  const button = {addEventListener(type, fn) { assert.equal(type,'click'); events.click = fn; }};
  const nodes = {'#cover-form':form,'#idea-seed':seed,'#idea-keep':keep,'#idea-status':status,'#surprise-song':button};
  let state = 721348;
  const seededMath = Object.create(Math);
  seededMath.random = random || (() => {state = (Math.imul(state,1664525)+1013904223)>>>0; return state/4294967296;});
  vm.runInNewContext(source, {Math:seededMath,
    document:{querySelector(selector) { assert.ok(selector in nodes); return nodes[selector]; }},
    Event:class {constructor(type) {this.type=type;}},
    fetch() {throw Error('No network allowed');},
    localStorage:{setItem() {throw Error('Draft inputs must not persist');}}});
  return {fields,seed,keep,status,vocal,changed,events};
}
const app=setup();
assert.equal(app.fields.title.value,'','Loading never replaces user input');
assert.equal(app.vocal.checked,false);
const titles=new Set(), combinations=new Set(), moods=new Set(), styles=new Set();
let previous;
for(let i=0;i<2000;i++) {
  app.events.click();
  const values=Object.fromEntries(Object.entries(app.fields).map(([key,input])=>[key,input.value]));
  for(const key of ['title','style','mood']) assert.ok(values[key].length>0 && values[key].length<=120, `${key} exceeds contract`);
  assert.equal(values.duration,'47');
  assert.equal(app.vocal.checked,true);
  assert.notEqual(values.title,previous,'Avoid immediate repeats'); previous=values.title;
  titles.add(values.title); combinations.add(JSON.stringify(values)); moods.add(values.mood); styles.add(values.style);
}
assert.ok(titles.size>=1900,`Only ${titles.size}/2000 distinct titles`);
assert.equal(combinations.size,2000);
assert.ok(styles.size>=1500 && moods.size===20);
app.seed.value='  moldy    cheese  ';
app.fields.style.value='My own acoustic style'; app.fields.mood.value='My own mood'; app.keep.checked=true;
let prevented=false;
app.events.keydown({key:'Enter',preventDefault(){prevented=true;}});
assert.ok(prevented,'Enter must never submit generation');
assert.ok(app.fields.title.value.toLowerCase().includes('moldy cheese'));
assert.equal(app.fields.style.value,'My own acoustic style'); assert.equal(app.fields.mood.value,'My own mood');
app.fields.style.value='  '; app.events.click(); assert.notEqual(app.fields.style.value.trim(),'');
app.fields.title.value='A fully custom title'; app.fields.style.value='Custom genre';
assert.equal(app.fields.title.value,'A fully custom title','Filled values remain editable');
app.keep.checked=false; app.seed.value='<img src=x onerror=alert(1)>';
app.events.click(); assert.ok(app.fields.title.value.includes(app.seed.value),'Seed is plain input text');
app.seed.value='\u{1f9c0}'.repeat(200);
for(let i=0;i<100;i++) {app.events.click(); assert.ok(app.fields.title.value.length<=120);}
assert.ok(app.changed.every(type=>type==='change'));
assert.match(app.status.textContent,/^Idea: /);
assert.ok(app.status.textContent.includes(app.fields.title.value));
app.events.reset(); assert.equal(app.status.textContent,'');
const fixed=setup(()=>0);
for(let i=0;i<100;i++) {fixed.events.click(); assert.ok(fixed.fields.title.value.length<=120);}
console.log(`PASS: ${titles.size}/2000 unique titles, ${combinations.size} distinct full ideas, ${styles.size} styles, 20 moods; custom seed/keep/edit/Enter/bounds/reset; no network, submission or persistence`);
