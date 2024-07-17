from fastapi import APIRouter, Request, Response, HTTPException, Header, status, Depends
from typing import List
from sqlalchemy.orm import Session 
from src import models
from src.models import Incident
from src import schemas
from src.database import get_db
from src.utils import verify_slack_request, create_modal_view
from starlette.responses import JSONResponse
from src.config import settings
import requests
import json
from pydantic import ValidationError
from datetime import datetime
from src.helperFunctions.opsgenie import create_alert
from src.helperFunctions.jira import create_jira_ticket

router = APIRouter()


# API endpoint for handling Slack slash commands. This endpoint is responsible for
# handling incidents reported through Slack's slash commands feature.
#
# Slash commands are a way for Slack users to interact with external integrations
# by typing a slash command in a channel, private group, or direct message.
#
# In this case, the /incident slash command is used to report incidents to the
# incident management system. When a user types /incident, a modal dialog is
# presented to the user to collect information about the incident. The user
# can then fill in the details of the incident and submit it to the system.
#
# This endpoint receives HTTP POST requests from Slack with the details of the
# slash command and its associated payload. The endpoint verifies the
# authenticity of the request using a cryptographic signature sent by Slack.
# If the request is valid, the endpoint processes the payload and either
# creates a new incident or updates an existing one in the system.
#
# The endpoint is designed to be used with FastAPI, a modern, fast (high-performance)
# web framework for building APIs with Python 3.6+ based on standard Python type hints.
# FastAPI automatically generates an OpenAPI specification for the API, which can
# be used by clients to interact with the API.
@router.post("/slack/commands")
async def incident(
    request: Request,
    x_slack_request_timestamp: str = Header(None),
    x_slack_signature: str = Header(None),
):
    # Debugging statement to check header values
    headers = request.headers
    print("Headers received:")
    for key, value in headers.items():
        print(f"{key}: {value}")

    # Verify Slack request signature
    try:
        await verify_slack_request(
            request, x_slack_signature, x_slack_request_timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Parse form data
    try:
        form_data = await request.form()
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to parse form data: {str(e)}"
        )

    # Handle URL verification with slack
    if form_data.get("type") == "url_verification":
        return {"challenge": form_data.get("challenge")}

    token = form_data.get("token")
    if token != settings.SLACK_VERIFICATION_TOKEN:
        raise HTTPException(status_code=400, detail="Invalid token")

    command = form_data.get("command")
    trigger_id = form_data.get("trigger_id")

    if command == "/create-incident":
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}",
        }
        modal_view = await create_modal_view(callback_id="incident_form")
        payload = {"trigger_id": trigger_id, "view": modal_view}
        print(json.dumps(payload, indent=2))  # Log the payload for debugging
        try:
            slack_response = requests.post(
                "https://slack.com/api/views.open", headers=headers, json=payload
            )
            slack_response.raise_for_status()  # Raise an exception for HTTP errors
            slack_response_data = slack_response.json()  # Parse JSON response
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to open the form: {str(e)}"
            )
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to parse Slack response: {str(e)}"
            )

        if not slack_response_data.get("ok"):
            raise HTTPException(
                status_code=400, detail=f"Slack API error: {slack_response_data}"
            )

        return JSONResponse(
            status_code=200,
            content={
                "response_type": "ephemeral",
                "text": "Incident form opening executed successfully in the fastapi Backend",
            },
        )
    else:
        return JSONResponse(status_code=404, content={"detail": "Command not found"})


# Endpoint to handle interactivity when sending the post back to the server from slack
@router.post("/slack/interactions", status_code=status.HTTP_201_CREATED)
async def slack_interactions(
    request: Request,
    db: Session = Depends(get_db),
    x_slack_signature: str = Header(None),
    x_slack_request_timestamp: str = Header(None),
):
    # Verify Slack request
    await verify_slack_request(request, x_slack_signature, x_slack_request_timestamp)

    # Parse form data
    try:
        form_data = await request.form()
        payload = form_data.get("payload")
        if not payload:
            raise HTTPException(
                status_code=400, detail="Payload is missing in the request"
            )
        payload_data = json.loads(payload)
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to parse request body: {str(e)}"
        )

    # Validate the token
    token = payload_data.get("token")
    if token != settings.SLACK_VERIFICATION_TOKEN:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Processing the actual interaction based on the propagated event
    if payload_data.get("type") == "view_submission":
        callback_id = payload_data.get("view", {}).get("callback_id")
        if callback_id == "incident_form":
            try:
                state_values = (
                    payload_data.get("view", {}).get("state", {}).get("values", {})
                )
                print("State values:", json.dumps(state_values, indent=2))

                # Extracting and converting the start_time and end_time
                start_date = state_values.get("start_time", {}).get("start_date_action", {}).get("selected_date")
                start_time = state_values.get("start_time_picker", {}).get("start_time_picker_action", {}).get("selected_time")
                end_date = state_values.get("end_time", {}).get("end_date_action", {}).get("selected_date")
                end_time = state_values.get("end_time_picker", {}).get("end_time_picker_action", {}).get("selected_time")
                

                
                if not start_date or not start_time:
                    raise HTTPException(status_code=400, detail="Missing start datetime")
                if not end_date or not end_time:
                    raise HTTPException(status_code=400, detail="Missing end datetime")
                
                # Combine date and time strings
                start_datetime_str = f"{start_date}T{start_time}:00"
                end_datetime_str = f"{end_date}T{end_time}:00"
                
                
                #Exception handling
                try:
                    start_time_obj = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M:%S')
                    end_time_obj = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid datetime format")
                
                
                # Parsing the extracted values and converting them to the appropriate data types
                # After receiving the Slack payload
                # Extracting values from the Slack payload
                affected_products_options = state_values.get("affected_products", {}).get("affected_products_action", {}).get("selected_options", [])
                affected_products = [option["value"] for option in affected_products_options]

                suspected_owning_team_options = state_values.get("suspected_owning_team", {}).get("suspected_owning_team_action", {}).get("selected_options", [])
                suspected_owning_team = [option["value"] for option in suspected_owning_team_options]

                suspected_affected_components_options = state_values.get("suspected_affected_components", {}).get("suspected_affected_components_action", {}).get("selected_options", [])
                suspected_affected_components = [option["value"] for option in suspected_affected_components_options]

                print(f"Extracted values: {affected_products} {suspected_owning_team} {suspected_affected_components}")


                # Print for debugging
                print(f"Processed Affected Products: {affected_products}")
                print(f"Processed Suspected Owning Team: {suspected_owning_team}")
                print(f"Processed Suspected Affected Components: {suspected_affected_components}")
                print("Extracted values:", affected_products, suspected_owning_team)

                
                incident_data = {
                    "affected_products": affected_products,
                    "severity": state_values.get("severity", {}).get("severity_action", {}).get("selected_option", {}).get("value"),
                    "suspected_owning_team": suspected_owning_team,
                    "start_time": start_time_obj.isoformat(),
                    "end_time": end_time_obj.isoformat(),
                    "p1_customer_affected": any(option.get("value") == "p1_customer_affected" for option in state_values.get("p1_customer_affected", {}).get("p1_customer_affected_action", {}).get("selected_options", [])),
                    "suspected_affected_components": suspected_affected_components,
                    "description": state_values.get("description", {}).get("description_action", {}).get("value"),
                    "message_for_sp": state_values.get("message_for_sp", {}).get("message_for_sp_action", {}).get("value", ""),
                    "statuspage_notification": any(option.get("value") == "statuspage_notification" for option in state_values.get("flags_for_statuspage_notification", {}).get("flags_for_statuspage_notification_action", {}).get("selected_options", [])),
                    "separate_channel_creation": any(option.get("value") == "separate_channel_creation" for option in state_values.get("flags_for_statuspage_notification", {}).get("flags_for_statuspage_notification_action", {}).get("selected_options", [])),
                }
   
                print(
                    "Incident data:", json.dumps(incident_data, indent=4)
                )  # Log the incident data for debugging
                
                

                try:
                    incident = schemas.IncidentCreate(**incident_data)
                    print(f"Incident data after parsing: {incident}")
                except ValidationError as e:
                    raise HTTPException(
                        status_code=400, detail=f"Failed to parse request body: {str(e)}"
                    )
                # Log the parsed incident data fields
                print("Incident data before Jira ticket creation:")
                print(f"Affected Products: {incident.affected_products}")
                print(f"Suspected Owning Team: {incident.suspected_owning_team}")
                print(f"Suspected Affected Components: {incident.suspected_affected_components}")

            except ValidationError as e:
                raise HTTPException(
                    status_code=400, detail=f"Failed to parse request body: {str(e)}"
                )
            
            # Time to save the incident to our postgresql database
            db_incident = models.Incident(**incident.dict())
            db.add(db_incident)
            db.commit()
            db.refresh(db_incident) 
            
            # Add these debug print statements here
            print(f"Incident data before Jira ticket creation:")
            print(f"Affected Products: {db_incident.affected_products}")
            print(f"Suspected Owning Team: {db_incident.suspected_owning_team}")
            
            if db_incident.end_time is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="End time not found")
            
            
            #Opsgenie integration
            try:
                await create_alert(db_incident)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
            
            #Jira integration-the logic is not implemented yet
            # try:
            #     incident = db.query(Incident).filter(Incident.id == db_incident.id).first()
            #     if not incident:
            #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
            #     issue = create_jira_ticket(incident)
            #     return {"issue_key": issue['key']}
            #     # return {"issue_key": issue.key}
            # except Exception as e:
            #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))    
            try:
                issue = create_jira_ticket(db_incident)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )
            return {"issue_key": issue['key']}
        else:
            return JSONResponse(
                status_code=404, content={"detail": "Command or callback ID not found"}
            )

    return JSONResponse(status_code=404, content={"detail": "Event type not found"})


