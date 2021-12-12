#!/usr/bin/python3
#-*- coding: utf-8 -*-
"""
steam.py

Crawler for Steam
"""
import os
import requests
from dotenv import load_dotenv

# load envvars
load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_ID = os.getenv("STEAM_ID")

def get_recent_playdata(steam_api_key, steam_id):
    """ (str, str) -> dict

    Crawl recent playdata from Steam Server
    """
    r = requests.Session()

    # get token from login
    url = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001"
    param = f"?key={steam_api_key}&format=json&steamid={steam_id}&count=10"
    result = r.get(f"{url}/{param}").json()
    return result

def collect_data():
    """ collect data """
    result = {}
    result = get_recent_playdata(STEAM_API_KEY, STEAM_ID)
    return result

def verify_data(data):
    """ Verify data """
    return True

