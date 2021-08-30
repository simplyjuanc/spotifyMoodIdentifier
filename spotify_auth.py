import os
import json, requests
from flask.helpers import url_for
from flask import Blueprint, redirect
from requests.api import request

from spotify_client import SpotifyClient

auth_bp = Blueprint('auth_bp', __name__)

client = SpotifyClient()



@auth_bp.route('/login')
def requestAuth():
    """
    Function that asks for initial user auth and then redirects to whitelisted URL.
    """
    auth_url = client.generateAuthUrl()
    # if client.ACCESS_TOKEN == None:
    #     requests.get(auth_url)
    print(auth_url)
    return redirect(auth_url)


@auth_bp.route('/callback')
def redirectForToken():
    client.getAccessToken()
    return client.getAccessToken
