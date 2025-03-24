!function () { var e, t, n; e = "16863fd582763a2", t = function () { Reo.init({ clientID: "16863fd582763a2" }) }, (n = document.createElement("script")).src = "https://static.reo.dev/" + e + "/reo.js", n.async = !0, n.onload = t, document.head.appendChild(n) }();

function random() {
  setTimeout('', 1000);
  document.getElementById("myNumber").innerHTML = Math.floor(Math.random() * 10000000);
  window.localStorage.removeItem("/.__announce");
}
window.addEventListener("load",random);
// window.onload = random;

function updateOS() {
  var ele = document.getElementsByName('osFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("OS_State", ele[i].id);
      openOS(ele[i].id);
      updatePage();
    }
  }
}

function updateCas() {
  window.localStorage.setItem("App_State", "Cas");
  var ele = document.getElementsByName('casFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("VER_State", ele[i].id);
      updatePage();
    }
  }
  updatePage();
}

function updateKafka() {
  window.localStorage.setItem("App_State", "Kafka");
  var ele = document.getElementsByName('kafFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("VER_State", ele[i].id);
      updatePage();
    }
  }
  updatePage();
}


function updateJava() {
  var ele = document.getElementsByName('javaFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("JAVA_State", ele[i].id);
      updatePage();
    }
  }
}

function updateAppVersion() {
  
  appVersion = document.getElementById('AppVersion').value
  if (window.localStorage.getItem("App_State") != null && window.localStorage.getItem("App_State") == "Cas"){
    window.localStorage.setItem("VER_State", "Cassandra" + appVersion) 
    console.info("Setting VER_State -> " + "Cassandra" + appVersion)
  }
  if (window.localStorage.getItem("App_State") != null && window.localStorage.getItem("App_State") == "Kafka"){
    window.localStorage.setItem("VER_State", "Kafka" + appVersion) 
    console.info("Setting VER_State -> " + "Kafka" + appVersion)
  }  
  updatePage()
}


function openOS(os) {
  var i;
  var x = document.getElementsByClassName("os");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  os += 'Div';
  for (i = 0; i < x.length; i++) {
    if(x[i].id == os)
      x[i].style.display = "block"
    // document.getElementById(os)[i].style.display = "block";
  }
}

function openCAS() {
  var i;
  if(document.getElementsByClassName("cas").length == 0)
    return;
  var x = document.getElementsByClassName("cas");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  let cas = "";

  switch(window.localStorage.getItem("App_State")){
    case "Cas":
      cas += window.localStorage.getItem("OS_State");
      cas += "Cassandra"
      cas += window.localStorage.getItem("JAVA_State");
      cas += 'Div';
    case "Kafka":
      cas += window.localStorage.getItem("OS_State");
      cas += window.localStorage.getItem("VER_State");
      cas += window.localStorage.getItem("JAVA_State");
      cas += 'Div';
  }
  console.log("Trying to get cas ->" + cas)
  document.getElementById(cas).style.display = "block";
}

function openJAVACAS() {
  var i;
  if(document.getElementsByClassName("javaFamily").length == 0)
    return;
  var jx = document.getElementsByClassName("javaFamily");
  for (i = 0; i < jx.length; i++) {
    jx[i].style.display = "none";
  }
  let javacas = "";
  if (window.localStorage.getItem("OS_State") == null){
    if (document.getElementsByName('casFamily').length > 0)
      window.localStorage.setItem("JAVA_State", "Java11")
    if (document.getElementsByName('KafkaFamily').length > 0)
      window.localStorage.setItem("JAVA_State", "Java11")    
  }

  // javacas += window.localStorage.getItem("CAS_State");
  javacas += window.localStorage.getItem("JAVA_State");
  // javacas += 'Div';
  console.log("javacas -> " + javacas)
  document.getElementById(javacas).checked = True
  // document.getElementById(javacas).style.display = "block";
}

function updatePage() {

  if (document.getElementsByName('osFamily')[0] != null && window.localStorage.getItem("OS_State") == null)
    window.localStorage.setItem("OS_State", "Debian");
  if (document.getElementsByName('casFamily')[0] != null && window.localStorage.getItem("VER_State") == null)
    window.localStorage.setItem("VER_State", "Cassandra30");
  if (document.getElementsByName('kafFamily').length > 0 && window.localStorage.getItem("VER_State") == null)
    window.localStorage.setItem("VER_State", "Kafka3");  
  if (document.getElementsByName('javaFamily')[0] != null && window.localStorage.getItem("JAVA_State") == null)
    window.localStorage.setItem("JAVA_State", "Java8");  

    
  if (document.getElementById('App_State') != null && window.localStorage.getItem("App_State") == null)
    document.getElementById('Cassandra').checked = True

  console.info("App State " + window.localStorage.getItem("App_State"))
  console.info("Ver State " + window.localStorage.getItem("VER_State"))
  console.info("Os State " + window.localStorage.getItem("OS_State"))
  console.info("Java State " + window.localStorage.getItem("JAVA_State"))

  hidePanels();
}

function hidePanels() {
  if(window.localStorage.getItem("App_State") != null && window.localStorage.getItem("App_State") == "Cas"){
    if(window.localStorage.getItem("VER_State") != null){
      switch(window.localStorage.getItem("VER_State")){
        case "Cassandra30":
          document.getElementById('Java8img').style.display = 'inline';  
          document.getElementById('Java11img').style.display = 'none';
          document.getElementById('Java17img').style.display = 'none';
          window.localStorage.setItem("JAVA_State", "Java8");
          document.getElementsByName('javaFamily')[0].checked = true
          openCAS();
          openJAVACAS();
          break;
        case "Cassandra311":
          document.getElementById('Java8img').style.display = 'inline';
          document.getElementById('Java11img').style.display = 'none';
          document.getElementById('Java17img').style.display = 'none';
          window.localStorage.setItem("JAVA_State", "Java8");
          document.getElementsByName('javaFamily')[0].checked = true
          openCAS();
          openJAVACAS();
          break;
        case "Cassandra40":
          document.getElementById('Java8img').style.display = 'inline';
          document.getElementById('Java11img').style.display = 'inline';
          document.getElementById('Java17img').style.display = 'inline';
          if(window.localStorage.getItem("JAVA_State") == "Java8")
            document.getElementsByName('javaFamily')[0].checked = true;
          else
            document.getElementsByName('javaFamily')[1].checked = true;
          openCAS();
          openJAVACAS();
          break;
        case "Cassandra41":
          document.getElementById('Java8img').style.display = 'inline';
          document.getElementById('Java11img').style.display = 'inline';
          document.getElementById('Java17img').style.display = 'inline';
          document.getElementsByName('javaFamily')[0].checked = true;
          if(window.localStorage.getItem("JAVA_State") == "Java8")
            document.getElementsByName('javaFamily')[0].checked = true;
          else
            document.getElementsByName('javaFamily')[1].checked = true;
          openCAS();
          openJAVACAS();
          break;
        case "Cassandra50":
          document.getElementById('Java8img').style.display = 'none';
          document.getElementById('Java11img').style.display = 'inline';
          document.getElementById('Java17img').style.display = 'inline';
          // window.localStorage.setItem("JAVA_State", "Java11")
          // document.getElementsByName('javaFamily')[1].checked = true;
          openCAS();
          openJAVACAS();
          break;
      }
    }
  }
  if(document.getElementsByName('kafFamily').length > 0){
    document.getElementById('Java8img').style.display = 'inline';
    document.getElementById('Java11img').style.display = 'inline';
    document.getElementById('Java17img').style.display = 'inline';
    if (window.localStorage.getItem("VER_State") == null)
      document.getElementsByName('kafFamily')[1].checked = true;

    
    // window.localStorage.setItem("JAVA_State", "Java17")
    // document.getElementsByName('javaFamily')[1].checked = true;
    openCAS();
    openJAVACAS();
  }
}

function resetLocalStorage(){
  if(window.localStorage.getItem("OS_State") != null)
    window.localStorage.removeItem("OS_State");
  if(window.localStorage.getItem("VER_State") != null)
    window.localStorage.removeItem("VER_State");
  if(window.localStorage.getItem("JAVA_State") != null)
    window.localStorage.removeItem("JAVA_State");
}

window.addEventListener("beforeunload",resetLocalStorage);
// window.onbeforeunload = resetLocalStorage();