import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing_extensions import Self, Tuple, cast
from genisys.config_parser import YAMLParser
from genisys.server.genisysinventory import GenisysInventory

def generate_response(status_code: int, message: str) -> bytes:
    """Generates a JSON formated HTTP response with the given status and message"""
    statuses = {200: "OK", 400: "Bad Request", 500: "Internal Server Error"}
    response_body = '{"hostname":"' + message + '"}'
    response = f"HTTP/1.1 {status_code} {statuses[status_code]}\n"
    response += f"Content-Length: {len(response_body)}\n"
    response += "Content-Type: application/json\n"
    response += "\n"
    response += response_body
    return bytes(response, encoding='utf-8')

class GenisysHTTPServer(HTTPServer):
    """Subclass to manage shared state between server requests"""
    def __init__(self: Self, bind: Tuple[str, int], inventory: GenisysInventory, config: YAMLParser):
        super().__init__(bind, GenisysHTTPRequestHandler)
        self.inventory = inventory
        self.config = config

class GenisysHTTPRequestHandler(BaseHTTPRequestHandler):
    """Process client "hello"s by running ansible playbooks on a received POST"""
    def do_POST(self: Self):
        """On POST, store the client in the Genisys Inventory and in return send
        a response with the client's new hostname"""
        try:
            # cast server since we know it will only be called from Genisys
            server = cast(GenisysHTTPServer, self.server)

            # get the request body
            content_length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(content_length))

            # validate the declared IP
            if body['ip'] != self.client_address[0]:
                self.wfile.write(generate_response(400, 'Declared IP is not valid.'))

            # Add the host to the GenisysInventory file
            client_new_hostname = server.inventory.add_host(body)

            # send success back to the client
            self.wfile.write(generate_response(200, client_new_hostname))
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            self.wfile.write(
                generate_response(
                    500,
                    'Internal server error. Check logs for details.'
                )
            )
