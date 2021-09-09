#!/usr/bin/python3
#-*- coding: utf-8 -*-
"""
server.py

Main application for the scheduler and the web server
"""

import os
import time
import json
from flask import Flask
from flask_restful import Resource, Api
from apscheduler.schedulers.background import BackgroundScheduler
from crawler import sega, swarm

####### Scheduler #######

def run_task():
    """ Function for test purposes. """
    exit(0)
    print("[*] Starting Scheduler..")

    # Collect swarm data
    _swarm = swarm.collect_data()
    _swarm['checkins']['items'] = _swarm['checkins']['items'][:5]
    f = open(os.path.join("data", "swarm.json"), "wb")
    f.write(json.dumps(_swarm).encode())
    f.close()

    # Collect SEGA data
    _sega = sega.collect_data()
    f = open(os.path.join("data", "sega.json"), "wb")
    f.write(json.dumps(_sega).encode())
    f.close()

    print("[*] Updated.")
    return True

sched = BackgroundScheduler(daemon=True)
sched.add_job(run_task, 'interval', hours=1, args=[])
sched.start()

####### Web #######

app = Flask(__name__)
api = Api(app)

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

api.add_resource(Swarm, "/api/v1/swarm")
api.add_resource(Sega, "/api/v1/sega")

@app.route("/")
def home():
    """ Function for test purposes. """
    return "hello"

if __name__ == "__main__":
    app.run(debug=False, port=5000, host='0.0.0.0')
