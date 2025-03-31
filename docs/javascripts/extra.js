!function () { var e, t, n; e = "16863fd582763a2", t = function () { Reo.init({ clientID: "16863fd582763a2" }) }, (n = document.createElement("script")).src = "https://static.reo.dev/" + e + "/reo.js", n.async = !0, n.onload = t, document.head.appendChild(n) }();

function random() {
  setTimeout('', 1000);
  document.getElementById("myNumber").innerHTML = Math.floor(Math.random() * 10000000);
  window.localStorage.removeItem("/.__announce");
}
window.addEventListener("load",random);
// window.onload = random;

// Select Opearting System
function selectOS() {
  var ele = document.getElementsByName('osFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("OS_State", ele[i].id);
      showHideOSPanel(ele[i].id);
      updatePage();
    }
  }
}

function showHideOSPanel(os) {
  var i;
  var x = document.getElementsByClassName("os");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  os += 'Div';
  for (i = 0; i < x.length; i++) {
    if(x[i].id == os)
      x[i].style.display = "block"
  }
}

// Select Cassandra Version
function selectCas() {
  var ele = document.getElementsByName('casFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("CAS_State", ele[i].id);
      updatePage();
    }
  }
}

function showHideCASPanel() {
  var i;
  if(document.getElementsByClassName("cas").length == 0)
    return;
  var x = document.getElementsByClassName("cas");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  let cas = "";
  cas += window.localStorage.getItem("OS_State");
  cas += window.localStorage.getItem("CAS_State");
  cas += window.localStorage.getItem("JAVA_State");
  cas += 'Div';
  document.getElementById(cas).style.display = "block";
}

// Select Java Version
function selectJava() {
  var ele = document.getElementsByName('javaFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("JAVA_State", ele[i].id);
      updatePage();
    }
  }
}

function openJAVACAS() {
  var i;
  if(document.getElementsByClassName("javacas").length == 0)
    return;
  var jx = document.getElementsByClassName("javacas");
  for (i = 0; i < jx.length; i++) {
    jx[i].style.display = "none";
  }
  let javacas = "";
  javacas += window.localStorage.getItem("CAS_State");
  // javacas += window.localStorage.getItem("JAVA_State");
  javacas += 'Div';
  document.getElementById(javacas).style.display = "block";
}

function updatePage() {
  if (document.getElementsByName('osFamily')[0] != null && window.localStorage.getItem("OS_State") == null)
    window.localStorage.setItem("OS_State", "Debian");
  if (document.getElementsByName('casFamily')[0] != null && window.localStorage.getItem("CAS_State") == null)
    window.localStorage.setItem("CAS_State", "Cassandra30");
  if (document.getElementsByName('javaFamily')[0] != null && window.localStorage.getItem("JAVA_State") == null)
    window.localStorage.setItem("JAVA_State", "Java8");
  if (document.getElementsByName('Service')[0] != null && window.localStorage.getItem("Service_State") == null)
    window.localStorage.setItem("Service_State", "Cassandra");
  if (document.getElementsByName('kafkaFamily')[0] != null && window.localStorage.getItem("KAFKA_State") == null)
    window.localStorage.setItem("KAFKA_State", "Kafka20");
  if (document.getElementsByName('kjavaFamily')[0] != null && window.localStorage.getItem("KJAVA_State") == null)
    window.localStorage.setItem("KJAVA_State", "Java");
  hidePanels();
}

function hidePanels() {
  if(window.localStorage.getItem("CAS_State") != null && window.localStorage.getItem("Service_State") == "Cassandra" ){
    switch(window.localStorage.getItem("CAS_State")){
      case "Cassandra30":
        document.getElementById('Java8img').style.display = 'inline';  
        document.getElementById('Java11img').style.display = 'none';
        document.getElementById('Java17img').style.display = 'none';
        window.localStorage.setItem("JAVA_State", "Java8");
        document.getElementsByName('javaFamily')[0].checked = true
        showHideCASPanel();
        openJAVACAS();
        break;
      case "Cassandra311":
        document.getElementById('Java8img').style.display = 'inline';
        document.getElementById('Java11img').style.display = 'none';
        document.getElementById('Java17img').style.display = 'none';
        window.localStorage.setItem("JAVA_State", "Java8");
        document.getElementsByName('javaFamily')[0].checked = true
        showHideCASPanel();
        openJAVACAS();
        break;
      case "Cassandra40":
        document.getElementById('Java8img').style.display = 'inline';
        document.getElementById('Java11img').style.display = 'inline';
        document.getElementById('Java17img').style.display = 'none';
        if(window.localStorage.getItem("JAVA_State") == "Java17")
          window.localStorage.setItem("JAVA_State", "Java11")
        if(window.localStorage.getItem("JAVA_State") == "Java8")
          document.getElementsByName('javaFamily')[0].checked = true;
        else
          document.getElementsByName('javaFamily')[1].checked = true;
        showHideCASPanel();
        openJAVACAS();
        break;
      case "Cassandra41":
        document.getElementById('Java8img').style.display = 'inline';
        document.getElementById('Java11img').style.display = 'inline';
        document.getElementById('Java17img').style.display = 'none';
        // document.getElementsByName('javaFamily')[0].checked = true;
        if(window.localStorage.getItem("JAVA_State") == "Java17")
          window.localStorage.setItem("JAVA_State", "Java11")
        if(window.localStorage.getItem("JAVA_State") == "Java8")
          document.getElementsByName('javaFamily')[0].checked = true;
        else
          document.getElementsByName('javaFamily')[1].checked = true;
        showHideCASPanel();
        openJAVACAS();
        break;
      case "Cassandra50":
        document.getElementById('Java8img').style.display = 'none';
        document.getElementById('Java11img').style.display = 'inline';
        document.getElementById('Java17img').style.display = 'inline';
        if(window.localStorage.getItem("JAVA_State") == "Java8")
          window.localStorage.setItem("JAVA_State", "Java11")
        if(window.localStorage.getItem("JAVA_State") == "Java11")
          document.getElementsByName('javaFamily')[1].checked = true;
        else
          document.getElementsByName('javaFamily')[2].checked = true;
        showHideCASPanel();
        openJAVACAS();
        break;
    }
  }
  if(window.localStorage.getItem("KAFKA_State") != null && window.localStorage.getItem("Service_State") == "Kafka"){
    switch(window.localStorage.getItem("KAFKA_State")){
      case "Kafka20":
        document.getElementById('Javaimg').style.display = 'inline';  
        // document.getElementById('Java11img').style.display = 'none';
        // document.getElementById('Java17img').style.display = 'none';
        window.localStorage.setItem("KJAVA_State", "Java");
        document.getElementsByName('kjavaFamily')[0].checked = true
        showHideKAFKAPanel();
        openJAVAKAFKA();
        break;
      case "Kafka30":
        document.getElementById('Javaimg').style.display = 'inline';  
        // document.getElementById('Java11img').style.display = 'none';
        // document.getElementById('Java17img').style.display = 'none';
        window.localStorage.setItem("KJAVA_State", "Java");
        document.getElementsByName('kjavaFamily')[0].checked = true
        showHideKAFKAPanel();
        openJAVAKAFKA();
        break;
    }
  }
}

function resetLocalStorage(){
  if(window.localStorage.getItem("OS_State") != null)
    window.localStorage.removeItem("OS_State");
  if(window.localStorage.getItem("CAS_State") != null)
    window.localStorage.removeItem("CAS_State");
  if(window.localStorage.getItem("JAVA_State") != null)
    window.localStorage.removeItem("JAVA_State");
  if(window.localStorage.getItem("Service_State") != null)
    window.localStorage.removeItem("Service_State");
  if(window.localStorage.getItem("KAFKA_State") != null)
    window.localStorage.removeItem("KAFKA_State");
  if(window.localStorage.getItem("KJAVA_State") != null)
    window.localStorage.removeItem("KJAVA_State");
}

window.addEventListener("beforeunload",resetLocalStorage);
// window.onbeforeunload = resetLocalStorage();

// Show or Hide Page based on Kafka or Cassandra selected.
function updateService() {
  var ele = document.getElementsByName('Service');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("Service_State", ele[i].id);
      openService(ele[i].id);
      updatePage();
    }
  }
}

function openService(service) {
  var i;
  var x = document.getElementsByName("service_div");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  service += 'Div';
  for (i = 0; i < x.length; i++) {
    if(x[i].id == service)
      x[i].style.display = "block"
    // document.getElementById(os)[i].style.display = "block";
  }
}

// Kafka Page Dynamic Loading
function updateKafka() {
  var ele = document.getElementsByName('kafkaFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("KAFKA_State", ele[i].id);
      updatePage();
    }
  }
}

function updateKJava() {
  var ele = document.getElementsByName('kjavaFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("KJAVA_State", ele[i].id);
      updatePage();
    }
  }
}

function showHideKAFKAPanel() {
  var i;
  if(document.getElementsByClassName("kafka").length == 0)
    return;
  var x = document.getElementsByClassName("kafka");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  let kafka = "";
  kafka += window.localStorage.getItem("OS_State");
  kafka += window.localStorage.getItem("KAFKA_State");
  kafka += window.localStorage.getItem("KJAVA_State");
  kafka += 'Div';
  document.getElementById(kafka).style.display = "block";
}

function openJAVAKAFKA() {
  var i;
  if(document.getElementsByClassName("javakafka").length == 0)
    return;
  var jx = document.getElementsByClassName("javakafka");
  for (i = 0; i < jx.length; i++) {
    jx[i].style.display = "none";
  }
  let kjavacas = "";
  kjavacas += window.localStorage.getItem("KAFKA_State");
  // javacas += window.localStorage.getItem("JAVA_State");
  kjavacas += 'Div';
  document.getElementById(kjavacas).style.display = "block";
}