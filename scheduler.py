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

from apscheduler.schedulers.blocking import BlockingScheduler # BackgroundScheduler
from crawler import sega, swarm, steam, gists, osu
from crawler import storefinder
from crawler.pjsekai_api import proseka

####### Scheduler #######
def run_update_task():
    """ Function for regular hourly updates.. """
    print("[*] Starting Scheduler..")

    list_crawler = [sega, swarm, steam, gists, osu]
    for crawler in list_crawler:
        try:
            crawler_name = crawler.__name__.split(".")[-1]
            crawler_result = crawler.collect_data()

            if crawler.verify_data(crawler_result):
                f = open(os.path.join("data", f"{crawler_name}.json"), "wb")
                f.write(json.dumps(crawler_result).encode())
                f.close()
                print(f"[.] {crawler_name} Success!")
            else:
                print(f"[*] {crawler_name} Failed..")
        except Exception as e:
            print(f"[*] {crawler_name} Crashed..: {str(e)}")

    print("[+] Updated.")
    return True

def run_asset_task():
    """ Updating asset server """
    proseka.get_character_assets()
    proseka.get_database()
    proseka.update_asset_server()

def run_weekly_task():
    """ Run daily tasks """
    storefinder.update_data()


if __name__ == "__main__":
    sched = BlockingScheduler(timezone='Asia/Tokyo', daemon=True)
    sched.add_job(run_update_task, 'interval', hours=1, args=[])
    sched.add_job(run_asset_task, 'interval', hours=3, args=[])
    sched.add_job(run_weekly_task, 'cron', day_of_week='mon', hour=16, minute=00, args=[])
    print("[-] Scheduler Started!")
    sched.start()
    print("[-] Scheduler Stopped!")
