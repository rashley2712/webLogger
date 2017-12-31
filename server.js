'use strict'

var http = require('http')
var url = require('url')
var fs = require('fs')
var path = require('path')

var port = process.argv[2]

if (port == undefined) port = 8080

var server = http.createServer(function (request, response) {
	// request handling logic
	var ip = request.socket.remoteAddress;
  // console.log("Request received from: " + ip)
	// console.log("URL: " + req.url)
	var URLData = url.parse(request.url, true)
	// console.log(URLData)
	var parts = URLData.pathname.split('/')
	console.log("Requesting: " + parts)
	switch(parts[1]) {
		case 'status' :
			writeout(null, "OK")
			break;
		default :
			console.log("Received request for a file: " + request.url)
			var filename = URLData.pathname.substring(1)
			console.log("Getting file: " + filename)
			fileServer(filename, response)
		}

	function fileServer(filename, response) {
		var rootPath = "/home/rashley/webLogger/www/"
		var fullFilename = rootPath + filename
		var contentType = 'text/html'
		var extname = path.extname(filename);
		switch (extname) {
			case '.js':
					contentType = 'text/javascript';
					break;
			case '.css':
					contentType = 'text/css';
					break;
			case '.json':
					contentType = 'application/json';
					break;
			case '.png':
					contentType = 'image/png';
					break;
			case '.gif':
					contentType = 'image/gif';
					break;
			case '.jpg':
					contentType = 'image/jpg';
					break;
				}

			fs.readFile(fullFilename, function(error, content) {
			response.writeHead(200, { 'Content-Type': contentType })
			//if (content!=null) console.log(content.toString())
		  response.end(content, 'utf-8')
		})

	}

	function writeout(err, data) {
		response.writeHead(200, { 'Content-Type': 'application/json',
							  'Access-Control-Allow-Origin': '*' })
		response.write(data)
		response.end()
	}


	}).on('error', function(err) { console.error(err)})

server.listen(port)

server.on('listening', function(socket) {
	console.log("Listening on port: " + port)
	})
