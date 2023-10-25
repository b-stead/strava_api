from app.strava import bp
from app import db, login
from flask import Flask, json, render_template, request, redirect, url_for, jsonify, send_from_directory, current_app, session, flash, abort
from flask_login import current_user, login_required, login_user, logout_user, login_manager
import os
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from urllib.parse import urlencode
import requests
from ..models import StravaUser

# Set local id, secret, and redirect_url variables
client_id = os.getenv('STRAVA_CLIENT_ID')
client_secret = os.getenv('STRAVA_CLIENT_SECRET')
redirect_url = "https://af10-92-15-30-29.ngrok-free.app/oauth2_callback"
athlete_url = "https://www.strava.com/api/v3/athlete"

@login.user_loader
def load_user(id):
    return db.session.get(StravaUser, int(id))

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

# Route to connect Strava account
@bp.route('/connect_strava')
@login_required
def oauth2_authorize():
    # Implement OAuth2 flow to connect Strava account
    # Set auth url and scope variables
    auth_url = "https://www.strava.com/oauth/authorize"

    qs = urlencode({
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_url,
        'approval_prompt': 'force',
        'scope': 'read_all',
    })
    #url = "https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_url}&approval_prompt=force&scope=read"
    # redirect the user to the OAuth2 provider authorization URL
    url = auth_url + '?' + qs
    #print(url)
    return redirect(url)


@bp.route('/oauth2_callback/')
@login_required
def oauth2_callback():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    
    # if there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('index'))
    
    # Get the code parameter from the query string
    code = request.args.get('code')

    # make sure that the authorization code is present
    if 'code' not in request.args:
        abort(401)
    
    if code:
        # Initialize the OAuth2Session
        auth_session = OAuth2Session(client_id, redirect_uri=redirect_url)

        # Exchange the code for an access token
        token_url = 'https://www.strava.com/oauth/token'
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
        }
        token_response = auth_session.post(token_url, data=token_data)

        if token_response.status_code != 200:
            abort(401)

        access_token = token_response.json()['access_token']
        if not access_token:
            abort(401)
            # Access token obtained successfully
        

        refresh_token = token_response.json()['refresh_token']
        strava_id = token_response.json()['athlete']['id']
        username = token_response.json()['athlete']['username']
        user = db.session.scalar(db.select(StravaUser).where(StravaUser.strava_id == strava_id))

        if user is None:
            user = StravaUser(strava_id=strava_id, username=username, 
                                token=access_token,refresh_token=refresh_token
                                )
            db.session.add(user)
            db.session.commit()

        # use the access token to get the user's email address
        athlete_response = requests.get(athlete_url, headers={
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json',
        })

        athlete_info = athlete_response.json()
        session['athlete_info'] = athlete_info
        # Redirect to a success page or wherever you want
        login_user(user)
        return redirect(url_for('strava.success'))

    # Handle any errors or redirect to an error page
    return redirect(url_for('strava.error'))

@bp.route('/success')
@login_required 
def success():
    athlete_info = session.get('athlete_info')
    return render_template('strava/strava_index.html', athlete_info=athlete_info)

# Function to refresh the access token using the refresh token
def refresh_access_token(refresh_token):
    refresh_url = 'https://www.strava.com/api/v3/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    refresh_response = requests.post(refresh_url, data=data)
    return refresh_response

@bp.route('/get_route_info/<int:user_id>', methods=['GET'])
@login_required
def get_route_info(user_id):
    user = db.session.query(StravaUser).filter(StravaUser.strava_id == user_id).first()
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    access_token = user.token
    refresh_token = user.refresh_token
    api_url = f'https://www.strava.com/api/v3/athletes/{user_id}/routes?page=1&per_page=30'
    headers = {'Authorization': f'Bearer {access_token}'}

    with requests.Session() as session:
        response = session.get(api_url, headers=headers)

        if response.status_code == 401:
            refresh_response = refresh_access_token(refresh_token)
            if refresh_response.status_code == 200:
                new_access_token = refresh_response.json().get('access_token')
                user.token = new_access_token
                db.session.commit()
                headers['Authorization'] = f'Bearer {new_access_token}'
                response = session.get(api_url, headers=headers)

        if response.status_code != 200:
            return jsonify({'error': 'Request failed.'}), response.status_code

        route_info = response.json()
        with open('static.starva_routes.json', 'w') as outfile:
            json.dump(route_info, outfile, indent=4)
    
    return jsonify(route_info)

# Function to fetch full route details from the Strava API
def fetch_full_route_details(route_id, access_token):
    api_url = f'https://www.strava.com/api/v3/routes/{route_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    with requests.Session() as session:
        response = session.get(api_url, headers=headers)

@bp.route('/fetch_and_save_routes', methods=['GET','POST'])
@login_required
def fetch_and_save_routes():
    
    user_id = current_user.id  # Get the user's ID
    user = db.session.query(StravaUser).filter(StravaUser.strava_id == user_id).first()

    data = request.get_json()
    selected_routes = data.get('selected_routes', [])

    access_token = user.token
    refresh_token = user.refresh_token

    

    # Iterate through the selected routes and fetch full route details
    for route in selected_routes:
        route_id = route['route_id']
        
        # Use the user's access token to make an API request to Strava to get full route details
        # This might involve multiple API requests to get different pieces of route information, including the GPX file
        full_route_details = fetch_full_route_details(route_id, access_token)
        print(full_route_details)
        # Save the full route details to your routes table
        #new_route = Route(user_id=user_id, route_id=route_id, full_route_data=full_route_details)
        #db.session.add(new_route)

    # Commit the changes to the database
    #db.session.commit()

    return jsonify({'message': 'Selected routes saved successfully'})

@bp.route('/error')
@login_required
def error():
    return "There was an error connecting your Strava account."
# Route to list user's routes
@bp.route('/user_routes', methods=['GET'])
@login_required
def user_routes():
    pass
    # Use the access token to make API requests to get user's routes
    # Display the user's routes in a template

# Route to upload GPS file to the club
@bp.route('/upload_gps', methods=['POST'])
@login_required
def upload_gps():
    pass
    # Handle file upload here and save the file's path in the database
    # Associate the file with the user and the club

# Route to list and download club GPS files
@bp.route('/club_gps', methods=['GET'])
@login_required
def club_gps():
    pass
    # Query the database for GPS files associated with the club
    # Display the list of GPS files and provide download links

# Route to download a GPS file
@bp.route('/download_gps/<file_name>', methods=['GET'])
@login_required
def download_gps(file_name):
    pass
    # Serve the GPS file for download
    directory = '/path/to/your/uploaded/files/directory'
    return send_from_directory(directory, file_name)

# Other routes for your application
# ...
