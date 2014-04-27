<!-- <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
 -->
 <html>
 <head>
    <title>Web Dreams</title>

    <link rel="stylesheet" href="/static/css/pure-min.css">
    <link rel="stylesheet" type="text/css" href="/static/css/style.css">

    <script src="/static/js/socketio/socket.io.js"></script>
    <script src="/static/js/screenfull.min.js"></script>

    <link href='https://fonts.googleapis.com/css?family=Playball' rel='stylesheet' type='text/css'/>

</head>
<body>

    <div>

    <h1>Web Dreams</h1>

        %if not signed_in:
        <button class="pure-button my_button" onClick="document.location = makeURL('/sign_in')">Sing In on Twitter</button>
        %else:
        <h2>Welcome {{username}}</h2>
        <button class="pure-button my_button" onClick="document.location = makeURL('/sign_out')">Logout</button>
        <button class="pure-button my_button" onClick="toggleFullscreen()">FS</button>
        %end

    </div>


    <script type="text/javascript">

    function makeURL(path) {
        if (!window.location.origin)
            window.location.origin = window.location.protocol+"//"+window.location.host;
        return window.location.origin + path
    }

    function toggleFullscreen() {
        if (screenfull.enabled) {
            screenfull.toggle();
        }
    }

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