
function frame1to2(){
    // frame 1 to 2
    document.getElementById('ssrf-frame-1').style.display = 'none';
    document.getElementById('ssrf-frame-2').style.display = 'flex';
    document.getElementById('ssrf-progress-bar').style.display = 'flex';
}

function frame2to3(){
    var markedCheckbox = document.querySelectorAll('input[type="checkbox"]:checked');
    var arr = [];
    for (var checkbox of markedCheckbox){
        arr.push(parseInt(checkbox.value));
    }
    var score = 0;
    var result = [8,9,10,11,12];
    for (var items of arr){
        if(result.includes(items)){
            score++;
        }
        else{
            score--;
        }
    }
    if( score >= 4 ){
        document.getElementById('ssrf-frame-2').style.display = 'none';
        document.getElementById('ssrf-bar-status1').classList.add('ssrf-bar-status')
        alert('Congratulation! You have figure this out !!');
        document.getElementById('ssrf-frame-3').style.display = 'flex';
    }
}

function frame3to4(){
    var markedCheckbox = document.querySelectorAll('input[name="form2"]:checked');
    var arr = [];
    for (var checkbox of markedCheckbox){
        arr.push(parseInt(checkbox.value));
    }
    var score = 0;
    var result = [3,7,11,15];
    for (var items of arr){
        if(result.includes(items)){
            score++;
        }
        else{
            score--;
        }
    }
    if( score >=4 ){
        document.getElementById('ssrf-frame-3').style.display = 'none';
        document.getElementById('ssrf-bar-status2').classList.add('ssrf-bar-status')
        alert('Congratulation! you have detected defective codes in html');
        document.getElementById('ssrf-frame-4').style.display = 'flex';
    }
}


function checkcode(){
    var python_code = document.getElementById('python').value
    var html_code = document.getElementById('html').value

    var formdata = new FormData();
    formdata.append('python_code', python_code);
    formdata.append('html_code', html_code);
    var requestOptions = {
        method: 'POST',
        body: formdata,
        redirect: 'follow'
      };
      
    fetch("api/ssrf", requestOptions)
    .then(response => response.text())
    .then((result) => {
        console.log(result);
        var obj = JSON.parse(result);
        alert(obj.message);
        if (obj.passed == 1 ){
            document.getElementById('ssrf-frame-4').style.display = 'none';
            document.getElementById('ssrf-bar-status3').classList.add('ssrf-bar-status')
            document.getElementById('ssrf-frame-5').style.display = 'flex';
        }
    })
    .catch(error => console.log('error', error));
}