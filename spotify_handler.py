import os, requests, json, datetime, base64
from werkzeug.utils import redirect

from flask import Blueprint, request


handler_blueprint = Blueprint('handler_bp',__name__)


class SpotifyHandler(object):
    
    def __init__(self):
        self.CLIENT_ID = os.environ.get('CLIENT_ID', None)
        self.SECRET_KEY = os.environ.get('SECRET_KEY', None)
        self.SCOPES = ['user-read-recently-played','playlist-modify-private']
        self.ACCESS_TOKEN = None
        self.REFRESH_TOKEN = None
        self.TOKEN_TIMESTAMP = None
        self.EXPIRES_IN = None
        self.BASE_URL = 'https://api.spotify.com/v1'
        self.auth = SpotifyAuthenticator()
 
    def requestAuth(self):
        """
        Function that asks for initial user auth and then redirects to whitelisted URL.
        """
        AUTH_URL = self.BASE_AUTH_URL + 'authorize'
        params = {
            'client_id':self.CLIENT_ID,
            'response_type':'code',
            'redirect_uri':self.REDIRECT_URL,
            'scope': ' '.join(self.SCOPES)
        }

        requests.get(AUTH_URL, params=params, allow_redirects=True)
        return redirect('/callback')

    @handler_blueprint.route('/callback')
    def accessCallback(self):
        """
        Triggered by requestAuth method, it automatically return the ACCESS_TOKEN.
        """
        TOKEN_URL =  self.BASE_AUTH_URL + 'api/token'
        
        data = {
            'grant_type':'authorization_code',
            'code':request.args['code'],
            'redirect_uri':self.REDIRECT_URL,
            'client_id':os.getenv('CLIENT_ID'),
            'client_secret':os.getenv('SECRET_KEY')
        } 

        token_response = requests.post(TOKEN_URL, data=data)
        token_json = json.loads(token_response.text)
        
        self.ACCESS_TOKEN = token_json['access_token']
        self.EXPIRES_IN = token_json['expires_in']
        self.REFRESH_TOKEN = token_json['refresh_token']
        self.TOKEN_TIMESTAMP = datetime.utcnow()
        
        return self.ACCESS_TOKEN

    @handler_blueprint.route('/access')
    def getAccessToken(self):
        """
        Decision tree function that will always return an ACCESS_TOKEN, either by requesting it as a first time or by refreshing it.
        """
        if self.ACCESS_TOKEN == None:
            return self.requestAuth()
        else:
            requiresRefresh = self.TOKEN_TIMESTAMP + datetime.timedelta(seconds=3600)
            if requiresRefresh < datetime.utcnow():
                return self.ACCESS_TOKEN
            else:
                _encodedSecrets = f'{self.CLIENT_ID}:{self.SECRET_KEY}'.encode('ascii')
                encodedSecrets_bytes = base64.b64encode(_encodedSecrets)
                header = {
                    'Authorization': 'Basic ' + encodedSecrets_bytes
                }
                params = {
                    'grant_type': 'refresh_token',
                    'refresh_token': self.REFRESH_TOKEN
                }

                token_response = requests.post(self.BASE_AUTH_URL + 'api/token', params=params, headers=header)
                token_json = json.loads(token_response.text)
                
                self.ACCESS_TOKEN = token_json['access_token']
                self.EXPIRES_IN = token_json['expires_in']
                self.REFRESH_TOKEN = token_json['refresh_token']
                self.TOKEN_TIMESTAMP = datetime.utcnow()

                return self.ACCESS_TOKEN



    def call_api(self, endpoint, params=None, payload=None):
        """
        Calls Spotify API with ACCESS_TOKEN, return JSON object for analysis.
        """
        call_url = self.BASE_URL + endpoint
        
        header = {
            'Authorization': 'Bearer {}'.format(self.auth.getAccessToken),
            'Accept':'application/json',
            'Content-Type': 'application/json'
        }
     
        response = requests.get(call_url, headers=header, data=payload, params=params)
        return json.loads(response.text)

