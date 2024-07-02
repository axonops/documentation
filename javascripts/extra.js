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
