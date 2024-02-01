#!/usr/bin/env python3
import os
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing_extensions import Self

class GenisysHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self: Self):
        print('posted')

if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 4443), GenisysHTTPRequestHandler)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile="./certs/cert.pem",
        keyfile="./certs/key.pem",
        password=open("./certs/passwd", "r", encoding="utf-8").readline().strip('\n')
    )
    httpd.socket = ssl_context.wrap_socket(httpd.socket)
    httpd.serve_forever()
