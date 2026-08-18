"""
Al-Furqan AI - Unified Production Entrypoint v2.0
Runs both the FastAPI Web Server and the Telegram Bot concurrently.
Includes built-in Render 24/7 Keep-Alive Daemon to prevent free-tier spin-down.
"""

import os
import sys
import time
import threading
import urllib.request
import uvicorn

def run_keep_alive_daemon():
    """
    Background daemon that periodically pings the local health endpoint and
    public Render URL to prevent the container from sleeping on free tier.
    """
    time.sleep(15) # Wait for server to start up
    port = int(os.environ.get("PORT", 8000))
    external_url = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
    local_url = f"http://127.0.0.1:{port}/api/v1/health"
    
    print(f"[Keep-Alive] Daemon started. Monitoring local: {local_url} | External: {external_url or 'Self-managed'}")
    
    while True:
        try:
            # 1. Ping local health check
            req = urllib.request.Request(local_url, headers={"User-Agent": "AlFurqanKeepAlive/2.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    pass
        except Exception as e:
            # Local ping silent ignore during startup
            pass

        # 2. Ping external Render URL if configured
        if external_url:
            try:
                ext_ping_url = f"{external_url}/api/v1/health"
                req_ext = urllib.request.Request(ext_ping_url, headers={"User-Agent": "AlFurqanKeepAlive/2.0"})
                with urllib.request.urlopen(req_ext, timeout=15) as resp:
                    if resp.status == 200:
                        print(f"[Keep-Alive] Successfully pinged {ext_ping_url} (200 OK)")
            except Exception as e:
                print(f"[Keep-Alive] External ping notice: {e}")

        # Sleep for 8 minutes (Render sleeps after 15 min, so 8 min is optimal)
        time.sleep(480)

def run_telegram_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("[Unified Runner] TELEGRAM_BOT_TOKEN not set. Telegram bot disabled.")
        return
    
    print("[Unified Runner] Starting Telegram Bot (@alfurqan_quran_bot) in background supervisor thread...")
    while True:
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            import bot
            bot.main()
            break
        except Exception as e:
            print(f"[Unified Runner] Telegram Bot supervisor notice: {e}. Auto-restarting in 10s...")
            time.sleep(10)


def run_web_server():
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"[Unified Runner] Starting FastAPI Web Server on {host}:{port}...")
    uvicorn.run("server:app", host=host, port=port, log_level="info")

if __name__ == "__main__":
    # 1. Start Keep-Alive Daemon
    keep_alive_thread = threading.Thread(target=run_keep_alive_daemon, daemon=True)
    keep_alive_thread.start()

    # 2. Start Telegram bot in daemon background thread if token is present
    if os.environ.get("TELEGRAM_BOT_TOKEN"):
        bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        bot_thread.start()
    
    # 3. Run FastAPI web server on main thread
    run_web_server()
