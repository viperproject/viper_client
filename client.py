#!/usr/bin/env python3

import sys
import argparse
import os.path
from pathlib import Path
import requests
import json
import platform

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
    default="__empty_viper_file__.vpr")

parser.add_argument(
    "-v", "--verifier",
    help="Specify which verification backend to use.",
    #choices=backends, -- we might need to use custom backends
    #default="silicon"
    )

parser.add_argument(
    "-x", "--options",
    default=( "--disableCaching  --z3Exe=/usr/local/Viper/z3/bin/z3" if not platform.system()=="Windows" else
              "--disableCaching '--z3Exe=C:\\Program Files\\Viper\\z3\\bin\\z3.exe'"),
    help="Pass an options string to the verifier.")

args = parser.parse_args()

if args.command == "terminate":
    r = requests.get("http://localhost:" + str(args.port) + "/exit")
    print(r.text)
    sys.exit(0)

if not Path(args.file).is_file():
    print("File `" + args.file + "` does not exist.")
    sys.exit(1)

if args.verifier is None:
    print("[viper_client] Using default verification backend (silicon). Reason: option -v is not provided.")
    verification_backend = "silicon"
else:
    verification_backend = args.verifier

if parser.get_default("file") == args.file:
    print("[viper_client] Testing ViperClient with an empty Viper file. Reason: no file is specified via option -f.")

if parser.get_default("options") == args.options:
    if verification_backend != "carbon":
        print("[viper_client] Default backend options set to: \n   " + args.options +
              "\n   (Override with -x)")
    else:
        default_carbon_options=( "  --boogieExe=/usr/local/Viper/boogie/Binaries/Boogie" if platform.system()=="Darwin" else
                                 " '--boogieExe=C:\\Program Files\\Viper\\boogie\\Binaries\\Boogie.exe'")
        print("[viper_client] Default backend options (for carbon) set to: \n" +
              "[viper_client]   " + args.options + default_carbon_options + "\n" +
              "[viper_client]   (Override with -x)")
        args.options += default_carbon_options

headers = {'Content-Type': 'application/json'}
req = {'arg': verification_backend + ' ' + args.options + ' ' +
       '"' + os.path.abspath(args.file) + '"'}

r = requests.post("http://localhost:" + str(args.port) + "/verify",
                  data=json.dumps(req),
                  headers=headers,
                  timeout=5)

print(r.text)

#r = requests.get("http://localhost:" + str(args.port) + "/exit",
#                 stream=True)

#r = requests.get("http://localhost:" + str(args.port) + "/discard/" +
#                 str(r.json()["id"]),
#                 stream=True)

r = requests.get("http://localhost:" + str(args.port) + "/verify/" +
                 str(r.json()["id"]),
                 stream=True)

for line in r.iter_lines():
    if line:
        print(json.dumps(json.loads(line.decode("utf-8")), indent=2))
