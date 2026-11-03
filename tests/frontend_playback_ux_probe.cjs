// Production functions with synthetic media/DOM; no browser or service claims.
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[2], 'utf8');
const seeking = source.slice(source.indexOf('function seekAudio('), source.indexOf('function trackCardInput('));
const dj = source.slice(source.indexOf('function canSeekDj('), source.indexOf('\ndocument.querySelector("#dj-play").addEventListener'));
const element = (tag, text) => ({tag, textContent:text, children:[], events:{},
  append(...items) { this.children.push(...items); }, replaceChildren() { this.children=[]; },
  setAttribute(key,value) { this[key]=value; }, addEventListener(key,fn) { this.events[key]=fn; }});
const elements = {}, calls = [];
const context = vm.createContext({
  djActive:false, djPresentationSaving:false, djHalted:false, notice:{}, node:element,
  djReady:()=>true,
  document:{querySelector:key=>elements[key] ||= element('div'), querySelectorAll:()=>[]},
  djAudio:{currentTime:10,duration:30,paused:true,src:'/b',getAttribute() { return this.src; }},
  latestSession:{tracks:[{id:'a',title:'Alpha',audio:{url:'/a'}},{id:'b',title:'Beta',audio:{url:'/b'}}],
    jobs:[],playback:{state:'idle',queue:['b','a'],index:0,current_track_id:null}},
  request:async (path,body)=>{ assert.equal(path,'/api/playback/queue/remove'); calls.push(body.track_id); },
  syncAfterMutation:async()=>{}
});
vm.runInContext(seeking + dj + ';globalThis.api={seekAudio,seekDj,canSeekDj,renderDj,updateManualSeeking};',context);
const api=context.api, audio=context.djAudio, session=context.latestSession;
const manualButtons=[{disabled:true},{disabled:true}];
context.document.querySelectorAll=()=>[{querySelector:()=>audio,querySelectorAll:()=>manualButtons}];
context.djActive=true;api.updateManualSeeking();
assert.equal(manualButtons[0].disabled,false,'idle snapshot restores manual seeking while DJ engine releases ownership');
context.djActive=false;
assert.equal(api.seekAudio(audio,5),true); assert.equal(audio.currentTime,15);
assert.equal(audio.paused,true, 'seeking must not start a paused player');
api.seekAudio(audio,-100); assert.equal(audio.currentTime,0);
api.seekAudio(audio,100); assert.equal(audio.currentTime,30);
audio.duration=NaN; assert.equal(api.seekAudio(audio,5),false);
audio.duration=30;audio.currentTime=10;
session.playback={state:'speaking',queue:['b','a'],index:0,current_track_id:'b'};
api.seekDj(5);assert.equal(audio.currentTime,10,'speech is not seekable via song controls');
session.playback.state='playing';api.seekDj(5);assert.equal(audio.currentTime,15);
session.playback.state='paused';session.playback.paused_from='playing';
api.seekDj(-5);assert.equal(audio.currentTime,10);assert.equal(audio.paused,true);
audio.src='/speech';api.seekDj(5);assert.equal(audio.currentTime,10,'stale speech source is protected');
session.playback={state:'idle',queue:['b','a'],index:0,current_track_id:null};
api.renderDj(session);
let rows=elements['#dj-queue'].children;
assert.equal(rows[0].textContent,'1. Beta','render queue order, not library order');
assert.equal(rows[1].textContent,'2. Alpha');
(async()=>{
  await rows[0].children[0].events.click();
  assert.deepEqual(calls,['b'],'remove only submits the local queue edit');
  session.playback={state:'playing',queue:['b','a'],index:0,current_track_id:'b'};
  api.renderDj(session);rows=elements['#dj-queue'].children;
  assert.equal(rows[0].children[0].disabled,true,'current entry is protected');
  assert.equal(rows[1].children[0].disabled,false,'upcoming entry can be removed');
  console.log('PASS: seek bounds/pause/speech guards; queue order/removal/current protection; no generation');
})().catch(error=>{console.error(error);process.exitCode=1;});
