const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[2],'utf8');
const handler=source.slice(source.indexOf('async function changeDjPresentation()'),source.indexOf('function selectDjVoice()'));
function setup(fail=false){
 const elements={'#dj-presentation':{value:'upbeat',disabled:false},'#dj-presentation-status':{textContent:''}},calls=[];
 let release;
 const gate=new Promise(resolve=>release=resolve);
 const voice={privateSyntheticMarker:true};
 const context=vm.createContext({djPresentationSaving:false,djVoiceFile:voice,latestSession:{dj_presentation:'relaxed'},
  document:{querySelector:id=>elements[id]},djUserQueue:callback=>callback(),syncAfterMutation:async()=>{},
  renderDj:session=>{elements['#dj-presentation'].value=session.dj_presentation;},
  request:async(path,data,withVoice)=>{calls.push({path,data,withVoice});await gate;if(fail)throw new Error('Style could not be saved');return {dj_presentation:data.style};}
 });
 vm.runInContext(handler,context);
 return {context,elements,calls,release,voice};
}
(async()=>{
 const t=setup();const pending=t.context.changeDjPresentation();
 assert.equal(t.elements['#dj-presentation'].disabled,true);
 await t.context.changeDjPresentation();assert.equal(t.calls.length,1,'ignore overlapping selector changes');
 assert.equal(t.calls[0].path,'/api/playback/presentation');assert.equal(t.calls[0].data.style,'upbeat');assert.equal(t.calls[0].withVoice,false);
 t.release();await pending;
 assert.equal(t.elements['#dj-presentation'].disabled,false);assert.equal(t.context.latestSession.dj_presentation,'upbeat');assert.equal(t.context.djVoiceFile,t.voice);
 assert.match(t.elements['#dj-presentation-status'].textContent,/new introductions/);
 const bad=setup(true);const failed=bad.context.changeDjPresentation();bad.release();await failed;
 assert.equal(bad.elements['#dj-presentation'].value,'relaxed');assert.equal(bad.elements['#dj-presentation'].disabled,false);
 assert.equal(bad.context.latestSession.dj_presentation,'relaxed');assert.equal(bad.context.djVoiceFile,bad.voice);assert.equal(bad.calls.length,1);
 assert.match(bad.elements['#dj-presentation-status'].textContent,/could not be saved/);
 console.log('PASS: style handler saves, serializes, rolls back and preserves reference selection without generation');
})().catch(error=>{console.error(error);process.exitCode=1;});
