<!-- <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
 -->
 <html>
 <head>
    <title>Web Dreams</title>

    <link rel="stylesheet" type="text/css" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/pure-min.css">

    <script src="/static/js/socketio/socket.io.js"></script>

</head>
<body>

    <div>

    <h1>Web Dreams</h1>

    <button class="pure-button my_button" onClick="document.location = makeURL('/sign_in')">Sing In on Twitter</button>

    </div>


    <script type="text/javascript">

    function makeURL(path) {
        if (!window.location.origin)
            window.location.origin = window.location.protocol+"//"+window.location.host;
        return window.location.origin + path
    }

    // function sendDistanceMeasurement() {
    //     xmlhttp = new XMLHttpRequest();
    //     var url = makeURL("/distance");
    //     xmlhttp.open("POST", url, true);
    //     xmlhttp.setRequestHeader("Content-type", "application/json");
    //     xmlhttp.onreadystatechange = function () { //Call a function when the state changes.
    //         if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
    //             // console.log("Server says: " + xmlhttp.responseText);
    //         }
    //     }
    //     var parameters = JSON.stringify({"pingerIP":document.getElementById('pinger').value,
    //                                      "pongerIP":document.getElementById('ponger').value,
    //                                      "distance":+document.getElementById('distance').value});
    //     xmlhttp.send(parameters);
    // }
    </script>



    <!-- Socket.IO stuff -->
    <script>
    var socket = io.connect("/tweets");

    socket.on('hello', function (data) {
        console.log(data)
    });

    </script>


</body>
</html>