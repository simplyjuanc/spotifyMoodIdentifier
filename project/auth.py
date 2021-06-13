# %%
import os
from flask import Blueprint, redirect, request
from flask.globals import session
import requests



auth = Blueprint('auth', __name__)


scopes = 'user-read-recently-played'
BASE_URL = 'https://api.spotify.com/v1'

REDIRECT_URI = 'http://localhost:5000/redirect'


@auth.route('/authorise')
def getAccessToken():
    AUTH_URL = 'https://accounts.spotify.com/authorize'
    payload = {
        'client_id':os.getenv('CLIENT_ID'),
        'response_type':'code',
        'redirect_uri':REDIRECT_URI,
        'scope':scopes,
    }

    requests.get(AUTH_URL, data=payload)
    # response_url = urlparse.urlparse(auth_response.url)   
    # print(response_url)
    
    # auth_response_data = auth_response.json()
    # pprint(auth_response_data)

    # session['code'] = auth_response_data['code']
    return redirect('/redirect')



@auth.route('/redirect')
def getAuthCode():
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type':'authorization_code',
        'code':request.args['code'], #session.get('access_token', None),
        'redirect_uri':REDIRECT_URI,
        'client_id':os.getenv('CLIENT_ID'),
        'client_secret':os.getenv('SECRET_KEY')
    } 
    token_response = requests.post(TOKEN_URL, data=data)

    session['token_data'] = token_response.json()
    
    return token_response.text


