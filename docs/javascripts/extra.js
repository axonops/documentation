function random(){
  setTimeout('', 1000);
  document.getElementById("myNumber").innerHTML = Math.floor(Math.random() * 100000);
  }

  
window.onload = random;