// Lazy-load Mermaid only when diagrams are detected
(function(){var loaded=false;
function hasMermaid(){return document.querySelector('.mermaid')!==null}
function loadMermaid(){if(loaded||!hasMermaid())return;loaded=true;
var s=document.createElement('script');s.src='https://unpkg.com/mermaid@10/dist/mermaid.min.js';s.async=true;
s.onload=function(){mermaid.initialize({startOnLoad:true,theme:'default',securityLevel:'loose',flowchart:{useMaxWidth:true,htmlLabels:true},sequence:{useMaxWidth:true,wrap:true}});mermaid.contentLoaded()};
document.head.appendChild(s)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',loadMermaid);else loadMermaid();
if(typeof document$!=='undefined')document$.subscribe(function(){if(!loaded)loadMermaid();else if(typeof mermaid!=='undefined')mermaid.contentLoaded()})})();
