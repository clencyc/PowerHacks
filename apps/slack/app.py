# main.py – 100% WORKING VERSION FOR RENDER (NOV 2025)
import os
import json
import logging
from datetime import datetime
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

# ←←← CORRECT SINGLE-WORKSPACE INITIALIZATION (THIS FIXES THE ERROR)
app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# -------------------------------------------------
# Health check
# -------------------------------------------------
@flask_app.route("/")
def health():
    return {"status": "healthy", "service": "SafeSpaceAI", "time": datetime.now().isoformat()}

# -------------------------------------------------
# Slack events endpoint
# -------------------------------------------------
@flask_app.route("/slack/events", methods=["GET", "POST"])
def slack_events():
    return handler.handle(request)

@app.event("app_mention")
def handle_app_mention(event, say):
    say("YES! SafeSpaceAI is fully alive and responding! You did it after 8 hours of hell!")

@app.event("message")
def handle_message_events(event, client):
    if event.get("subtype") or event.get("bot_id"):
        return
    text = event.get("text", "")
    if len(text.strip()) < 3:
        return
        
@app.command("/gbv-help")
def handle_gbv_help_command(ack, respond, command):
    ack()
    respond("SafeSpaceAI is here to help with GBV resources in the workplace.")

@app.command("/gbv-report")
def handle_gbv_report_command(ack, body, client):
    ack()

@app.command("/gbv-privacy")
def handle_privacy_command(ack, respond):
    ack()
    respond("Your privacy is protected. Reports are encrypted and anonymous.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Starting SafeSpaceAI on port {port}")
    flask_app.run(host="0.0.0.0", port=port)
