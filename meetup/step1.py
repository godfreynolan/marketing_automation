from flask import Flask, request, redirect
import requests
import config

app = Flask(__name__)

# Configuration
CLIENT_ID = config.MEETUP_CLIENT_ID
CLIENT_SECRET = config.MEETUP_CLIENT_SECRET
REDIRECT_URI = 'http://127.0.0.1:5000/oauth2/callback'
MEETUP_AUTH_URL = 'https://secure.meetup.com/oauth2/authorize'
MEETUP_TOKEN_URL = 'https://secure.meetup.com/oauth2/access'

@app.route('/')
def home():
    # Redirect the user to Meetup's authorization page
    auth_url = (
        f"{MEETUP_AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
    )
    return f'<a href="{auth_url}">Connect with Meetup</a>'

@app.route('/oauth2/callback')
def oauth_callback():
    # Retrieve the authorization code from the callback
    authorization_code = request.args.get('code')
    if authorization_code:
        # Exchange the authorization code for an access token
        token_response = requests.post(
            MEETUP_TOKEN_URL,
            data={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': REDIRECT_URI,
                'code': authorization_code,
            },
        )
        if token_response.status_code == 200:
            access_token = token_response.json().get('access_token')
            return f'Access token: {access_token}'
        else:
            return 'Failed to obtain access token.', 400
    else:
        return 'Authorization code not found.', 400
    

if __name__ == '__main__':
    app.run(debug=True)
