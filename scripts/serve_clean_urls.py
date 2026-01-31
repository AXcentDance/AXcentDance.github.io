
import http.server
import socketserver
import os

PORT = 8000

class CleanUrlHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # If the path ends with a slash, default behavior (index.html) is fine
        if self.path.endswith("/"):
            return super().do_GET()
        
        # Split path query/fragment
        path = self.path.split('?')[0].split('#')[0]
        
        # If the file exists exactly as requested, serve it
        # (e.g. style.css, image.png)
        if os.path.exists(os.path.join(os.getcwd(), path.lstrip('/'))):
             return super().do_GET()

        # If it doesn't exist, try appending .html
        if os.path.exists(os.path.join(os.getcwd(), path.lstrip('/')) + ".html"):
            self.path = path + ".html"
            return super().do_GET()
            
        # Fallback to default (404)
        return super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CleanUrlHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print("Clean URLs enabled: Requesting '/about' will serve 'about.html'")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
