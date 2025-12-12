// Lazy-load MathJax only when math content is detected
(function(){var loaded=false;
function hasMath(){return document.querySelector('.arithmatex')!==null}
function loadMathJax(){if(loaded||!hasMath())return;loaded=true;
window.MathJax={tex:{inlineMath:[["\\(","\\)"]],displayMath:[["\\[","\\]"]],processEscapes:true,processEnvironments:true},options:{ignoreHtmlClass:".*|",processHtmlClass:"arithmatex"}};
var s=document.createElement('script');s.src='https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js';s.async=true;document.head.appendChild(s)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',loadMathJax);else loadMathJax();
if(typeof document$!=='undefined')document$.subscribe(function(){if(!loaded)loadMathJax();else if(typeof MathJax!=='undefined'&&MathJax.typesetPromise){MathJax.startup.output.clearCache();MathJax.typesetClear();MathJax.texReset();MathJax.typesetPromise()}})})();
