<!-- <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
 -->
 <html>
 <head>
    <title>Web Dreams</title>

    <link rel="stylesheet" href="/static/css/pure-min.css">
    <link rel="stylesheet" type="text/css" href="/static/css/style.css">

    <link href='https://fonts.googleapis.com/css?family=Playball' rel='stylesheet' type='text/css'/>
    <link href='https://fonts.googleapis.com/css?family=Roboto+Condensed:400,300,700' rel='stylesheet' type='text/css'/>
    <link href='https://fonts.googleapis.com/css?family=Amaranth' rel='stylesheet' type='text/css'/>

    <script src="/static/js/socketio/socket.io.js"></script>
    <script src="/static/js/screenfull.min.js"></script>
    <script src="/static/js/d3.v3.min.js"></script>


</head>
<body>

    <div id="inner_container" class="pure-g">
    <div class="pure-u-1-1">


    %if not signed_in:

            <h1>Web Dreams</h1>

            <button class="pure-button my_button" onClick="document.location = makeURL('/sign_in')">Sing In on Twitter</button>
            <p class="small_text centered">
                You'll be directed to Twitter.com to sign with your account. Upon authentication, you will be redirected to this site.
            </p>

            <p class="small_text centered">
                This site won't Tweet on your behalf. Your are required to authenticate to access the real-time stream of tweets we will visualize/sonify.
            </p>


    %else:

        <div class="pure-menu pure-menu-open pure-menu-horizontal">

            <div class="bar-left">
                <h1 style="display: inline; font-size: 120%; padding: 5px 5px 10px 20px;">Web Dreams</h1>by
                <h1 style="display: inline; font-size: 100%; padding: 5px 20px 10px 5px;">{{username}}</h1>
                <!-- <button class="pure-button pure-button-disabled">Welcome {{username}}</button> -->
            </div>

            <div class="bar-center">
                Enter search terms:
                <input type="text" id="search_terms"></input>  <img src="/static/assets/help.png" title"Comma separated list of terms to track (only firts 5 will be considered)"></img>
                <button class="pure-button" onClick="startStream()">Start</button>
            </div>

            <div class="bar-right">
                <button class="pure-button" onClick="document.location = makeURL('/sign_out')">Logout</button>
                <button class="pure-button" onClick="toggleFullscreen()">Full Screen</button>
            </div>

        </div>

        <div class="main_canvas"><svg id="svg_canvas"></svg></div>

    %end

    </div> <!-- pure-u-1-1 -->
    </div> <!-- #inner_container -->


    </div>

    <script>

    // Socket.IO stuff
    var socket = io.connect("/tweets");

    socket.on('hello', function (data) {
        console.log(data);
    });

    socket.on('failed_stream', function() {
        alert('Failed to start twitter stream');
    });

    socket.on('new_tweet', function (tweet) {
        // console.log(tweet);
        nodes.push(tweet);
        update();
    });

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

    function startStream() {
        terms = document.getElementById('search_terms').value.split(',');
        // console.log(terms)
        socket.emit('start_stream', terms)
    }

    var width = 800;
    var height = 600;

    var color = d3.scale.category10();

    var nodes = [];
    var links = [];

    var force = d3.layout.force()
                  .nodes(nodes)
                  .links(links)
                  .charge(-120)
                  .friction(0.6)
                  .linkDistance(500)
                  .size([width, height]);


    var svg = d3.select("#svg_canvas");

    function update() {

        var link = svg.selectAll(".link")
                    .data(links);

        link.enter().append("line")
                    .attr("class", "link");
                    // .style("stroke-width", function(d) { return Math.sqrt(d.value); });

        link.exit().remove();

        // nodes.sort(function(a,b) {return a.ip.localeCompare(b.ip);});

        var node = svg.selectAll(".node")
                    .data(nodes);

        create_node = function(nodg) {
            nodg.append("circle")
                .attr("r", 12)
                .style("stroke", function(d,i) { return color(i); });

            nodg.append("text")
                .attr("class", "node_name")
                .attr("x", 16)
                .attr("dy", ".35em")
                .style("fill", function(d,i) { return color(i); })
                .style("stroke-width", 0)
                .style("display", "block")
                .text(function(d) { return "<placeholder>"; });

            node.append("title")
                .text(function(d){ return "<placeholder>"; });
        }

        node.enter().append("g")
                    .attr("class", "node")
                    .call(force.drag)
                    .call(create_node);

        node.select("text")
            .text(function(d) { return "<placeholder>"; })

        node.select("title")
            .text(function(d) { return "<placeholder>"; })

        node.exit().remove();

        force.on("tick", function() {
            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
        });

        force.start();
    }


    </script>





</body>
</html>