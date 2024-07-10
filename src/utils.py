from fastapi import Request, HTTPException
from .config import settings
import hmac
import hashlib
import json


async def verify_slack_request(
    request: Request, x_slack_signature: str, x_slack_request_timestamp: str
):
    if x_slack_signature is None or x_slack_request_timestamp is None:
        raise HTTPException(
            status_code=400, detail="Missing Slack signature or timestamp"
        )

    body = await request.body()
    sig_base = f"v0:{x_slack_request_timestamp}:{body.decode('utf-8')}"
    my_signature = (
        "v0="
        + hmac.new(
            settings.SLACK_SIGNING_SECRET.encode(), sig_base.encode(), hashlib.sha256
        ).hexdigest()
    )

    if not hmac.compare_digest(my_signature, x_slack_signature):
        raise HTTPException(status_code=400, detail="Invalid request signature")


async def slack_challenge_parameter_verification(request: Request):
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to parse JSON body: {str(e)}"
        )
    # Handle URL verification with slack to accept the challenge parameter
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}


async def create_modal_view(callback_id: str) -> dict:
    return {
        "type": "modal",
        "callback_id": callback_id,
        "title": {"type": "plain_text", "text": "Report Incident"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "private_metadata": json.dumps({"callback_id": callback_id}),
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
                ],
                "action_id": "affected_products_action"
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
                ],
                "action_id": "severity_action"
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
                ],
                "action_id": "suspected_owning_team_action"
            }
        },
        {
            "type": "input",
            "block_id": "start_time",
            "label": {
                "type": "plain_text",
                "text": "Start Time",
                "emoji": True
            },
            "element": {
                "type": "datepicker",
                "action_id": "start_date_action"
            }
        },
        {
            "type": "input",
            "block_id": "end_time",
            "label": {
                "type": "plain_text",
                "text": "End Time",
                "emoji": True
            },
            "element": {
                "type": "datepicker",
                "action_id": "end_date_action"
            }
        },
        {
            "type": "input",
            "block_id": "start_time_picker",
            "label": {
                "type": "plain_text",
                "text": "Start Time Picker",
                "emoji": True
            },
            "element": {
                "type": "timepicker",
                "action_id": "start_time_picker_action"
            }
        },
        {
            "type": "input",
            "block_id": "end_time_picker",
            "label": {
                "type": "plain_text",
                "text": "End Time Picker",
                "emoji": True
            },
            "element": {
                "type": "timepicker",
                "action_id": "end_time_picker_action"
            }
        },
        {
            "type": "input",
            "block_id": "p1_customer_affected",
            "label": {
                "type": "plain_text",
                "text": "P1 Customer Affected"
            },
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
                ],
                "action_id": "p1_customer_affected_action"
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
                ],
                "action_id": "suspected_affected_components_action"
            }
        },
        {
            "type": "input",
            "block_id": "description",
            "label": {
                "type": "plain_text",
                "text": "Description"
            },
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": "description_action",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Enter description"
                }
            }
        },
        {
            "type": "input",
            "block_id": "message_for_sp",
            "label": {
                "type": "plain_text",
                "text": "Message for SP"
            },
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": "message_for_sp_action",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Enter message"
                }
            }
        },
        {
            "type": "input",
            "block_id": "flags_for_statuspage_notification",
            "label": {
                "type": "plain_text",
                "text": "Flags"
            },
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
                ],
                "action_id": "flags_for_statuspage_notification_action"
            }
        },
        # {
        #     "type": "actions",
        #     "block_id": "actionblock789",
        #     "elements": [
        #         {
        #             "type": "button",
        #             "text": {
        #                 "type": "plain_text",
        #                 "text": "Submit"
        #             },
        #             "style": "primary",
        #             "value": "click_me_123",
        #             "action_id": "button-action"
        #         }
        #     ]
        # }
    ]
    }
 
 
