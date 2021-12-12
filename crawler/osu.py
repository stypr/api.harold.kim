#!/usr/bin/python -u
#-*- coding: utf-8 -*-

"""
osu.py

Parse osu! profile (osu!catch)
"""

import os
import datetime
import requests

from dotenv import load_dotenv

# load envvars
load_dotenv()

OSU_URL = os.getenv("OSU_URL")
OSU_API_KEY = os.getenv("OSU_API_KEY")

def fetch_data(user_id):
    """ (str) -> dict

    Fetch data from osu! server
    """
    result = {}
    data = {
        "k": OSU_API_KEY,
        "u": user_id,
        "m": 2,
    }
    r = requests.post("https://osu.ppy.sh/api/get_user", data=data).json()[0]
    result['user'] = r
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.27 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-CN;q=0.5,zh;q=0.4",
        "cache-control": "no-cache",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }
    r = requests.get(f"https://osu.ppy.sh/users/{user_id}/scores/best?mode=fruits&offset=0&limit=100", headers=headers).json()
    result['recent_play'] = r
    return result

def collect_data(user_id="4266189"):
    """ (str) -> dict

    Fetch data and optimize results
    """
    r = fetch_data(user_id)
    r['recent_play'] = sorted(r['recent_play'], key=lambda x: datetime.datetime.strptime(x['created_at'], "%Y-%m-%dT%H:%M:%S+00:00").timestamp(), reverse=True)[:10]

    for i, _record in enumerate(r['recent_play']):
        r['recent_play'][i] = {
            'accuracy': round(_record['accuracy'] * 100, 2),
            'rank': _record['rank'],
            'pp': _record['pp'],
            'created_at': datetime.datetime.strptime(_record['created_at'], "%Y-%m-%dT%H:%M:%S+00:00").timestamp(),
            'beatmap_difficulty': _record['beatmap']['difficulty_rating'],
            'beatmap_level': _record['beatmap']['version'],
            'beatmap_artist': _record['beatmapset']['artist'],
            'beatmap_title': _record['beatmapset']['title_unicode'],
        }

    return r

def verify_data(data):
    """ Verify data """
    return data['user'] and data['recent_play']

if __name__ == "__main__":
    uid = "4266189"
    print(collect_data(uid))

