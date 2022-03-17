var pth = window.location.pathname.split('/');
console.log(pth);
var xhr = new XMLHttpRequest();
xhr.open("GET", "./php/action.php/?auth=true&pth="+pth.pop().split(".")[0],true);
xhr.setRequestHeader("Content-type","application/json; charset=utf-8");
xhr.send();
xhr.onreadystatechange = function(){
    if(xhr.readyState == 4 && xhr.status == 200){
        var rs = JSON.parse(xhr.response);
        if (!rs.auth) {
          if(rs.login) window.location = './index.php';
          else window.location = './home.html';
        }
    }
}
