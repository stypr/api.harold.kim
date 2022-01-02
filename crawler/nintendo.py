#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
nintendo.py

Nintendo API

Some of codes were derived from
  - https://github.com/frozenpandaman/splatnet2statink/blob/master/iksm.py
  - https://gitlab.com/solidtux-rust/switch-api
"""
import os
import re
import sys
import json
import uuid
import time
import requests
import base64
import hashlib

from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup

# load envvars
load_dotenv()

NINTENDO_TOKEN = os.getenv("NINTENDO_TOKEN")
NINTENDO_USER_ID = os.getenv("NINTENDO_USER_ID")
NINTENDO_DEVICE_ID = os.getenv("NINTENDO_DEVICE_ID")
NINTENDO_CLIENT_ID = os.getenv("NINTENDO_CLIENT_ID")
"""
For normal clients

NINTENDO_CLIENT_ID = "71b963c1b7b6d119"
NINTENDO_CLIENT_SCOPE = "openid user user.birthday user.mii user.screenName"
"""
# client info
NINTENDO_CLIENT_SCOPE = "openid user user.mii moonUser:administration moonDevice:create moonOwnedDevice:administration moonParentalControlSetting moonParentalControlSetting:update moonParentalControlSettingState moonPairingState moonSmartDevice:administration moonDailySummary moonMonthlySummary"
NINTENDO_NSO_VERSION = "1.14.0"
NINTENDO_PCTL_VERSION = "1.16.0"
NINTENDO_PCTL_VERSION_BUILD = "310"

"""
For normal Splatoon clients

NINTENDO_CLIENT_ID = "71b963c1b7b6d119"
NINTENDO_CLIENT_SCOPE = "openid user user.birthday user.mii user.screenName"
"""


session = requests.Session()

def get_nsoapp_version():
    """Fetches the current Nintendo Switch Online app version from the Google Play Store."""
    global NINTENDO_NSO_VERSION
    try:
        page = requests.get("https://play.google.com/store/apps/details?id=com.nintendo.znca&hl=en")
        soup = BeautifulSoup(page.text, "html.parser")
        elts = soup.find_all("span", {"class": "htlgb"})
        ver = elts[7].get_text().strip()
        return ver
    except:
        return NINTENDO_NSO_VERSION


def get_session_token():
    """Logs in to a Nintendo Account and returns a session_token."""
    auth_state = base64.urlsafe_b64encode(os.urandom(36))
    auth_code_verifier = base64.urlsafe_b64encode(os.urandom(32))
    auth_cv_hash = hashlib.sha256()
    auth_cv_hash.update(auth_code_verifier.replace(b"=", b""))
    auth_code_challenge = base64.urlsafe_b64encode(auth_cv_hash.digest())

    headers = {
        "Host": "accounts.nintendo.com",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8n",
        "DNT": "1",
        "Accept-Encoding": "gzip,deflate,br",
    }
    data = {
        "state": auth_state,
        "redirect_uri": f"npf{NINTENDO_CLIENT_ID}://auth",
        "client_id": NINTENDO_CLIENT_ID,
        "scope": NINTENDO_CLIENT_SCOPE,
        "response_type": "session_token_code",
        "session_token_code_challenge": auth_code_challenge.replace(b"=", b""),
        "session_token_code_challenge_method": "S256",
        "theme": "login_form",
    }
    url = "https://accounts.nintendo.com/connect/1.0.0/authorize"
    r = session.get(url, headers=headers, params=data)

    post_login = r.history[0].url
    print("Navigate to this URL in your browser:")
    print(post_login)
    print('Paste URL:')

    while True:
        try:
            use_account_url = input("")
            if use_account_url == "skip":
                return "skip"
            session_token_code = re.search("de=(.*)&", use_account_url)
            return get_session_token(session_token_code.group(1), auth_code_verifier)
        except KeyboardInterrupt:
            print("\nBye!")
            sys.exit(1)
        except AttributeError:
            print("Malformed URL. Please try again, or press Ctrl+C to exit.")
            print("URL:", end=" ")
        except KeyError:
            # session_token not found
            print("URL expired :( Try again.")
            sys.exit(1)


def get_session_token(session_token_code, auth_code_verifier):
    """Helper function for log_in()."""
    headers = {
        "User-Agent": "OnlineLounge/" + NINTENDO_NSO_VERSION + " NASDKAPI Android",
        "Accept-Language": "en-US",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "accounts.nintendo.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }
    data = {
        "client_id": NINTENDO_CLIENT_ID,
        "session_token_code": session_token_code,
        "session_token_code_verifier": auth_code_verifier.replace(b"=", b""),
    }
    url = "https://accounts.nintendo.com/connect/1.0.0/api/session_token"
    r = session.post(url, headers=headers, data=data)
    return r.json()["session_token"]


def get_access_token(session_token):
    """get access and id token"""
    timestamp = int(time.time())
    guid = str(uuid.uuid4())

    headers = {
        "Host": "accounts.nintendo.com",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Language": "en-US",
        "Accept": "application/json",
        "Connection": "Keep-Alive",
        "User-Agent": "OnlineLounge/" + NINTENDO_NSO_VERSION + " NASDKAPI Android",
    }
    data = {
        "client_id": NINTENDO_CLIENT_ID,
        "session_token": session_token,
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
    }
    url = "https://accounts.nintendo.com/connect/1.0.0/api/token"
    r = requests.post(url, headers=headers, json=data)
    return r.json()


def me(session_token):
    """ Returns a new cookie provided the session_token. """
    id_response = get_access_token(session_token)

    # get user info
    try:
        headers = {
            "User-Agent": "OnlineLounge/" + NINTENDO_NSO_VERSION + " NASDKAPI Android",
            "Accept-Language": "en-US",
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(id_response["access_token"]),
            "Host": "api.accounts.nintendo.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }
    except:
        print("Error from Nintendo (in api/token step):")
        print(json.dumps(id_response, indent=2))
        sys.exit(1)

    url = "https://api.accounts.nintendo.com/2.0.0/users/me"
    r = requests.get(url, headers=headers)
    user_info = json.loads(r.text)
    nickname = user_info["nickname"]
    return user_info


def get_device_list(session_token):
    id_response = get_access_token(session_token)
    user_id = NINTENDO_USER_ID
    # get devices_info
    try:
        headers = {
            "Authorization": "Bearer {}".format(id_response["access_token"]),
            "X-Moon-App-Id": "com.nintendo.znma",
            "X-Moon-Os": "IOS",
            "X-Moon-TimeZone": "Asia/Tokyo",
            "X-Moon-Os-Language": "en-US",
            "X-Moon-App-Language": "en-US",
            "X-Moon-App-Display-Version": NINTENDO_PCTL_VERSION,
            "X-Moon-App-Internal-Version": NINTENDO_PCTL_VERSION_BUILD,
            "User-Agent": f"moon_ios/{NINTENDO_PCTL_VERSION} (com.nintendo.znma; build:{NINTENDO_PCTL_VERSION_BUILD}; iOS 15.1.0) Alamofire/{NINTENDO_PCTL_VERSION}",
            "Accept-Language": "en-US",
            "Accept": "application/json",
            "Host": "api-lp1.pctl.srv.nintendo.net",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }
    except:
        print("Error from Nintendo (in api/token step):")
        print(json.dumps(id_response, indent=2))
        sys.exit(1)

    url = f"https://api-lp1.pctl.srv.nintendo.net/moon/v1/users/{user_id}/devices?filter.device.activated.$eq=true"
    # print(url)
    r = requests.get(url, headers=headers)
    device_list = r.json()
    return device_list

def get_daily_summary(session_token):
    id_response = get_access_token(session_token)
    device_id = NINTENDO_DEVICE_ID

    # get daily summary
    try:
        headers = {
            "Authorization": "Bearer {}".format(id_response["access_token"]),
            "X-Moon-App-Id": "com.nintendo.znma",
            "X-Moon-Os": "IOS",
            "X-Moon-TimeZone": "Asia/Tokyo",
            "X-Moon-Os-Language": "en-US",
            "X-Moon-App-Language": "en-US",
            "X-Moon-App-Display-Version": NINTENDO_PCTL_VERSION,
            "X-Moon-App-Internal-Version": NINTENDO_PCTL_VERSION_BUILD,
            "User-Agent": f"moon_ios/{NINTENDO_PCTL_VERSION} (com.nintendo.znma; build:{NINTENDO_PCTL_VERSION_BUILD}; iOS 15.1.0) Alamofire/{NINTENDO_PCTL_VERSION}",
            "Accept-Language": "en-US",
            "Accept": "application/json",
            "Host": "api-lp1.pctl.srv.nintendo.net",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }
    except:
        print("Error from Nintendo (in api/token step):")
        print(json.dumps(id_response, indent=2))
        sys.exit(1)

    url = f"https://api-lp1.pctl.srv.nintendo.net/moon/v1/devices/{device_id}/daily_summaries"
    r = requests.get(url, headers=headers)
    device_list = r.json()
    return device_list

def get_monthly_summary(session_token, month=datetime.now().month):
    id_response = get_access_token(session_token)
    device_id = NINTENDO_DEVICE_ID

    # get monthly summary
    try:
        headers = {
            "Authorization": "Bearer {}".format(id_response["access_token"]),
            "X-Moon-App-Id": "com.nintendo.znma",
            "X-Moon-Os": "IOS",
            "X-Moon-TimeZone": "Asia/Tokyo",
            "X-Moon-Os-Language": "en-US",
            "X-Moon-App-Language": "en-US",
            "X-Moon-App-Display-Version": NINTENDO_PCTL_VERSION,
            "X-Moon-App-Internal-Version": NINTENDO_PCTL_VERSION_BUILD,
            "User-Agent": f"moon_ios/{NINTENDO_PCTL_VERSION} (com.nintendo.znma; build:{NINTENDO_PCTL_VERSION_BUILD}; iOS 15.1.0) Alamofire/{NINTENDO_PCTL_VERSION}",
            "Accept-Language": "en-US",
            "Accept": "application/json",
            "Host": "api-lp1.pctl.srv.nintendo.net",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }
    except:
        print("Error from Nintendo (in api/token step):")
        print(json.dumps(id_response, indent=2))
        sys.exit(1)

    url = f"https://api-lp1.pctl.srv.nintendo.net/moon/v1/devices/{device_id}/daily_summaries"
    r = requests.get(url, headers=headers)
    device_list = r.json()
    return device_list

def get_monthly_playlog():
    """ get playlog of the current month """
    result = {}
    monthly_summary = get_monthly_summary(NINTENDO_TOKEN)

    for playlog in monthly_summary['items']:

        # Gather game list
        for app_info in playlog['playedApps']:
            if not result.get(app_info['applicationId'], None):
                result[app_info['applicationId']] = {
                    "image": app_info['imageUri']['medium'],
                    "title": app_info['title'],
                    "playtime": 0,
                }

        # Gather anonymous player info
        if playlog["anonymousPlayer"]:
            for game_info in playlog["anonymousPlayer"].get("playedApps", []):
                result[game_info['applicationId']]['playtime'] += game_info['playingTime']

        # Gather existing user info
        for user_info in playlog.get("devicePlayers", {}):
            for game_info in user_info.get('playedApps', []):
                result[game_info['applicationId']]['playtime'] += game_info['playingTime']

    return result

def collect_data():
    result = get_monthly_playlog()
    return result

def verify_data(data):
    """ Verify data """
    return True

if __name__ == "__main__":
    if not NINTENDO_TOKEN:
        NINTENDO_TOKEN = get_session_token()
        print("NINTENDO_TOKEN =", NINTENDO_TOKEN)

    if not NINTENDO_USER_ID:
        NINTENDO_USER_ID = me(NINTENDO_TOKEN)['id']
        print("NINTENDO_USER_ID =", NINTENDO_USER_ID)

    if not NINTENDO_DEVICE_ID:
        NINTENDO_DEVICE_ID = get_device_list(NINTENDO_TOKEN)['items'][0]['deviceId']
        print("NINTENDO_DEVICE_ID =", NINTENDO_DEVICE_ID)

    f = open("nintendo.json", "w")
    f.write(json.dumps(get_monthly_playlog()))
    f.close()
