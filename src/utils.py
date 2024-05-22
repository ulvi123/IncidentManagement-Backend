from fastapi import Request,HTTPException
from .config import settings
import hmac
import hashlib


async def verify_slack_request(request: Request, x_slack_signature: str, x_slack_request_timestamp: str):
    if x_slack_signature is None or x_slack_request_timestamp is None:
        raise HTTPException(status_code=400, detail="Missing Slack signature or timestamp")

    body = await request.body()
    sig_base = f"v0:{x_slack_request_timestamp}:{body.decode('utf-8')}"
    my_signature = "v0=" + hmac.new(
        settings.SLACK_SIGNING_SECRET.encode(),
        sig_base.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(my_signature, x_slack_signature):
        raise HTTPException(status_code=400, detail="Invalid request signature")
    
async def create_modal_view():
    return {
        "type": "modal",
        "callback_id": "incident_form",
        "title": {
            "type": "plain_text",
            "text": "Report Incident"
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "section",
                "block_id": "section1",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please fill out the following incident form:"
                }
            },
            {
                "type": "input",
                "block_id": "affected_products",
                "label": {
                    "type": "plain_text",
                    "text": "Affected Products"
                },
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select products"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Product 1"
                            },
                            "value": "product_1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Product 2"
                            },
                            "value": "product_2"
                        }
                    ]
                }
            },
            {
                "type": "input",
                "block_id": "severity",
                "label": {
                    "type": "plain_text",
                    "text": "Severity"
                },
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select severity"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "High"
                            },
                            "value": "high"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Medium"
                            },
                            "value": "medium"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Low"
                            },
                            "value": "low"
                        }
                    ]
                }
            },
            {
                "type": "input",
                "block_id": "suspected_owning_team",
                "label": {
                    "type": "plain_text",
                    "text": "Suspected Owning Team"
                },
                "element": {
                    "type": "multi_static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select teams"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Team 1"
                            },
                            "value": "team_1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Team 2"
                            },
                            "value": "team_2"
                        }
                    ]
                }
            },
            {
                "type": "input",
                "block_id": "start_time",
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Enter start time"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Start Time",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "block_id": "p1_customer_affected",
                "element": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "P1 customer affected"
                            },
                            "value": "p1_customer_affected"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "P1 Customer Affected",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "block_id": "suspected_affected_components",
                "label": {
                    "type": "plain_text",
                    "text": "Suspected Affected Components"
                },
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select components"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Component 1"
                            },
                            "value": "component_1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Component 2"
                            },
                            "value": "component_2"
                        }
                    ]
                }
            },
            {
                "type": "input",
                "block_id": "description",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True
                },
                "label": {
                    "type": "plain_text",
                    "text": "Description",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "block_id": "message_for_sp",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True
                },
                "label": {
                    "type": "plain_text",
                    "text": "Message for SP",
                    "emoji": True
                },
                "optional": True
            },
            {
                "type": "input",
                "block_id": "flags_for_statuspage_notification",
                "element": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Statuspage Notification"
                            },
                            "value": "statuspage_notification"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Separate Channel Creation"
                            },
                            "value": "separate_channel_creation"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Flags",
                    "emoji": True
                }
            },
            {
                "type": "actions",
                "block_id": "actionblock789",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Submit"
                        },
                        "value": "click_me_123",
                        "action_id": "button-action"
                    }
                ]
            }
        ]
    }
