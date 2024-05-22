import hmac
import hashlib
import time
import urllib.parse

from config import settings

form_data = {
    'token': 'Djk1qAbWR6meez3Y0lVSC2KS',
    'team_id': 'T0001',
    'team_domain': 'example',
    'channel_id': 'C2147483705',
    'channel_name': 'test',
    'user_id': 'U2147483697',
    'user_name': 'Steve',
    'command': '/create-incident',
    'text': 'incident details',
    'response_url': 'https://hooks.slack.com/commands/1234/5678',
    'trigger_id': '13345224609.738474920.8088930838d88f008e0'
}

# URL-encode the form data
request_body = urllib.parse.urlencode(form_data)

# Your Slack Signing Secret
SLACK_SIGNING_SECRET =  settings.SLACK_SIGNING_SECRET

# Current timestamp
timestamp = str(int(time.time()))

# # Request body you are sending (should be URL-encoded form data as a single string)
# request_body = 'token=Djk1qAbWR6meez3Y0lVSC2KS&team_id=T0001&team_domain=example&channel_id=C2147483705&channel_name=test&user_id=U2147483697&user_name=Steve&command=%2Fcreate-incident&text=incident+details&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2F1234%2F5678&trigger_id=13345224609.738474920.8088930838d88f008e0'

# Create the basestring
sig_base = f'v0:{timestamp}:{request_body}'

# Create the signature
my_signature = 'v0=' + hmac.new(
    SLACK_SIGNING_SECRET.encode(),
    sig_base.encode(),
    hashlib.sha256
).hexdigest()

print('x-slack-request-timestamp:', timestamp)
print('x-slack-signature:', my_signature)
print('request-body:', request_body)
