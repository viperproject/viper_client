#!/usr/local/bin/python3

import sys
import argparse
import os.path
from pathlib import Path
import requests
import json

backends = ["silicon", "carbon"]
command = ["verify", "terminate"]

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--command",
    help="Specify the command for the server.",
    choices=command,
    default="verify")

parser.add_argument(
    "-p", "--port",
    help="Specify the port lestened by ViperServer.",
    type=int,
    required=True)

parser.add_argument(
    "-f", "--file",
    help="File to verify. Must be a Viper program.",
    required=True)

parser.add_argument(
    "-v", "--verifier",
    help="Specify which verification backend to use.",
    choices=backends,
    required=True)

parser.add_argument(
    "-x", "--options",
    default="",
    help="Pass an options string to the verifier.")

args = parser.parse_args()

if args.command == "terminate":
    r = requests.get("http://localhost:" + str(args.port) + "/exit")
    print(r.text)
    sys.exit(0)

if not Path(args.file).is_file():
    print("File `" + args.file + "` does not exist.")
    sys.exit(1)

headers = {'Content-Type': 'application/json'}
req = {'arg': args.verifier + ' ' + args.options + ' ' + args.file}

r = requests.post("http://localhost:" + str(args.port) + "/verify",
                  data=json.dumps(req),
                  headers=headers,
                  timeout=5)

print(r.text)

r = requests.get("http://localhost:" + str(args.port) + "/verify/" + str(r.json()["id"]),
                 timeout=500)

print(r.text)
