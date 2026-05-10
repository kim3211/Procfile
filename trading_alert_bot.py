"""
Universal Trading Alert Bot
TradingView Webhook → Python Server → Telegram Message

Supports: ANY coin, ANY timeframe, ANY exchange
BTC, ETH, SOL, PEPE, DOGE, XRP — sab kuch

Requirements:
    pip install flask requests

Usage:
    python trading_alert_bot.py
"""

import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ─────────────────────────────────────────────
#  CONFIG — Sirf yahan apni values daalo
# ─────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID   = "YOUR_CHAT_ID_HERE"
WEBHOOK_SECRET     = "my_trading_bot_2026"   # Koi bhi secret word rakho

# ─────────────────────────────────────────────
#  TELEGRAM SENDER
# ─────────────────────────────────────────────
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print(f"[✅ SENT] {datetime.now().strftime('%H:%M:%S')} | Telegram OK")
    except Exception as e:
        print(f"[❌ ERROR] Telegram send failed: {e}")


# ─────────────────────────────────────────────
#  ALERT FORMATTER — Any Coin Support
# ─────────────────────────────────────────────
def format_alert(data: dict) -> str:
    signal    = data.get("signal", "UNKNOWN").upper()   # LONG / SHORT / CLOSE
    pair      = data.get("pair", "BTC/USDT")            # Any pair
    exchange  = data.get("exchange", "Binance")         # Binance / CoinDCX etc
    timeframe = data.get("timeframe", "15m")
    score     = data.get("score", "")                   # Optional score
    entry     = data.get("entry", "?")
    sl        = data.get("sl", "?")
    tp1       = data.get("tp1", "?")
    tp2       = data.get("tp2", "")                     # Optional
    tp3       = data.get("tp3", "")                     # Optional
    rr        = data.get("rr", "")                      # Optional
    strategy  = data.get("strategy", "")                # e.g. "ICT Kill Zone"
    note      = data.get("note", "")
    ts        = datetime.now().strftime("%d %b %Y | %H:%M:%S")

    # Signal emoji
    if signal == "LONG":
        header = "🟢 <b>LONG SETUP</b>"
        direction = "📈 BUY / LONG"
    elif signal == "SHORT":
        header = "🔴 <b>SHORT SETUP</b>"
        direction = "📉 SELL / SHORT"
    elif signal == "CLOSE":
        header = "⚪ <b>CLOSE / EXIT SIGNAL</b>"
        direction = "🚪 EXIT TRADE"
    else:
        header = "🔔 <b>ALERT</b>"
        direction = signal

    msg = f"""{header}
━━━━━━━━━━━━━━━━━━━━
📊 <b>{pair}</b> | {timeframe} | {exchange}
⏰ {ts}"""

    if strategy:
        msg += f"\n📋 <b>Strategy:</b> {strategy}"

    if score:
        msg += f"\n🎯 <b>Score:</b> {score}"

    msg += f"""
━━━━━━━━━━━━━━━━━━━━
{direction}

📌 <b>Entry:</b>  <code>{entry}</code>
🛑 <b>SL:</b>     <code>{sl}</code>
✅ <b>TP1:</b>    <code>{tp1}</code>"""

    if tp2:
        msg += f"\n🏆 <b>TP2:</b>    <code>{tp2}</code>"
    if tp3:
        msg += f"\n💎 <b>TP3:</b>    <code>{tp3}</code>"
    if rr:
        msg += f"\n📐 <b>R:R:</b>    {rr}"

    msg += "\n━━━━━━━━━━━━━━━━━━━━"

    if note:
        msg += f"\n📝 {note}\n━━━━━━━━━━━━━━━━━━━━"

    msg += "\n⚠️ <i>Alert only — verify before entering.</i>"

    return msg.strip()


# ─────────────────────────────────────────────
#  WEBHOOK ENDPOINT
# ─────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    # Security check
    secret = request.args.get("secret", "")
    if secret != WEBHOOK_SECRET:
        print("[⛔ BLOCKED] Wrong secret key")
        return jsonify({"error": "Unauthorized"}), 401

    # Parse body
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw = request.data.decode("utf-8")
            data = json.loads(raw)
    except Exception as e:
        print(f"[❌ PARSE ERROR] {e}")
        return jsonify({"error": "Invalid JSON"}), 400

    print(f"[📥 ALERT] {data.get('pair', '?')} | {data.get('signal', '?')} | {datetime.now().strftime('%H:%M:%S')}")

    message = format_alert(data)
    send_telegram(message)

    return jsonify({"status": "ok"}), 200


# ─────────────────────────────────────────────
#  HEALTH CHECK
# ─────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "✅ Running",
        "bot": "Universal Trading Alert Bot",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), 200


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Universal Trading Alert Bot Starting...")
    print(f"   Webhook: http://localhost:5000/webhook?secret={WEBHOOK_SECRET}")
    print("   Ready for alerts from TradingView...\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
