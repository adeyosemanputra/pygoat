event4 = function(){
    var code = document.getElementById('a7_input').value
    var myHeaders = new Headers();
    // myHeaders.append("Cookie", "csrftoken=5fVOTXh2HNahtvJFJNRSrKkwPAgPM9YCHlrCGprAxhAAKOUWMxqMnWm8BUomv0Yd; jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNjUzMzEzMDIxLCJpYXQiOjE2NTMzMDk0MjF9.dh2gfP9wKD8GKu1J-jVs2jJUYMgKu_kMaJjrD0hHP-I");

    var formdata = new FormData();
    // formdata.append("csrfmiddlewaretoken", "5fVOTXh2HNahtvJFJNRSrKkwPAgPM9YCHlrCGprAxhAAKOUWMxqMnWm8BUomv0Yd");
    formdata.append("code", code);

    var requestOptions = {
    method: 'POST',
    headers: myHeaders,
    body: formdata,
    redirect: 'follow'
    };

    fetch("/2021/discussion/A7/api", requestOptions)
    .then(response => response.text())
    .then(result => {
        let data = JSON.parse(result);  // parse JSON string into object
        console.log(data);
        document.getElementById("a7_d4").style.display = 'flex';
        document.getElementById("a7_d4").innerText =  "Result: " + data.message;
        
    }
    ).catch(error => console.log('error', error));
}