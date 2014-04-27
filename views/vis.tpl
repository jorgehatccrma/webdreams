<html>
<head>
    <title>Web Dreams</title>

    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/pure-min.css">

    <script src="/static/js/socketio/socket.io.js"></script>
    <script src="/static/js/screenfull.min.js"></script>

</head>
<body>

    <h1>Web Dreams ... </h1>
    <h2>Welcome {{username}}</h2>


    <script type="text/javascript">

    function toggleFullscreen() {
        if (screenfull.enabled) {
            screenfull.toggle();
        }
    }



    </script>

</body>
</html>