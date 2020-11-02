import os
import subprocess
import logging
from sys import exit
from log import Logger
from platform import system

logging.setLoggerClass(Logger)
log = logging.getLogger("Aerial Main")


## Clear Screen
def clear():
    if system() == "Windows":
        os.system("cls")
    else: # Linux + Mac
        os.system("clear")


clear()

## Requirements
log.info(f"Updating Packages...")
subprocess.check_call(["pip3", "install", "-U", "pip", "fortnitepy", "pyyaml"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import fortnitepy
from fortnitepy.ext import commands
import yaml

config = yaml.safe_load(open("config.yml", "r"))

## Device Auth Functions

def get_details(name: str) -> dict:
    details = {}
    data = config.get(name, {})
    details["email"] = data.get("Email", "")

    if data.get("Account ID", "") == "automagically-filled":
        return details # Only return email if nothing else is present

    details["account_id"] = data.get("Account ID", "")
    details["device_id"] = data.get("Device ID", "")
    details["secret"] = data.get("Secret", "")
    return details # Return saved details


## Loading Clients
clients = {}
for client in config:
    clients[client] = commands.Bot(
        command_prefix="",
        auth=fortnitepy.AdvancedAuth(
            prompt_authorization_code=True,
            **get_details(client)
        )
    )
log.info(f"Loaded {len(config)} Clients.")

## Loading Extensions
for ext in os.listdir("extensions"):
    if ext.endswith(".py"): # Simple Extensions
        try:
            for client in list(clients.values()):
                client.load_extension(f"extensions.{ext[:-3]}")
            log.info(f"$GREENLoaded Extension $CYAN{ext[:-3]}$GREEN.")
        except:
            log.warning(f"Cannot Load Extension $CYAN{ext}$YELLOW.")

    elif os.path.isdir(f"extensions/{ext}") and os.path.isfile(f"extensions/{ext}/main.py"):
        if os.path.isfile(f"extensions/{ext}/requirements.txt"):
            subprocess.check_call(["pip3", "install", "-U", "-r", f"extensions/{ext}/requirements.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        #try:
        for client in list(clients.values()):
            client.load_extension(f"extensions.{ext}.main")
        log.info(f"$GREENLoaded Extension $CYAN{ext}$GREEN.")
        #except:
        #    log.warning(f"Cannot Load Extension $CYAN{ext}$YELLOW.")

## Starting Clients
fortnitepy.run_multiple(list(clients.values()))
