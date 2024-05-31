# from fastapi import APIRouter, Request, Response, HTTPException, Header
# from src.config import settings
# from src.utils import verify_slack_request, create_modal_view
# import requests
# from starlette.responses import JSONResponse
# import json

# router = APIRouter()

# @router.post("/slack/commands")
# async def incident(
#     request: Request,
#     response: Response,
#     slack_request_timestamp: str = Header(None),
#     slack_signature: str = Header(None)
# ):
#     # Handle Slack URL verification
#     body = await request.json()
#     if "challenge" in body:
#         return JSONResponse(content={"challenge": body["challenge"]})

#     # Verify Slack request
#     await verify_slack_request(request, slack_signature, slack_request_timestamp)

#     form_data = await request.form()
    
#     if not form_data:
#         raise HTTPException(status_code=400, detail="Missing form data")
#     # Process form data
#     token = form_data.get("token")
#     if token != settings.SLACK_VERIFICATION_TOKEN:
#         raise HTTPException(status_code=400, detail="Invalid token")
    
    
#     command = form_data.get("command")
#     trigger_id = form_data.get("trigger_id")
    
#     if command == "/create-incident":
#         headers = {
#             "Content-Type": "application/json(charset=utf-8)",
#             "Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"
#         }
#         modal_view = create_modal_view()
#         payload = {
#             "trigger_id": trigger_id,
#             "view": modal_view
#         }
#         print(json.dumps(payload, indent=2))  # Log the payload for debugging
        
#         slack_response = requests.post("https://slack.com/api/views.open", headers=headers, json=payload)
#         if slack_response.status_code != 200 or not response.json().get("ok"):
#             raise HTTPException(status_code=400, detail=f"Failed to open the form: {slack_response.text}")
#         return JSONResponse(status_code=200, content={"response_type": "ephemeral", "text": "Opening incident report form..."})
#     else:
#         return JSONResponse(status_code=404, content={"detail": "Command not found"})







from fastapi import APIRouter, Request, Response, HTTPException, Header
from src.utils import verify_slack_request, create_modal_view
from starlette.responses import JSONResponse
from src.config import settings
import os
import requests
import json
import hashlib
import hmac

router = APIRouter()

# Endpoint to handle slash commands
@router.post("/slack/commands")
async def incident(
    request: Request,
    x_slack_request_timestamp: str = Header(None),
    x_slack_signature: str = Header(None)
):
    
    # Debugging statement to check header values
    headers = request.headers
    print("Headers received:")
    for key, value in headers.items():
        print(f"{key}: {value}")
    
    # Verify Slack request signature
    await verify_slack_request(request, x_slack_signature, x_slack_request_timestamp)

    # Parse form data
    try:
        form_data = await request.form()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse form data: {str(e)}")

    token = form_data.get("token")
    if token != settings.SLACK_VERIFICATION_TOKEN:
        raise HTTPException(status_code=400, detail="Invalid token")

    command = form_data.get("command")
    trigger_id = form_data.get("trigger_id")

    if command == "/create-incident":
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"
        }
        modal_view = await create_modal_view()
        payload = {
            "trigger_id": trigger_id,
            "view": modal_view
        }
        print(json.dumps(payload, indent=2))  # Log the payload for debugging

        try:
            slack_response = requests.post("https://slack.com/api/views.open", headers=headers, json=payload)
            slack_response.raise_for_status()  # Raise an exception for HTTP errors
            slack_response_data = slack_response.json()  # Parse JSON response
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Failed to open the form: {str(e)}")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse Slack response: {str(e)}")

        if not slack_response_data.get("ok"):
            raise HTTPException(status_code=400, detail=f"Slack API error: {slack_response_data}")

        return JSONResponse(status_code=200, content={"response_type": "ephemeral", "text": "Incident form opening executed successfully in the fastapi Backend"})
    else:
        return JSONResponse(status_code=404, content={"detail": "Command not found"})

Endpoint to handle interactivity
@router.post("/slack/interactions")
async def slack_interactions(
    request: Request,
    slack_signature: str = Header(None),
    slack_request_timestamp: str = Header(None)
):
    body = await request.body()
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse request body: {str(e)}")

    # Verify Slack request
    await verify_slack_request(request, slack_signature, slack_request_timestamp)

    token = payload.get("token")

    if token != settings.SLACK_VERIFICATION_TOKEN:
        raise HTTPException(status_code=400, detail="Invalid token")

    if payload.get("type") == "view_submission":
        # Process the submitted modal data here
        print(payload)  # Log the payload for debugging
        return JSONResponse(content={"response_action": "clear"})

#     return JSONResponse(content={})

@router.post("/incidents")
def create_incident():
    return {"status": "success", "message": "Incident form processed successfully"}

@router.get("/incidents/{incident_id}")
def get_incident(incident_id: int):
    return {"incident_id": incident_id}
