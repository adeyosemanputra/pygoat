from http.server import HTTPServer, BaseHTTPRequestHandler

class Collect(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(post_data.decode('utf-8'))
        print(self.path)
        print(self.headers)


PORT = 9000
my_server = HTTPServer(("192.168.64.1", PORT), Collect)

# Star the server
my_server.serve_forever()