!function () { var e, t, n; e = "16863fd582763a2", t = function () { Reo.init({ clientID: "16863fd582763a2" }) }, (n = document.createElement("script")).src = "https://static.reo.dev/" + e + "/reo.js", n.async = !0, n.onload = t, document.head.appendChild(n) }();

function random() {
  setTimeout('', 1000);
  document.getElementById("myNumber").innerHTML = Math.floor(Math.random() * 10000000);
}
window.onload = random;

const tabSync = () => {
  if (document.getElementsByName('osFamily')[0] != null)
    document.getElementsByName('osFamily')[0].checked = true;
  if (document.getElementsByName('casFamily')[0] != null)
    document.getElementsByName('casFamily')[0].checked = true;
  if (document.getElementsByName('javaFamily')[0] != null)
    document.getElementsByName('javaFamily')[0].checked = true;

  const tabs = document.querySelectorAll(".tabbed-set > input")
  for (const tab of tabs) {
    tab.addEventListener("change", function () {
      const tabInner = document.querySelector(`label[for=${tab.id}]`).innerHTML
      // Check if Debian or RedHat
      if (tab.checked && tabInner.includes("Debian")) {
        document.getElementsByName('osFamily')[0].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }
      if (tab.checked && tabInner.includes("RedHat")) {
        document.getElementsByName('osFamily')[1].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }

      //Check if Java8 or Java11
      if (tab.checked && tabInner.includes("OpenJDK 8")) {
        document.getElementsByName('javaFamily')[0].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }
      if (tab.checked && tabInner.includes("OpenJDK 11")) {
        document.getElementsByName('javaFamily')[1].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }

      // Check Cassandra and Debian
      if (tab.checked && tabInner.includes("Cassandra 3.0") && tabs[0].checked) {
        document.getElementsByName('osFamily')[0].checked = true;
        document.getElementsByName('casFamily')[0].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }
      if (tab.checked && tabInner.includes("Cassandra 3.11") && tabs[0].checked) {
        document.getElementsByName('osFamily')[0].checked = true;
        document.getElementsByName('casFamily')[1].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }
      if (tab.checked && tabInner.includes("Cassandra 4.0") && tabs[0].checked) {
        document.getElementsByName('osFamily')[0].checked = true;
        document.getElementsByName('casFamily')[2].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }
      if (tab.checked && tabInner.includes("Cassandra 4.1") && tabs[0].checked) {
        document.getElementsByName('osFamily')[0].checked = true;
        document.getElementsByName('casFamily')[3].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }

      // Check Cassandra and RedHat
      if (tab.checked && tabInner.includes("Cassandra 3.0") && tabs[1].checked) {
        document.getElementsByName('osFamily')[1].checked = true;
        document.getElementsByName('casFamily')[0].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }
      if (tab.checked && tabInner.includes("Cassandra 3.11") && tabs[1].checked) {
        document.getElementsByName('osFamily')[1].checked = true;
        document.getElementsByName('casFamily')[1].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }
      if (tab.checked && tabInner.includes("Cassandra 4.0") && tabs[1].checked) {
        document.getElementsByName('osFamily')[1].checked = true;
        document.getElementsByName('casFamily')[2].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }
      if (tab.checked && tabInner.includes("Cassandra 4.1") && tabs[1].checked) {
        document.getElementsByName('osFamily')[1].checked = true;
        document.getElementsByName('casFamily')[3].checked = true;
        window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      }
    });
  }
}
window.onload = tabSync;


function updateOS() {
  var ele = document.getElementsByName('osFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked) {
      window.localStorage.setItem("OS_State", ele[i].id);
      window.localStorage.setItem("yScroll", document.documentElement.scrollTop);
      window.localStorage.setItem("pageURL", ele[i].value);
      updatePage();
    }
  }
}

function updateCas() {
  var ele = document.getElementsByName('casFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked)
      window.location.href = ele[i].value;
  }
}

function updateJava() {
  var ele = document.getElementsByName('javaFamily');
  for (i = 0; i < ele.length; i++) {
    if (ele[i].checked)
      window.location.href = ele[i].value;
  }
}

// rbtn.style.display = 'none';
// Get Qeury parameter on page load and sync the image buttons 
// window.localStorage.setItem("OS_State", "Debian");
// window.localStorage.getItem("OS_State");


function updatePage() {
  if (document.getElementsByName('osFamily')[0] != null || document.getElementsByName('casFamily')[0] != null || document.getElementsByName('javaFamily')[0] != null) {
    window.scrollY = window.localStorage.getItem("yScroll");
    window.location.href = window.localStorage.getItem("pageURL");
  }
}

function clearPage() {
  if (window.location.href.includes("#") = false) {
    window.localStorage.removeItem("OS_State");
    window.localStorage.removeItem("yScroll");
    window.localStorage.removeItem("pageURL");
    window.localStorage.removeItem("./__tabs");
    document.getElementsByName('osFamily')[0].checked = true;
  }
}

// window.onload = clearPage;