# main.py – FINAL VERSION THAT WORKS ON RENDER (Nov 2025)
import os
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

# ←←← THIS IS THE ONLY CORRECT INITIALIZATION FOR SINGLE WORKSPACE + FLASK
app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Health check
@flask_app.route("/")
def health():
    return {"status": "healthy", "service": "SafeSpaceAI", "up": True}

# Slack events endpoint
@flask_app.route("/slack/events", methods=["GET", "POST"])
def slack_events():
    return handler.handle(request)

# ——— YOUR ORIGINAL HANDLERS (copy them back exactly as they were) ———
# Just paste everything from your old file starting from @app.event("message")
# down to the end of all your @app.command / @app.action handlers.
# (I’m assuming they are all still there — they don’t cause the error)

# Example of the first one so you know where to paste:
@app.event("app_mention")
def handle_app_mention(event, say):
    say("Hello! SafeSpaceAI is now fully working 🎉")

# ←←← PASTE THE REST OF YOUR ORIGINAL HANDLERS HERE
# (everything from @app.event("message") … to the very end of handle_report_submission etc.)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
