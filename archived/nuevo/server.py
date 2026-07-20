from RangeHTTPServer import RangeRequestHandler
from http.server import HTTPServer

class CORSRequestHandler(RangeRequestHandler):
    def end_headers(self):
        # Mantenemos CORS e inyectamos soporte para Range Requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

if __name__ == '__main__':
    print("Levantando servidor optimizado para PMTiles en http://localhost:8000 ...")
    server = HTTPServer(('localhost', 8000), CORSRequestHandler)
    server.serve_forever()