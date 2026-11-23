// Isolated program-logic checks; no browser automation.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync(__dirname+'/../app.js','utf8');
const routes=JSON.parse(fs.readFileSync(__dirname+'/../data/routes.geojson'));
const nodes={};for(const k of ['terrain','environment','access']){nodes['#'+k+'Weight']={value:40};nodes['#'+k+'Out']={};}for(const k of ['ranking','routeTable'])nodes['#'+k]={};
const context={routes,selectedRoute:'A',colors:['blue','orange','purple'],$:s=>nodes[s],$$:()=>[]};
const body=src.slice(src.indexOf('function rank()'),src.indexOf('function form()'));
vm.createContext(context);vm.runInContext(body,context);
for(const [weights,expected] of [[[100,0,0],'A'],[[0,100,0],'C'],[[0,0,100],'B']]){['terrain','environment','access'].forEach((k,i)=>nodes['#'+k+'Weight'].value=weights[i]);vm.runInContext('rank()',context);assert(nodes['#ranking'].innerHTML.includes('Route '+expected));}
['terrain','environment','access'].forEach(k=>nodes['#'+k+'Weight'].value=0);vm.runInContext('rank()',context);assert(!nodes['#ranking'].innerHTML.includes('NaN'));assert(nodes['#routeTable'].innerHTML.includes('14.61 km'));
console.log('PASS: ranking responds correctly to terrain, environment and access priorities; zero-weight fallback; calculated table output.');
