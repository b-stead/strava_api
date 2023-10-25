from flask import Flask, render_template, redirect,jsonify, current_app, session
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = Flask(__name__)

# Define your Strava OAuth2 settings in your app's configuration.
app.config['OAUTH2_PROVIDERS'] = {
    'strava': {
        'client_id': os.getenv('STRAVA_CLIENT_ID'),
        'client_secret': os.getenv('STRAVA_CLIENT_SECRET'),
        'authorize_url': 'https://www.strava.com/oauth/authorize',
        'token_url': 'https://www.strava.com/oauth/token',
        'userinfo': {
            'url': 'https://www.strava.com/api/v3/athlete',
            'username': lambda json: json[5]['username'],
        },
        'scopes': 'read_all',
    },
}

@app.route("/")
def home():
    print(app.config['OAUTH2_PROVIDERS'])

    return render_template('home.html')

@app.route('/connect', methods=['POST'])
def strava_callback():
    strava_settings = current_app.config['OAUTH2_PROVIDERS'].get('strava')
    if strava_settings:
        redirect_uri = 'http://127.0.0.1/exchange_token/'  # Define your redirect URI here.
        strava_client_id = strava_settings.get('client_id')
        authorization_url = f"https://www.strava.com/oauth/authorize?client_id={strava_client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=force&scope=read"
        return redirect(authorization_url)
    else:
        return "Strava OAuth2 settings not found."

def exchange_token():
    # Get the authorization code from the URL
    authorization_code = requests.args.get('code')

    # Define your Strava API credentials
    strava_client_id = 'your_client_id'
    strava_client_secret = 'your_client_secret'

    # Define the token exchange URL
    token_url = 'https://www.strava.com/api/v3/oauth/token'

    # Prepare the request payload
    data = {
        'client_id': strava_client_id,
        'client_secret': strava_client_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code',
    }

    # Make the POST request to exchange the code for tokens
    response = requests.post(token_url, data=data)

    # Parse the response JSON to obtain the tokens and athlete info
    token_data = response.json()

    # Check if the response contains an error
    if 'error' in token_data:
        return f"Error: {token_data['error']} - {token_data.get('error_description')}"

    # Store the tokens in the session
    session['access_token'] = token_data.get('access_token')
    session['refresh_token'] = token_data.get('refresh_token')

    # Optionally, you can also store the athlete info
    athlete_info = token_data.get('athlete')
    session['athlete_info'] = athlete_info

    # You can return a JSON response with the tokens and athlete info if needed
    return jsonify(token_data)

@app.route('/user_info')
def user_info():
    # Check if the user has an access token
    access_token = session.get('access_token')
    if not access_token:
        return "Access token not found. Please authenticate."

    # Define the Strava API endpoint for user info
    user_info_url = 'https://www.strava.com/api/v3/athlete'

    # Prepare headers with the access token
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Make a GET request to fetch user info
    response = requests.get(user_info_url, headers=headers)

    # Parse the response JSON to get user data
    user_data = response.json()

    # Render a template to display the user info
    return render_template('user_info.html', user_data=user_data)

#http://127.0.0.1/exchange_token/?state=&code=893a77bfdcd96d447df928534373d701eb74ece6&scope=read

#http://www.strava.com/oauth/authorize?client_id=114528&response_type=code&redirect_uri=http://127.0.0.1/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all

#http://127.0.0.1/exchange_token?state=&code=82d443cace9939c9f99476f63975ea33c78661e7&scope=read,activity:read_all,profile:read_all