#!/usr/bin/env python
import robobrowser
import re
from datetime import datetime, timezone

GAME_CLASSES = {
    "teamsList__game teamsList__game--post",
    "teamsList__game teamsList__game--pre",
    "teamsList__game teamsList__game--live",
    }

TEAM_CODES = {
    "BRI" : "Brisbane Broncos",
    "CAN" : "Canberra Raiders",
    "CBY" : "Canterbury Bankstown Bulldogs",
    "CRO" : "Cronulla Sharks",
    "GLD" : "Gold Coast Titans",
    "MAN" : "Manly Warringbah Sea Eagles",
    "MEL" : "Melbourne Storm",
    "NEW" : "Newcastle Knights",
    "NQL" : "North Queensland Cowboys",
    "PAR" : "Parramatta Eels",
    "PEN" : "Penrith Panthers",
    "SOU" : "South Sydney Rabbitohs",
    "STI" : "St George Illawarra Dragons",
    "SYD" : "Sydney Roosters",
    "WAR" : "New Zealand Warriors",
    "WST" : "Wests Tigers"
}

NRL = "http://www.nrl.com/"

def printDetails(matchcode, stadium, time, calendar):
    local = time.replace(tzinfo=timezone.utc).astimezone(tz=None)

    print('**' + TEAM_CODES[matchcode[:3]] + '** Vs. **' + TEAM_CODES[matchcode[4:]] + '**\n')
    print('**Location**: ' + "[" + stadium.text + "](" + stadium['href'] + ")\n")
    print('**Start Time**: ' + local.strftime('%H:%M - %d-%m-%Y') + "\n")
    print("[Add game to calendar](" + calendar + ")\n")

browser = robobrowser.RoboBrowser(history=True, parser="html.parser")

browser.open(NRL)
browser.open(NRL + browser.find('a', href=True, text=re.compile("Team Lists"))['href'])

for status in GAME_CLASSES:
    for game in browser.find_all('div', class_=status):
        matchcode = game['matchcode']
        details = game.find('h2', class_="teamsList__timeLocation")
        stadium = details.find('a', href=True, target="_blank")
        time = datetime.strptime(details.find('span', class_="localTime")['utc'], "%Y-%m-%dT%H:%M:%SZ")
        calendar = NRL + game.find('a', href=True, text=re.compile("Add"))['href']
        printDetails(matchcode, stadium, time, calendar)

