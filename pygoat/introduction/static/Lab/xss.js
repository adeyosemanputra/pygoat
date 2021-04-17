var coll = document.getElementsByClassName("coll");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
function SendToServer(){

        comment=document.getElementById("comment").value;


        var xhr;
        xhr = new XMLHttpRequest();
        xml="<?xml version='1.0'?>"+"<comm>"+"<text>"+comment+"</text>"+"</comm>";
       var url="http://127.0.0.1:2000/xxe_parse";
       xhr.open("POST", url, true);
       xhr.setRequestHeader("Content-Type", "text/xml");
       xhr.send(xml);

}