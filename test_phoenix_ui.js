/* DOM-handler test without browser dependencies. Does not replace visual QA. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const data=JSON.parse(fs.readFileSync(__dirname+'/data/phoenix_reference.json','utf8'));
const elements={};const q=id=>elements[id]??=( {value:'',innerHTML:'',textContent:''} );q('phxLanguage').value='pt';let exported;
const context={document:{getElementById:q,createElement:()=>({click(){}})},fetch:async()=>({ok:true,json:async()=>data}),Blob,URL:{createObjectURL:b=>{exported=b;return 'blob:test';},revokeObjectURL(){}},setTimeout:fn=>fn()};
vm.runInNewContext(fs.readFileSync(__dirname+'/phoenix.js','utf8'),context);
setImmediate(async()=>{
 assert.match(q('phxContent').innerHTML,/Rosy Red/);assert.match(q('phxContent').innerHTML,/not_available/);
 q('phxSample').onchange({target:{value:'Sorceress 2'}});assert.match(q('phxContent').innerHTML,/unreliable_sensor/);assert.match(q('phxContent').innerHTML,/reported_value_upper_uncertainty_unresolved/);
 q('phx_ph').value='8.1';q('phx_ec').value='1500';q('phxForm').oninput();q('phxLanguage').value='en';q('phxLanguage').onchange();assert.match(q('phxContent').innerHTML,/value="8.1"/);
 q('phxForm').onsubmit({preventDefault(){}});let result=JSON.parse(await exported.text());assert.equal(result.hypothesis.values.ph.value,8.1);assert.equal(result.hypothesis.values.na.value,null);assert.equal(result.hypothesis.affects_crop_model,false);
 q('phx_ph').value='15';q('phxForm').onsubmit({preventDefault(){}});assert.match(q('phxStatus').textContent,/Check fields/);
 q('phxReset').onclick();q('phxReset').onclick();assert.doesNotMatch(q('phxContent').innerHTML,/value="8.1"/);
 console.log('PASS: sample switching, missing qualifiers, language draft retention, export separation/nulls, invalid values, repeated reset (mock DOM; visual QA not covered)');
});
