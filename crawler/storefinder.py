#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
storefinder.py

Cronjob for https://github.com/bemusicscript/gcm-storefinder
"""

import os
import hashlib

def commit_data(output_dir="./storefinder/"):
    """Updated updated assets into the server"""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir)
    _ = os.popen(f"git -C {output_dir} add {output_dir}/").read()
    curr_status = os.popen(f"git -C {output_dir} status").read()
    curr_status = os.popen(f"git -C {output_dir} status").read()
    if "Changes to be committed:" in curr_status:
        _ = os.popen(f"git -C {output_dir} commit -m \"JSON Update $(date '+%Y-%m-%d %H:%M:%S')\"").read()
    curr_status = os.popen(f"git -C {output_dir} status").read()
    if "Your branch is ahead of 'origin/master'" in curr_status:
        _ = os.popen(f"git -C {output_dir} push -f origin master").read()
    return True

def update_data(output_dir="./storefinder/"):
    """(str) -> dict

    Fetch data and optimize results
    """
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir)
    runner_hash = (
        "b2f88f979c834d11c6d87e57d36d0a97"
        + "8a51117d7a8a74121093860993e7ab1a"
        + "1901d479613254ea7b344bc9b8a98699"
        + "ac16ed4fed3b13290ed8d5f807a499c9"
    )

    _ = os.popen(
        f"git clone git@github.com:bemusicscript/gcm-storefinder.git {output_dir} 2>&1"
    ).read()

    if not os.path.exists(os.path.join(output_dir, "storemap.py")):
        return {"err": "File does not exist.."}

    with open(os.path.join(output_dir, "storemap.py"), "rb") as fp:
        if hashlib.sha512(fp.read()).hexdigest() != runner_hash:
            return {"err": "Hash mismatch!"}

    _ = os.popen(
        f"cd {output_dir}; python3 {os.path.join(output_dir, 'storemap.py')} 2>&1"
    ).read()

    return commit_data()

if __name__ == "__main__":
    print(update_data())
