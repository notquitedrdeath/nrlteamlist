#/usr/bin/env python
import robobrowser
from bs4 import BeautifulSoup, element
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

SIDES = ["home", "away"]

NRL = "http://www.nrl.com/"

def buildTeamList(teamlist_html):
    teamlist = list()
    for position_html in teamlist_html.find_all("li"):
        position = dict()
        position["name"] = position_html.find("span", class_="teamsList__position").text
        if position["name"] == "\xa0":
            position["name"] = ""
        for side in SIDES:
            try:
                player = position_html.find("span", class_="teamsList__%sPlayer" % side).a.text
            except AttributeError:
                player = ""
            number = position_html.find("span", class_="teamsList__positionId teamsList__positionId--%s" % side).text
            if number == "\xa0":
                number = ""
            position[side] = (number, player)
        teamlist.append(position)
    return teamlist

# Post Creation Functions
def gameDetails(matchcode, stadium, time, calendar):
    local = time.replace(tzinfo=timezone.utc).astimezone(tz=None)
    
    details = "**%s** Vs. **%s**\n\n" % (TEAM_CODES[matchcode[:3]], TEAM_CODES[matchcode[4:]])
    if isinstance(stadium, element.Tag):
        details += "**Location**: [%s](%s)\n\n" % (stadium.text, stadium['href'])
    else:
        details += "**Location**: %s\n\n" % stadium
    details += "**StartTime**: %s\n\n" % local.strftime("%H:%M - %d/%m/%Y")
    details += "[Add game to calendar](%s)\n\n" % calendar 

    return details

def teamHeader(matchcode):
    header = " %s | Number | Position | Number | %s\n" % (TEAM_CODES[matchcode[:3]], TEAM_CODES[matchcode[4:]])
    header += ":---------|:-----------:|:-----------:|:-----------:|-----------:\n"

    return header

def teamList(team):
    table = ""
    for position in team:
        name = position["name"]
        home = position["home"]
        away = position["away"]
        table += "| %s | %s | %s | %s | %s |\n" % (home[1], home[0], name, away[0], away[1])

    return table

# Main Function
if __name__ == "__main__":
    browser = robobrowser.RoboBrowser(history=True, parser="html.parser")
    browser.open(NRL)
    browser.open(NRL + browser.find("a", href=True, text=re.compile("Team Lists"))["href"])
    #browser = BeautifulSoup(open("backup.html").read())

    for status in GAME_CLASSES:
        for game_html in browser.find_all("div", class_=status):
                # Game Location/Time
            matchcode = game_html["matchcode"]
            details = game_html.find("h2", class_="teamsList__timeLocation")
            stadium = details.find("a", href=True, target="_blank")
            if not stadium:
                print("Didn't find a stadium link, checking for venuename")
                stadium = details["venuename"]
            time = datetime.strptime(details.find("span", class_="localTime")["utc"], "%Y-%m-%dT%H:%M:%SZ")
            calendar = NRL + game_html.find("a", href=True, text=re.compile("Add"))["href"]

            # Players
            teamlist = game_html.find("div", class_="teamsList__game__details")
            # Starting
            starting_html = teamlist.find("ul", class_="teamsList__game__details__players")
            starting = buildTeamList(starting_html)

            # Interchange
            interchange_html = teamlist.find("div", class_="teamsList__game__details--interchange").find("ul", class_="teamsList__game__details__players")
            interchange = buildTeamList(interchange_html)

            # Editorials
            editorial_home = teamlist.find('div', class_="teamsList__editorialSection teamsList__editorialSection1").find('p').text
            editorial_away = teamlist.find('div', class_="teamsList__editorialSection teamsList__editorialSection2").find('p').text

            # Creating Post
            interchangeBar = "| | | **INTERCHANGE** | | |\n"
            game = "%s" % gameDetails(matchcode, stadium, time, calendar)
            game += "%s%s%s%s" % (teamHeader(matchcode), teamList(starting), interchangeBar, teamList(interchange))
            game += "\n%s\n\n%s" % (editorial_home, editorial_away)
            print(game)
