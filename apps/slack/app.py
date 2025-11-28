import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from .detection import detector

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message()
def handle_message(message, say, client):
    text = message.get("text", "")
    user_id = message.get("user")
    channel_id = message.get("channel")
    
    # Run detection
    result = detector.analyze_text(text)
    
    if result["flagged"]:
        # Send ephemeral warning
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=f"⚠️ Your message was flagged as potentially harmful. Please review our code of conduct.",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⚠️ **Wait!** Your message was flagged as potentially harmful (Toxicity: {result['scores']['toxicity']}).\n\nPlease consider rephrasing."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Edit Message"},
                            "action_id": "edit_message_action"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Delete"},
                            "style": "danger",
                            "action_id": "delete_message_action"
                        }
                    ]
                }
            ]
        )

@app.action("report_incident")
def open_report_modal(ack, body, client):
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "submit_report",
            "title": {"type": "plain_text", "text": "Anonymous Report"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "incident_description",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "description",
                        "multiline": True
                    },
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from .detection import detector

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message()
def handle_message(message, say, client):
    text = message.get("text", "")
    user_id = message.get("user")
    channel_id = message.get("channel")
    
    # Run detection
    result = detector.analyze_text(text)
    
    if result["flagged"]:
        # Send ephemeral warning
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=f"⚠️ Your message was flagged as potentially harmful. Please review our code of conduct.",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⚠️ **Wait!** Your message was flagged as potentially harmful (Toxicity: {result['scores']['toxicity']}).\n\nPlease consider rephrasing."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Edit Message"},
                            "action_id": "edit_message_action"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Delete"},
                            "style": "danger",
                            "action_id": "delete_message_action"
                        }
                    ]
                }
            ]
        )

@app.action("report_incident")
def open_report_modal(ack, body, client):
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "submit_report",
            "title": {"type": "plain_text", "text": "Anonymous Report"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "incident_description",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "description",
                        "multiline": True
                    },
                    "label": {"type": "plain_text", "text": "Describe the incident"}
                }
            ]
        }
    )

@app.view("submit_report")
def handle_report_submission(ack, body, view, client):
    ack()
    # Encrypt and send to backend API here
    # For now, just log
    print("Report submitted")

@app.command("/safespace")
def handle_safespace_command(ack, respond, command):
    ack()
    user_query = command['text']
    
    # Call RAG service
    from .rag import rag_service
    response = rag_service.query(user_query)
    
    respond(f"SafeSpace AI: {response}")

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
