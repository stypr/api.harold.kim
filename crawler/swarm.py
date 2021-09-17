#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
swarm.py

FourSquare Swarm API

"""
import os
import json
import foursquare
from dotenv import load_dotenv

# load envvars
load_dotenv()
SWARM_ACCESS_TOKEN = os.getenv("SWARM_ACCESS_TOKEN")

def generate_auth_url(client_id, client_secret, redirect_uri):
    """ (str, str, str) -> str
    generates auth URL for generating access token
    """
    client = foursquare.Foursquare(
        client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri
    )
    auth_uri = client.oauth.auth_url()
    return auth_uri


def get_my_access_token(client_id, client_secret, redirect_uri, oauth_token):
    """ (str, str, str, str) -> str
    generates accesstoken based on the given oauth token
    """
    client = foursquare.Foursquare(
        client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri
    )
    access_token = client.oauth.get_token(oauth_token)
    client.set_access_token(access_token)
    # user = client.users()
    return access_token


def get_my_checkin(access_token):
    """
    Get my checkin based on the given access token
    """
    client = foursquare.Foursquare(access_token=access_token)
    return client.users.checkins()

def collect_data():
    return get_my_checkin(SWARM_ACCESS_TOKEN)

if __name__ == "__main__":
    f = open("track.json", "w")
    f.write(json.dumps(get_my_checkin(SWARM_ACCESS_TOKEN)))
    f.close()
