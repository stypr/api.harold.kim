#!/usr/bin/python3
#-*- coding: utf-8 -*-
"""
server.py

Main application for the scheduler and the web server
"""

import os
import sys
import json
import uvicorn
from fastapi import FastAPI, APIRouter

app = FastAPI()
api = APIRouter(prefix="/api/v1", tags=["api"])

@api.get("/{name}")
async def fetch_json(name):
    """ grabs the output from the scheduled task. """
    return (
        json.loads(open(os.path.join("data", f"{name}.json"), "rb").read())
        if name.isalpha() and name.islower() else []
    )

app.include_router(api)

@app.get("/")
async def root():
    """ Function for test purposes. """
    return {"message": "api.harold.kim"}

if __name__ == "__main__":
    if len(sys.argv) != 1:
        uvicorn.run(app, host="0.0.0.0", port=4000, loglevel="debug")
    else:
        uvicorn.run("server:app", port=3000)
