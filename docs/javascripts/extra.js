!function () { var e, t, n; e = "16863fd582763a2", t = function () { Reo.init({ clientID: "16863fd582763a2" }) }, (n = document.createElement("script")).src = "https://static.reo.dev/" + e + "/reo.js", n.async = !0, n.onload = t, document.head.appendChild(n) }();

// Process CQL syntax blocks to convert *placeholder* to italics
function processCqlSyntaxBlocks() {
  // Process fenced code blocks
  document.querySelectorAll('.highlight code').forEach(function(block) {
    if (!block.dataset.processed && /\*[a-zA-Z_][a-zA-Z0-9_]*\*/.test(block.textContent)) {
      block.innerHTML = block.innerHTML.replace(/\*([a-zA-Z_][a-zA-Z0-9_]*)\*/g, '<em>$1</em>');
      block.dataset.processed = 'true';
    }
  });
  // Process inline code in tables and paragraphs
  document.querySelectorAll('.md-typeset code:not(.highlight code)').forEach(function(inline) {
    if (!inline.dataset.processed && /\*[a-zA-Z_][a-zA-Z0-9_]*\*/.test(inline.textContent)) {
      inline.innerHTML = inline.innerHTML.replace(/\*([a-zA-Z_][a-zA-Z0-9_]*)\*/g, '<em>$1</em>');
      inline.dataset.processed = 'true';
    }
  });
}

// Run on initial page load
document.addEventListener('DOMContentLoaded', processCqlSyntaxBlocks);

// Run on MkDocs Material instant navigation
if (typeof document$ !== 'undefined') {
  document$.subscribe(processCqlSyntaxBlocks);
} else {
  // Fallback: use MutationObserver for content changes
  var observer = new MutationObserver(function(mutations) {
    processCqlSyntaxBlocks();
  });
  document.addEventListener('DOMContentLoaded', function() {
    var content = document.querySelector('.md-content');
    if (content) {
      observer.observe(content, { childList: true, subtree: true });
    }
  });
}

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
        document.getElementById('KJavaimg').style.display = 'inline';  
        // document.getElementById('Java11img').style.display = 'none';
        // document.getElementById('KJava17img').style.display = 'inline';
        // window.localStorage.setItem("KJAVA_State", "Java");
        if(window.localStorage.getItem("KJAVA_State") == "Java")
          document.getElementsByName('kjavaFamily')[0].checked = true
        else
          document.getElementsByName('kjavaFamily')[1].checked = true
        showHideKAFKAPanel();
        openJAVAKAFKA();
        break;
      case "Kafka30":
        document.getElementById('KJavaimg').style.display = 'inline';  
        // document.getElementById('Java11img').style.display = 'none';
        // document.getElementById('KJava17img').style.display = 'inline';
        // window.localStorage.setItem("KJAVA_State", "Java");
        if(window.localStorage.getItem("KJAVA_State") == "Java")
          document.getElementsByName('kjavaFamily')[0].checked = true
        else
          document.getElementsByName('kjavaFamily')[1].checked = true
        // document.getElementsByName('kjavaFamily')[0].checked = true
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
  if(window.localStorage.getItem("KAFKATYPE_State") != null)
    window.localStorage.removeItem("KAFKATYPE_State");
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
  kjavacas += window.localStorage.getItem("KJAVA_State");
  kjavacas += 'Div';
  document.getElementById(kjavacas).style.display = "block";
  
  if(window.localStorage.getItem("KAFKATYPE_State") != null){
    selectKafkaType(null,window.localStorage.getItem("KAFKATYPE_State"));
  }
  else
    window.localStorage.setItem("KAFKATYPE_State", "Broker");
}

function selectKafkaType(evt,kafkaType) {
  // Store selection in localStorage
  window.localStorage.setItem("KAFKATYPE_State", kafkaType);

  // Array of class names to process
  const classNames = [
    "axon_kafka_dynamic_s1",
    "axon_kafka_dynamic_s2",
    "axon_kafka_dynamic_s3",
    "axon_kafka_dynamic_s4",
    "axon_kafka_dynamic_s5",
    "axon_kafka_dynamic_s6",
    "axon_kafka_dynamic_s7"
  ];

  // Hide/show sections based on kafkaType
  classNames.forEach(className => {
    const elements = document.getElementsByClassName(className);
    for (let i = 0; i < elements.length; i++) {
      elements[i].style.display = (elements[i].id === kafkaType) ? "block" : "none";
    }
  });

  // Handle tab selection highlighting
  const tablinks = document.getElementsByClassName("tabSelected");
  for (let i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" w3-grey", "");
    if (tablinks[i].id === kafkaType) {
      tablinks[i].className += " w3-grey";
    }
  }

  // var i, tablinks;
  // window.localStorage.setItem("KAFKATYPE_State", kafkaType);

  // var u = document.getElementsByClassName("axon_kafka_dynamic_s1");
  // for (i = 0; i < u.length; i++) {
  //   if (u[i].id != kafkaType)
  //     u[i].style.display = "none";
  //   else
  //     u[i].style.display = "block";
  // }

  // var w = document.getElementsByClassName("axon_kafka_dynamic_s2");
  // for (i = 0; i < w.length; i++) {
  //   if (w[i].id != kafkaType)
  //     w[i].style.display = "none";
  //   else
  //     w[i].style.display = "block";
  // }

  // var x = document.getElementsByClassName("axon_kafka_dynamic_s3");
  // for (i = 0; i < x.length; i++) {
  //   if (x[i].id != kafkaType)
  //     x[i].style.display = "none";
  //   else
  //     x[i].style.display = "block";
  // }

  // var y = document.getElementsByClassName("axon_kafka_dynamic_s4");
  // for (i = 0; i < y.length; i++) {
  //   if (y[i].id != kafkaType)
  //     y[i].style.display = "none";
  //   else
  //     y[i].style.display = "block";
  // }

  // var z = document.getElementsByClassName("axon_kafka_dynamic_s5");
  // for (i = 0; i < z.length; i++) {
  //   if (z[i].id != kafkaType)
  //     z[i].style.display = "none";
  //   else
  //     z[i].style.display = "block";
  // }
  
  // tablinks = document.getElementsByClassName("tabSelected");
  // for (i = 0; i < x.length; i++) {
  //   tablinks[i].className = tablinks[i].className.replace(" w3-grey", "");
  //   if(tablinks[i].id == window.localStorage.getItem("KAFKATYPE_State"))
  //   {
  //     tablinks[i].className += " w3-grey";
  //   }
  // }

  // if (evt != null){
  //   evt.currentTarget.className += " w3-grey";
  // }
}