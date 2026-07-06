import os
import sys
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import dns.resolver
from pyrogram import idle
from pyrogram.types import BotCommand  # <--- Added for Auto Commands

from . import app, log

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = [
    '8.8.8.8']  # this is a google public dns


# --- HUGGING FACE HEALTH CHECK SERVER ---
class QuietHTTPServer(HTTPServer):
    def handle_error(self, request, client_address):
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
        return

def run_health_check_server():
    port = int(os.environ.get("PORT", 7860))
    server_address = ('0.0.0.0', port)
    httpd = QuietHTTPServer(server_address, HealthCheckHandler)
    logging.info(f"Starting health check server on port {port}...")
    httpd.serve_forever()
# ----------------------------------------


async def main():
    await app.start()
    
    # --- AUTO UPDATE COMMANDS WITH BOTFATHER ---
    logging.info("Syncing bot commands with BotFather...")
    await app.set_bot_commands([
        BotCommand("start", "Check if the bot is alive"),
        BotCommand("help", "Display the interactive help menu"),
        BotCommand("settings", "Open personal encoding settings menu"),
        BotCommand("reset", "Reset encoding settings to default"),
        BotCommand("vset", "View summary of current video settings"),
        BotCommand("dl", "Process a Telegram file (Reply to video)"),
        BotCommand("af", "Audio stream rearrangement (Reply to video)"),
        BotCommand("ddl", "Process a file from a direct download link"),
        BotCommand("speedtest", "Run a server internet speed test"),
        BotCommand("status", "View server hardware and queue status"),
        BotCommand("stats", "View bot user and uptime statistics"),
        BotCommand("clean", "[Sudo] Clean working directories"),
        BotCommand("restart", "[Sudo] Restart the bot safely"),
        BotCommand("update", "[Sudo] Update bot code from GitHub")
    ])
    logging.info("Commands successfully synced!")
    # --------------------------------------------

    await app.send_message(chat_id=log, text=f'<b>Bot Started! @{(await app.get_me()).username}</b>')
    await idle()
    await app.stop()


# 1. Start the Health Check Server in a background thread
threading.Thread(target=run_health_check_server, daemon=True).start()

# 2. Start the bot's main loop
app.loop.run_until_complete(main())
