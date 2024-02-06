import sys
import json
from typing_extensions import Self, cast
from http.server import HTTPServer, BaseHTTPRequestHandler
from genisys.server.inventory import Inventory

def generate_response(status_code: int, body: str) -> bytes:
    statuses = {200: "OK", 400: "Bad Request", 500: "Internal Server Error"}
    response = f"HTTP/1.1 {status_code} {statuses[status_code]}\n"
    response += f"Content-Length: {len(body)}\n"
    response += "Content-Type: application/json\n"
    response += "\n"
    response += body
    return bytes(response, encoding='utf-8')

class GenisysHTTPServer(HTTPServer):
    """Subclass to manage shared state between server requests"""
    inventory: Inventory

class GenisysHTTPRequestHandler(BaseHTTPRequestHandler):
    """Process client "hello"s by running ansible playbooks on a received POST"""
    def do_POST(self: Self):
        """On POST, store the client in the Ansible inventory and run playbooks"""
        try:
            # cast server since we know it will only be called from Genisys
            server = cast(GenisysHTTPServer, self.server)

            # get the request body
            content_length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(content_length))

            # add the host to the inventory file
            server.inventory.add_host(body['ip'])

            # send success back to the client
            self.wfile.write(generate_response(200, '{"message": "success"}'))
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            self.wfile.write(
                generate_response(
                    500,
                    '{"message": "Internal server error. Check logs for details."}'
                )
            )

