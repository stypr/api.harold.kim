#!/usr/bin/python3
#-*- coding: utf-8 -*-
"""
server.py

Main application for the scheduler and the web server
"""

import os
import sys
import time
import json
import gevent.pywsgi
from flask import Flask
from flask_restful import Resource, Api
from apscheduler.schedulers.background import BackgroundScheduler
from crawler import sega, swarm, steam, gists, osu
from crawler.pjsekai_api import proseka
####### Scheduler #######

def run_update_task():
    """ Function for regular hourly updates.. """
    print("[*] Starting Scheduler..")

    # Collect github data
    try:
        _gists = gists.collect_data()
        f = open(os.path.join("data", "gists.json"), "wb")
        f.write(json.dumps(_gists).encode())
        f.close()
    except Exception as e:
        print("[*] Gists crashed")

    # Collect steam data
    try:
        _steam = steam.collect_data()
        f = open(os.path.join("data", "steam.json"), "wb")
        f.write(json.dumps(_steam).encode())
        f.close()
    except:
        print("[*] Steam crashed")

    # Collect swarm data
    try:
        _swarm = swarm.collect_data()
        _swarm['checkins']['items'] = _swarm['checkins']['items'][:3]
        f = open(os.path.join("data", "swarm.json"), "wb")
        f.write(json.dumps(_swarm).encode())
        f.close()
    except:
        print("[*] Swarm Crashed")

    try:
        # Collect SEGA data
        _sega = sega.collect_data()
        # print(_sega)
        if _sega['ongeki'] and _sega['chunithm'] and _sega['maimai']:
            f = open(os.path.join("data", "sega.json"), "wb")
            f.write(json.dumps(_sega).encode())
            f.close()
    except Exception as e:
        print("[*] SEGA Crashed", str(e))

    try:
        # Collect Proseka data
        _proseka = proseka.collect_data()
        if _proseka['user']['userGamedata']['name']:
            f = open(os.path.join("data", "proseka.json"), "wb")
            f.write(json.dumps(_proseka).encode())
            f.close()
    except Exception as e:
        print("[*] Proseka Crashed", str(e))

    try:
        # Collect osu!catch data
        _osu = osu.collect_data("4266189")
        if _osu['user'] and _osu['recent_play']:
            f = open(os.path.join("data", "osu.json"), "wb")
            f.write(json.dumps(_osu).encode())
            f.close()
    except Exception as e:
        print("[*] osu! Crashed", str(e))


    print("[*] Updated.")
    return True

def run_asset_task():
    """ Updating asset server """
    proseka.get_character_assets()
    proseka.get_database()
    proseka.update_asset_server()

sched = BackgroundScheduler(daemon=True)
sched.add_job(run_update_task, 'interval', hours=1, args=[])
sched.add_job(run_asset_task, 'interval', hours=3, args=[])
sched.start()

####### Web #######

app = Flask(__name__)
api = Api(app)

class Gists(Resource):
    """ /api/v1/gists: Get GitHub gists """
    def get(self):
        """ grabs the output from the scheduled task. """
        return json.loads(open(os.path.join("data", "gists.json"), "rb").read())

class Steam(Resource):
    """ /api/v1/steam: Get Steam Game Information """
    def get(self):
        """ grabs the output from the scheduled task. """
        return json.loads(open(os.path.join("data", "steam.json"), "rb").read())

class Sega(Resource):
    """ /api/v1/sega: Get SEGA Game Information """
    def get(self):
        """ grabs the output from the scheduled task. """
        return json.loads(open(os.path.join("data", "sega.json"), "rb").read())

class Swarm(Resource):
    """ /api/v1/swarm: Get recent location """
    def get(self):
        """ grabs the output from the scheduled task. """
        return json.loads(open(os.path.join("data", "swarm.json"), "rb").read())

class Proseka(Resource):
    """ /api/v1/proseka: Proseka Information """
    def get(self):
        """ grabs the output from the scheduled task. """
        return json.loads(open(os.path.join("data", "proseka.json"), "rb").read())

class Osu(Resource):
    """ /api/v1/proseka: Proseka Information """
    def get(self):
        """ grabs the output from the scheduled task. """
        return json.loads(open(os.path.join("data", "osu.json"), "rb").read())

api.add_resource(Gists, "/api/v1/gists")
api.add_resource(Steam, "/api/v1/steam")
api.add_resource(Swarm, "/api/v1/swarm")
api.add_resource(Sega, "/api/v1/sega")
api.add_resource(Proseka, "/api/v1/proseka")
api.add_resource(Osu, "/api/v1/osu")

@app.route("/")
def home():
    """ Function for test purposes. """
    return "api.harold.kim"

if __name__ == "__main__":
    if len(sys.argv) != 1:
        app.run(debug=True, port=3000, host='0.0.0.0')
    else:
        # run_update_task()
        # run_asset_task()
        app_server = gevent.pywsgi.WSGIServer(('localhost', 3000), app)
        app_server.serve_forever()
