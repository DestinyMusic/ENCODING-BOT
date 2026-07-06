import os
import sys
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import dns.resolver
from pyrogram import idle

from . import app, log

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = [
    '8.8.8.8']  # this is a google public dns


# --- HUGGING FACE HEALTH CHECK SERVER ---
class QuietHTTPServer(HTTPServer):
    def handle_error(self, request, client_address):
        # Silently ignore ConnectionResetError
        if isinstance(sys.exc_info()[1], ConnectionResetError):
            return
        super().handle_error(request, client_address)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        return # Silence logging

def run_health_check_server():
    # Hugging Face Spaces default port is 7860
    port = int(os.environ.get("PORT", 7860))
    server_address = ('0.0.0.0', port)
    httpd = QuietHTTPServer(server_address, HealthCheckHandler)
    logging.info(f"Starting health check server on port {port}...")
    httpd.serve_forever()
# ----------------------------------------


async def main():
    await app.start()
    await app.send_message(chat_id=log, text=f'<b>Bot Started! @{(await app.get_me()).username}</b>')
    await idle()
    await app.stop()


# 1. Start the Health Check Server in a background thread FIRST
threading.Thread(target=run_health_check_server, daemon=True).start()

# 2. Then start the bot's main loop
app.loop.run_until_complete(main())
