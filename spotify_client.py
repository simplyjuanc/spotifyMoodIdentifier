import base64
import datetime
import json
import os

from flask import request
import requests
from urllib.parse import quote, urlencode

class SpotifyClient(object):
    
    def __init__(self):
        self.BASE_URL = 'https://api.spotify.com/v1'
        self.BASE_AUTH_URL = 'https://accounts.spotify.com/'
        self.CLIENT_URL = 'http://127.0.0.1:5000'
        self.REDIRECT_URL = self.CLIENT_URL + '/callback'
        
        self.CLIENT_ID = os.environ.get('CLIENT_ID', None)
        self.SECRET_KEY = os.environ.get('SECRET_KEY', None)
        self.SCOPES = ['user-read-recently-played','playlist-modify-private']
        
        self.ACCESS_TOKEN = None
        self.REFRESH_TOKEN = None
        self.TOKEN_TIMESTAMP = None
        self.EXPIRES_IN = None
 
    def generateAuthUrl(self):
        """
        Function that asks for initial user auth and then redirects to whitelisted URL.
        """
        AUTH_URL = self.BASE_AUTH_URL + 'authorize'
        params = {
            'client_id':self.CLIENT_ID,
            'response_type':'code',
            'redirect_uri':self.REDIRECT_URL,
            'scope': '%20'.join(self.SCOPES)
        }
        
        query_params = '&'.join([f"{key}={str(value)}" for key, value in params.items()])
        
        return AUTH_URL + '/?' + query_params

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
        self.TOKEN_TIMESTAMP = datetime.datetime.utcnow()
        
        return dict(token_json)

    def getAccessToken(self):
        """
        Decision tree function that will always return an ACCESS_TOKEN, either by requesting it as a first time or by refreshing it.
        """
        if self.ACCESS_TOKEN == None:
            return self.accessCallback()
        else:
            requiresRefresh = self.TOKEN_TIMESTAMP + datetime.timedelta(seconds=3600)
            if requiresRefresh < datetime.datetime.utcnow():
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


    def call_api(self, endpoint, method='GET', params=None, payload=None):
        """
        Calls Spotify API with ACCESS_TOKEN, return JSON object for analysis.
        """
        call_url = self.BASE_URL + endpoint
        access_token = self.getAccessToken()
        print(access_token)

        header = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Accept':'application/json',
            'Content-Type': 'application/json'
        }

        if method == 'GET':
           response = requests.get(call_url, headers=header, data=payload, params=params)
        elif method == 'POST':
            response = requests.post(call_url, headers=header, data=payload, params=params)
        else:
            print('Please use either GET or POST methods.')
        
        return dict(json.loads(response.text))
