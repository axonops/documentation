function random(){
  setTimeout('', 1000);
  document.getElementById("myNumber").innerHTML = Math.floor(Math.random() * 10000000);
  }

  
window.onload = random;