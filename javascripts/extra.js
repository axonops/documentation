// Process CQL syntax blocks to convert *placeholder* to italics
function processCqlSyntaxBlocks(){
  document.querySelectorAll('.highlight code').forEach(function(b){
    if(!b.dataset.processed&&/\*[a-zA-Z_]\w*\*/.test(b.textContent)){
      b.innerHTML=b.innerHTML.replace(/\*([a-zA-Z_]\w*)\*/g,'<em>$1</em>');b.dataset.processed='true'}});
  document.querySelectorAll('.md-typeset code:not(.highlight code)').forEach(function(i){
    if(!i.dataset.processed&&/\*[a-zA-Z_]\w*\*/.test(i.textContent)){
      i.innerHTML=i.innerHTML.replace(/\*([a-zA-Z_]\w*)\*/g,'<em>$1</em>');i.dataset.processed='true'}})}
document.addEventListener('DOMContentLoaded',processCqlSyntaxBlocks);
if(typeof document$!=='undefined')document$.subscribe(processCqlSyntaxBlocks);

// OS/Version selection
function selectOS(){var e=document.getElementsByName('osFamily');for(var i=0;i<e.length;i++)if(e[i].checked){localStorage.setItem('OS_State',e[i].id);showHideOSPanel(e[i].id);updatePage()}}
function showHideOSPanel(os){var x=document.getElementsByClassName('os');for(var i=0;i<x.length;i++)x[i].style.display='none';var d=document.getElementById(os+'Div');if(d)d.style.display='block'}
function selectCas(){var e=document.getElementsByName('casFamily');for(var i=0;i<e.length;i++)if(e[i].checked){localStorage.setItem('CAS_State',e[i].id);updatePage()}}
function showHideCASPanel(){if(!document.getElementsByClassName('cas').length)return;var x=document.getElementsByClassName('cas');for(var i=0;i<x.length;i++)x[i].style.display='none';var c=(localStorage.getItem('OS_State')||'')+(localStorage.getItem('CAS_State')||'')+(localStorage.getItem('JAVA_State')||'')+'Div';var el=document.getElementById(c);if(el)el.style.display='block'}
function selectJava(){var e=document.getElementsByName('javaFamily');for(var i=0;i<e.length;i++)if(e[i].checked){localStorage.setItem('JAVA_State',e[i].id);updatePage()}}
function openJAVACAS(){if(!document.getElementsByClassName('javacas').length)return;var x=document.getElementsByClassName('javacas');for(var i=0;i<x.length;i++)x[i].style.display='none';var c=(localStorage.getItem('CAS_State')||'')+'Div';var el=document.getElementById(c);if(el)el.style.display='block'}

function updatePage(){
  var d={osFamily:['OS_State','Debian'],casFamily:['CAS_State','Cassandra30'],javaFamily:['JAVA_State','Java8'],Service:['Service_State','Cassandra'],kafkaFamily:['KAFKA_State','Kafka20'],kjavaFamily:['KJAVA_State','Java17']};
  for(var n in d)if(document.getElementsByName(n)[0]&&!localStorage.getItem(d[n][0]))localStorage.setItem(d[n][0],d[n][1]);
  hidePanels()}

function hidePanels(){
  var c=localStorage.getItem('CAS_State'),s=localStorage.getItem('Service_State'),j=localStorage.getItem('JAVA_State');
  if(c&&s==='Cassandra'){
    var cfg={Cassandra30:{s:['Java8img'],h:['Java11img','Java17img'],j:'Java8'},Cassandra311:{s:['Java8img'],h:['Java11img','Java17img'],j:'Java8'},Cassandra40:{s:['Java8img','Java11img'],h:['Java17img']},Cassandra41:{s:['Java8img','Java11img'],h:['Java17img']},Cassandra50:{s:['Java11img','Java17img'],h:['Java8img']}};
    var cf=cfg[c];if(cf){
      cf.s.forEach(function(id){var e=document.getElementById(id);if(e)e.style.display='inline'});
      cf.h.forEach(function(id){var e=document.getElementById(id);if(e)e.style.display='none'});
      if(cf.j)localStorage.setItem('JAVA_State',cf.j);
      if(c==='Cassandra50'&&j==='Java8')localStorage.setItem('JAVA_State','Java11');
      if((c==='Cassandra40'||c==='Cassandra41')&&j==='Java17')localStorage.setItem('JAVA_State','Java11');
      var jf=document.getElementsByName('javaFamily'),js=localStorage.getItem('JAVA_State');
      if(jf[0])jf[js==='Java8'?0:js==='Java11'?1:2].checked=true;
      showHideCASPanel();openJAVACAS()}}
  var k=localStorage.getItem('KAFKA_State');
  if(k&&s==='Kafka'){var e=document.getElementById('KJavaimg');if(e)e.style.display='inline';
    var kj=document.getElementsByName('kjavaFamily'),ks=localStorage.getItem('KJAVA_State');
    var kjIdx=ks==='Java'?0:1;if(kj[kjIdx])kj[kjIdx].checked=true;
    showHideKAFKAPanel();openJAVAKAFKA()}}

function resetLocalStorage(){['OS_State','CAS_State','JAVA_State','Service_State','KAFKA_State','KJAVA_State','KAFKATYPE_State'].forEach(function(k){localStorage.removeItem(k)})}
window.addEventListener('beforeunload',resetLocalStorage);

function updateService(){var e=document.getElementsByName('Service');for(var i=0;i<e.length;i++)if(e[i].checked){localStorage.setItem('Service_State',e[i].id);openService(e[i].id);updatePage()}}
function openService(s){var x=document.getElementsByName('service_div');for(var i=0;i<x.length;i++){x[i].style.display='none';if(x[i].id===s+'Div')x[i].style.display='block'}}
function updateKafka(){var e=document.getElementsByName('kafkaFamily');for(var i=0;i<e.length;i++)if(e[i].checked){localStorage.setItem('KAFKA_State',e[i].id);updatePage()}}
function updateKJava(){var e=document.getElementsByName('kjavaFamily');for(var i=0;i<e.length;i++)if(e[i].checked){localStorage.setItem('KJAVA_State',e[i].id);updatePage()}}
function showHideKAFKAPanel(){if(!document.getElementsByClassName('kafka').length)return;var x=document.getElementsByClassName('kafka');for(var i=0;i<x.length;i++)x[i].style.display='none';var k=(localStorage.getItem('OS_State')||'Debian')+(localStorage.getItem('KAFKA_State')||'Kafka20')+'Java17Div';var el=document.getElementById(k);if(el)el.style.display='block'}
function openJAVAKAFKA(){if(!document.getElementsByClassName('javakafka').length)return;var x=document.getElementsByClassName('javakafka');for(var i=0;i<x.length;i++)x[i].style.display='none';var ks=localStorage.getItem('KAFKA_State')||'Kafka20';var k1=ks+'JavaDiv';var k2=ks+'Java17Div';var el1=document.getElementById(k1);var el2=document.getElementById(k2);if(el1)el1.style.display='block';if(el2)el2.style.display='block';var kt=localStorage.getItem('KAFKATYPE_State')||'Broker';selectKafkaType(null,kt)}
function selectKafkaType(e,t){localStorage.setItem('KAFKATYPE_State',t);var ks=localStorage.getItem('KAFKA_State')||'Kafka20';var jk1=ks+'JavaDiv';var jk2=ks+'Java17Div';var jkEl1=document.getElementById(jk1);var jkEl2=document.getElementById(jk2);if(jkEl1)jkEl1.style.display='block';if(jkEl2)jkEl2.style.display='block';['axon_kafka_dynamic_s1','axon_kafka_dynamic_s2','axon_kafka_dynamic_s3','axon_kafka_dynamic_s4','axon_kafka_dynamic_s5','axon_kafka_dynamic_s6','axon_kafka_dynamic_s7'].forEach(function(c){var x=document.getElementsByClassName(c);for(var i=0;i<x.length;i++)x[i].style.display=x[i].id===t?'block':'none'});var tb=document.getElementsByClassName('tabSelected');for(var i=0;i<tb.length;i++){tb[i].className=tb[i].className.replace(' w3-grey','');if(tb[i].id===t)tb[i].className+=' w3-grey'}}
