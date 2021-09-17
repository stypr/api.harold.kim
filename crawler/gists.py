#!/usr/bin/python3
#-*- coding: utf-8 -*-
"""
gists.py

Crawler for Gists
"""
import os
import re
import requests
from dotenv import load_dotenv

# load envvars
load_dotenv()
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

def get_gists(username):
    """ (str, str) -> dict

    Crawl recent gists from user
    """
    r = requests.Session()
    url = f"https://api.github.com/users/{username}/gists"
    result = r.get(url).json()
    return result

def collect_data():
    """ collect data """
    result = get_gists(GITHUB_USERNAME)
    return result
