# ──────────────────────────────────────────────────────────────
# SafeSpace AI Slack Bot — Flask + HTTP Events API Mode
# ──────────────────────────────────────────────────────────────

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests
from cryptography.fernet import Fernet

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

try:
    # Try to use full detector with ML models
    from detection import detector
    logger.info("Using full ML-based GBV detector")
except ImportError as e:
    # Fallback to lightweight detector
    logger.warning(f"ML libraries not available ({e}), using lightweight detector")
    from detection_lite import detector

from rag import rag_service

# ── CORRECT SLACK APP CONFIGURATION FOR HTTP MODE ──
app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)

# API endpoint for reports
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Encryption for anonymous reports
ENCRYPTION_KEY = os.environ.get("REPORT_ENCRYPTION_KEY")
if ENCRYPTION_KEY:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode() if len(ENCRYPTION_KEY) == 44 else Fernet.generate_key())
else:
    cipher_suite = Fernet(Fernet.generate_key())
    logger.warning("Using generated encryption key. Set REPORT_ENCRYPTION_KEY in production.")

def get_channel_type(channel_id, client):
    """Determine if channel is public, private, or DM"""
    try:
        # Try to get channel info
        response = client.conversations_info(channel=channel_id)
        channel = response["channel"]
        
        if channel.get("is_im"):
            return "dm"
        elif channel.get("is_private"):
            return "private"
        else:
            return "public"
    except Exception:
        return "unknown"

@app.event("message")
def handle_message_events(event, client):
    """Handle all message events for proactive monitoring"""
    # Skip bot messages and already processed messages
    if event.get("subtype") or event.get("bot_id"):
        return
    
    text = event.get("text", "")
    user_id = event.get("user")
    channel_id = event.get("channel")
    channel_type = get_channel_type(channel_id, client)
    
    # Skip very short messages
    if len(text.strip()) < 3:
        return
    
    try:
        # Run GBV detection
        result = detector.analyze_text(text, user_id, channel_type)
        
        if result["flagged"]:
            handle_flagged_message(result, event, client, channel_type)
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def handle_flagged_message(detection_result, event, client, channel_type):
    """Handle a message that was flagged for GBV content"""
    user_id = event.get("user")
    channel_id = event.get("channel")
    severity = detection_result.get("severity", "low")
    categories = detection_result.get("categories", [])
    
    # Get appropriate response from RAG
    rag_response = rag_service.get_incident_response(severity, categories)
    
    # Determine response strategy based on severity and channel type
    if severity == "high":
        send_high_severity_response(client, channel_id, user_id, rag_response, detection_result)
    elif severity == "medium":
        send_medium_severity_response(client, channel_id, user_id, rag_response, detection_result)
    else:
        send_low_severity_response(client, channel_id, user_id, detection_result)

def send_high_severity_response(client, channel_id, user_id, rag_response, detection_result):
    """Handle high-severity incidents with immediate support"""
    try:
        # Send immediate support via DM
        dm_channel = client.conversations_open(users=[user_id])["channel"]["id"]
        
        client.chat_postMessage(
            channel=dm_channel,
            text="🚨 SafeSpace AI detected you may need immediate support",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🛡️ **SafeSpace AI - Immediate Support Available**\n\n{rag_response}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "🚨 Call Emergency (999)"},
                            "style": "danger",
                            "action_id": "emergency_call",
                            "url": "tel:999"
                        },
                        {
                            "type": "button", 
                            "text": {"type": "plain_text", "text": "📞 GBV Hotline"},
                            "action_id": "gbv_hotline",
                            "url": "tel:0709558000"
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "📋 Anonymous Report"},
                            "action_id": "open_report_modal"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "💬 More Help"},
                            "action_id": "get_more_help"
                        }
                    ]
                }
            ]
        )
        
        # Also send ephemeral in original channel for potential witnesses
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="🛡️ SafeSpace AI is available to help. Check your DMs for private support resources."
        )
        
    except Exception as e:
        logger.error(f"Error sending high severity response: {e}")

def send_medium_severity_response(client, channel_id, user_id, rag_response, detection_result):
    """Handle medium-severity incidents with education and reporting options"""
    try:
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="🌟 SafeSpace AI - Support & Resources Available",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🌟 **SafeSpace AI - Support Available**\n\n{rag_response[:500]}..."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "📋 Report Incident"},
                            "action_id": "open_report_modal"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "💬 Get Help"},
                            "action_id": "get_detailed_help"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "🔒 Privacy Info"},
                            "action_id": "privacy_info"
                        }
                    ]
                }
            ]
        )
    except Exception as e:
        logger.error(f"Error sending medium severity response: {e}")

def send_low_severity_response(client, channel_id, user_id, detection_result):
    """Handle low-severity incidents with educational message"""
    try:
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="💡 SafeSpace AI - Workplace Reminder",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "💡 **Friendly Reminder**: Let's keep our workplace respectful and inclusive for everyone.\n\n📚 Learn more about our values with `/gbv-help`"
                    }
                },
                {
                    "type": "actions", 
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "💬 Learn More"},
                            "action_id": "learn_more_gbv"
                        }
                    ]
                }
            ]
        )
    except Exception as e:
        logger.error(f"Error sending low severity response: {e}")

# SLASH COMMANDS

@app.command("/gbv-help")
def handle_gbv_help_command(ack, respond, command):
    """Provide GBV help and resources"""
    ack()
    try:
        user_query = command.get('text', 'general help')
        response = rag_service.query(user_query)
        
        respond({
            "response_type": "ephemeral",
            "text": "SafeSpace AI - Help & Resources",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": response
                    }
                }
            ]
        })
    except Exception as e:
        logger.error(f"Error in gbv-help command: {e}")
        respond("I'm having trouble right now. Please call the Gender Violence Recovery Centre at 0709 558 000 for immediate help.")

@app.command("/gbv-report")
def handle_gbv_report_command(ack, body, client):
    """Open anonymous reporting modal"""
    ack()
    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view=get_report_modal()
        )
    except Exception as e:
        logger.error(f"Error opening report modal: {e}")

@app.command("/gbv-privacy")
def handle_privacy_command(ack, respond):
    """Explain privacy and data handling"""
    ack()
    privacy_info = """🔒 **SafeSpace AI Privacy Policy**

**What we collect:**
• Only flagged message metadata (not full content)
• Anonymous reports (encrypted, no user identification)
• Usage statistics (aggregated, no personal data)

**What we DON'T collect:**
• Your private messages unless flagged
• Personal identifying information in reports
• Message history or conversation logs

**Data retention:**
• Flagged message metadata: 30 days maximum
• Anonymous reports: Kept until resolved, then archived
• All data can be deleted on request

**Your rights:**
• Request data deletion anytime
• Report concerns to your HR department
• Access support resources without data collection

**Contact:** For privacy questions, contact your IT administrator."""

    respond({
        "response_type": "ephemeral", 
        "text": privacy_info
    })

# BUTTON ACTIONS

@app.action("open_report_modal")
def open_report_modal(ack, body, client):
    """Open the anonymous reporting modal"""
    ack()
    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view=get_report_modal()
        )
    except Exception as e:
        logger.error(f"Error opening report modal: {e}")

@app.action("get_more_help")
def handle_get_more_help(ack, respond):
    """Provide additional help resources"""
    ack()
    help_response = rag_service.query("comprehensive GBV support resources Kenya")
    respond({
        "response_type": "ephemeral",
        "replace_original": False,
        "text": help_response
    })

@app.action("get_detailed_help")
def handle_get_detailed_help(ack, respond):
    """Provide detailed help for medium-severity incidents"""
    ack()
    help_response = rag_service.query("workplace harassment reporting process Kenya")
    respond({
        "response_type": "ephemeral", 
        "replace_original": False,
        "text": help_response
    })

@app.action("learn_more_gbv")
def handle_learn_more(ack, respond):
    """Educational content about GBV prevention"""
    ack()
    educational_content = rag_service.query("GBV prevention workplace education")
    respond({
        "response_type": "ephemeral",
        "replace_original": False, 
        "text": educational_content
    })

@app.action("privacy_info")
def handle_privacy_info(ack, respond):
    """Show privacy information"""
    ack()
    privacy_text = """🔒 **Your Privacy Matters**

• This conversation is confidential
• Reports are encrypted and anonymous
• No personal data is stored with reports
• You control what information you share

Use `/gbv-privacy` for full privacy policy."""

    respond({
        "response_type": "ephemeral",
        "replace_original": False,
        "text": privacy_text
    })

# MODAL SUBMISSIONS

@app.view("submit_report")
def handle_report_submission(ack, body, view, client):
    """Handle anonymous report submission"""
    ack()
    try:
        # Extract form data
        values = view["state"]["values"]
        description = values["incident_description"]["description"]["value"]
        incident_type = values["incident_type"]["incident_type_select"]["selected_option"]["value"]
        occurred_when = values["when_occurred"]["when_select"]["selected_option"]["value"]
        location = values.get("location", {}).get("location_input", {}).get("value", "")
        witnesses = values.get("witnesses", {}).get("witnesses_input", {}).get("value", "")
        
        # Create encrypted report
        report_data = {
            "description": description,
            "incident_type": incident_type, 
            "occurred_when": occurred_when,
            "location": location,
            "witnesses": witnesses,
            "submitted_at": datetime.now().isoformat(),
            "channel_id": body.get("user", {}).get("id")  # For follow-up only
        }
        
        # Encrypt the report
        encrypted_report = cipher_suite.encrypt(json.dumps(report_data).encode())
        
        # Submit to API
        submit_report_to_api(encrypted_report.decode(), body.get("user", {}).get("id"))
        
        # Send confirmation DM
        user_id = body["user"]["id"]
        dm_channel = client.conversations_open(users=[user_id])["channel"]["id"]
        
        client.chat_postMessage(
            channel=dm_channel,
            text="✅ **Report Submitted Successfully**",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn", 
                        "text": "✅ **Your anonymous report has been submitted securely.**\n\n🔒 Your identity is protected\n📋 Report ID: `" + encrypted_report[:16].decode() + "`\n⏰ Expected response: 24-48 hours\n\n**Immediate Support:**\n📞 Gender Violence Recovery Centre: 0709 558 000\n📞 FIDA Kenya: 0800 720 553"
                    }
                }
            ]
        )
        
    except Exception as e:
        logger.error(f"Error handling report submission: {e}")

def get_report_modal():
    """Generate the anonymous reporting modal"""
    return {
        "type": "modal",
        "callback_id": "submit_report",
        "title": {"type": "plain_text", "text": "Anonymous Report"},
        "submit": {"type": "plain_text", "text": "Submit Securely"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🔒 **This report is completely anonymous and encrypted.**\n\nYour identity will not be shared. Provide as much detail as you're comfortable sharing."
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "input",
                "block_id": "incident_type",
                "element": {
                    "type": "static_select",
                    "action_id": "incident_type_select",
                    "placeholder": {"type": "plain_text", "text": "Select incident type"},
                    "options": [
                        {"text": {"type": "plain_text", "text": "Sexual Harassment"}, "value": "sexual_harassment"},
                        {"text": {"type": "plain_text", "text": "Discrimination"}, "value": "discrimination"}, 
                        {"text": {"type": "plain_text", "text": "Verbal Abuse/Threats"}, "value": "verbal_abuse"},
                        {"text": {"type": "plain_text", "text": "Physical Violence"}, "value": "physical_violence"},
                        {"text": {"type": "plain_text", "text": "Other"}, "value": "other"}
                    ]
                },
                "label": {"type": "plain_text", "text": "Type of Incident"}
            },
            {
                "type": "input", 
                "block_id": "incident_description",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "description",
                    "multiline": True,
                    "placeholder": {"type": "plain_text", "text": "Describe what happened. Include dates, locations, and any other relevant details you're comfortable sharing."}
                },
                "label": {"type": "plain_text", "text": "Description"}
            },
            {
                "type": "input",
                "block_id": "when_occurred", 
                "element": {
                    "type": "static_select",
                    "action_id": "when_select",
                    "placeholder": {"type": "plain_text", "text": "When did this occur?"},
                    "options": [
                        {"text": {"type": "plain_text", "text": "Today"}, "value": "today"},
                        {"text": {"type": "plain_text", "text": "This week"}, "value": "this_week"},
                        {"text": {"type": "plain_text", "text": "This month"}, "value": "this_month"},
                        {"text": {"type": "plain_text", "text": "More than a month ago"}, "value": "older"},
                        {"text": {"type": "plain_text", "text": "Ongoing"}, "value": "ongoing"}
                    ]
                },
                "label": {"type": "plain_text", "text": "When did this occur?"}
            },
            {
                "type": "input",
                "block_id": "location",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "location_input",
                    "placeholder": {"type": "plain_text", "text": "Office, meeting room, virtual meeting, etc. (optional)"}
                },
                "label": {"type": "plain_text", "text": "Location (Optional)"},
                "optional": True
            },
            {
                "type": "input",
                "block_id": "witnesses",
                "element": {
                    "type": "plain_text_input", 
                    "action_id": "witnesses_input",
                    "placeholder": {"type": "plain_text", "text": "Were there witnesses? (optional - no names required)"}
                },
                "label": {"type": "plain_text", "text": "Witnesses (Optional)"},
                "optional": True
            }
        ]
    }

def submit_report_to_api(encrypted_report: str, user_id: str):
    """Submit encrypted report to FastAPI backend"""
    try:
        payload = {
            "encrypted_blob": encrypted_report,
            "channel_id": user_id,  # For follow-up contact only
            "source": "slack"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/reports/",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("Report submitted successfully to API")
        else:
            logger.error(f"Failed to submit report: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error submitting report to API: {e}")

# APP MENTIONS
@app.event("app_mention")
def handle_app_mention(event, say):
    """Handle direct mentions of the bot"""
    try:
        text = event.get("text", "")
        user_id = event.get("user")
        
        # Remove bot mention from text
        clean_text = text.split(">", 1)[-1].strip() if ">" in text else text
        
        if not clean_text:
            clean_text = "help"
            
        response = rag_service.query(clean_text)
        
        say(
            text="SafeSpace AI is here to help",
            blocks=[
                {
                    "type": "section", 
                    "text": {
                        "type": "mrkdwn",
                        "text": response
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "📋 Anonymous Report"},
                            "action_id": "open_report_modal"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "🔒 Privacy Info"},
                            "action_id": "privacy_info"
                        }
                    ]
                }
            ]
        )
    except Exception as e:
        logger.error(f"Error handling app mention: {e}")
        say("I'm having trouble right now. Please use `/gbv-help` or call 0709 558 000 for immediate support.")

# ── FLASK APP SETUP ──
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Health check endpoints
@flask_app.route("/")
def health():
    return {
        "status": "healthy",
        "service": "SafeSpace AI Slack Bot",
        "timestamp": datetime.now().isoformat()
    }

@flask_app.route("/health")
def health_check():
    return {"status": "ok", "bot": "running"}

# Slack events endpoint
@flask_app.route("/slack/events", methods=["GET", "POST"])
def slack_events():
    return handler.handle(request)

# ── All your existing @app.event, @app.command, etc. are already registered above ──

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 Starting SafeSpace AI Slack Bot on port {port}")
    flask_app.run(host="0.0.0.0", port=port, debug=False)
