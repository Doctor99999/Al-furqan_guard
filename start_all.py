"""
Al-Furqan AI - Unified Production Entrypoint
Runs both the FastAPI Web Server and the Telegram Bot concurrently in a single process / container.
Perfect for 1-Click deployment on Render, Railway, Fly.io, and Docker.
"""

import os
import sys
import threading
import uvicorn

def run_telegram_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("[Unified Runner] TELEGRAM_BOT_TOKEN not set. Telegram bot disabled.")
        return
    
    print("[Unified Runner] Starting Telegram Bot in background thread...")
    try:
        import bot
        bot.main()
    except Exception as e:
        print(f"[Unified Runner] Telegram Bot error: {e}")

def run_web_server():
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"[Unified Runner] Starting FastAPI Web Server on {host}:{port}...")
    uvicorn.run("server:app", host=host, port=port, log_level="info")

if __name__ == "__main__":
    # Start Telegram bot in daemon background thread if token is present
    if os.environ.get("TELEGRAM_BOT_TOKEN"):
        bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        bot_thread.start()
    
    # Run FastAPI web server on main thread
    run_web_server()
