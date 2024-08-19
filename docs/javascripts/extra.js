!function(){var e,t,n;e="16863fd582763a2",t=function(){Reo.init({clientID:"16863fd582763a2"})},(n=document.createElement("script")).src="https://static.reo.dev/"+e+"/reo.js",n.async=!0,n.onload=t,document.head.appendChild(n)}();

function random(){
  setTimeout('', 1000);
  document.getElementById("myNumber").innerHTML = Math.floor(Math.random() * 10000000);
  }

  
window.onload = random;

const tabSync = () => {
  document.getElementsByName('osFamily')[0].checked = true;
  document.getElementsByName('casFamily')[0].checked = true;
  const tabs = document.querySelectorAll(".tabbed-set > input")

  // var atabs = Array.prototype.slice.call(tabs,0);
  
  // atabs.forEach(function(tabs) {
  //   var ihtml = document.querySelector(`label[for=${tabs.id}]`).innerHTML
  //   document.getElementsByName(tabs.name)[0].checked = false;
  //   // if(!ihtml.includes("Debian")){
  //   //   console.log("Contains Debian");
  //   //   console.log(tabs.name);
  //   //   console.log(document.getElementsByName(tabs.name)[0]);
  //   //   document.getElementsByName(tabs.name)[0].checked = false;
  //   // }
  //   if(ihtml.includes("Debian")){
  //     console.log("Contains Debian");
  //     console.log(tabs.name);
  //     console.log(document.getElementsByName(tabs.name)[0]);
  //     document.getElementsByName(tabs.name)[0].checked = true;
  //   }
  //   // console.log(tabs.checked);
  //   // console.log(ihtml);
  // });

  for (const tab of tabs) {
    tab.addEventListener("change", function() {
      const tabInner = document.querySelector(`label[for=${tab.id}]`).innerHTML
      // Check if Debian or RedHat
      if(tab.checked && tabInner.includes("Debian"))
        document.getElementsByName('osFamily')[0].checked = true;
      if(tab.checked && tabInner.includes("RedHat"))
        document.getElementsByName('osFamily')[1].checked = true;
      
      // Check Cassandra and Debian
      if(tab.checked && tabInner.includes("Cassandra 3.0") && tabs[0].checked){
        document.getElementsByName('osFamily')[0].checked = true;
        document.getElementsByName('casFamily')[0].checked = true;
      }
      if(tab.checked && tabInner.includes("Cassandra 3.11") && tabs[0].checked){
        document.getElementsByName('osFamily')[0].checked = true;
        document.getElementsByName('casFamily')[1].checked = true;
      }
      if(tab.checked && tabInner.includes("Cassandra 4.0") && tabs[0].checked){
        document.getElementsByName('osFamily')[0].checked = true;
        document.getElementsByName('casFamily')[2].checked = true;
      }
      if(tab.checked && tabInner.includes("Cassandra 4.1") && tabs[0].checked){
        document.getElementsByName('osFamily')[0].checked = true;
        document.getElementsByName('casFamily')[3].checked = true;
      }

      // Check Cassandra and RedHat
      if(tab.checked && tabInner.includes("Cassandra 3.0") && tabs[1].checked){
        document.getElementsByName('osFamily')[1].checked = true;
        document.getElementsByName('casFamily')[0].checked = true;
      }
      if(tab.checked && tabInner.includes("Cassandra 3.11") && tabs[1].checked){
        document.getElementsByName('osFamily')[1].checked = true;
        document.getElementsByName('casFamily')[1].checked = true;
      }
      if(tab.checked && tabInner.includes("Cassandra 4.0") && tabs[1].checked){
        document.getElementsByName('osFamily')[1].checked = true;
        document.getElementsByName('casFamily')[2].checked = true;
      }
      if(tab.checked && tabInner.includes("Cassandra 4.1") && tabs[1].checked){
        document.getElementsByName('osFamily')[1].checked = true;
        document.getElementsByName('casFamily')[3].checked = true;
      }
    });
  }
}
window.onload = tabSync;


function updateOS() {
  var ele = document.getElementsByName('osFamily');
  for(i = 0; i < ele.length; i++) {
      if(ele[i].checked)
      // document.getElementById("result").innerHTML = "Choosen: "+ele[i].value;
      window.location.href = ele[i].value;
  }
}

function updateCas() {
  var ele = document.getElementsByName('casFamily');
  for(i = 0; i < ele.length; i++) {
      if(ele[i].checked)
      window.location.href = ele[i].value;
  }
}