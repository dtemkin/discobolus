from pandas import DataFrame
from bs4 import BeautifulSoup as bsoup
import requests
from datetime import datetime
from time import time
import re
from csv import DictReader
from urllib import request
from discobolus.data.sportsref import League



def check_game_id(game_id, data_table):
    if len(data_table) == 0:
        return False
    else:

        x = [d for d in data_table if game_id != d['game_id']]
        if len(x) > 0:
            return True
        else:
            return False


def get_table(league, start_year, end_year, *args, **kwargs):

    lg = League(name=league)
    abbrevs_year = {y: lg.abbreviations_teamnames(year=y) for y in range(start_year-1, end_year+1)}

    posthead = {"Host": "www.shrpsports.com",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Referer": "http://www.shrpsports.com/%s/result.htm" % league,
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"}

    season0 = str(start_year)
    season1 = str(end_year)

    season_type = kwargs.pop("seastype", "reg")

    postdata = {"team1": "", "div1": "", "team2": "", "div2": "",
                "begseas": season0, "begdate": "all", "begmonth": "all", "begyear": "all",
                "endseas": season1, "enddate": "all", "endmonth": "all", "endyear": "all",
                "seastype": season_type, "location": "", "gametype": "",
                "serstand": "", "specmonth": "all", "specdate": "all",
                "month": "", "day": "", "last": "", "B1": "Submit"}
    postdata.update({k: kwargs.get(k) for k in kwargs if k in postdata})
    baseurl = "http://www.shrpsports.com/%s/result.php" % league

    postdata.update({"beginseas": season0, "endseas": season1})
    postreq = requests.post(url=baseurl, data=postdata, headers=posthead)

    soup = bsoup(postreq.text, "lxml")

    htmltable = soup.find("table", {"cellpadding": "5", "cellspacing": "0"})
    rows = htmltable.findAll("tr")
    datatable = []

    for r in range(len(rows)):

        cols = rows[r].findAll("td")
        season = cols[0].string.replace(" season:", "").strip()
        date = datetime.strptime(cols[1].string, "%a %b %d %Y")
        loc = cols[2].string.split(" ")[1].strip()

        # abbr = re.search("(?<=;team=).*?&", str(cols[3]))

        teams_scores = [c.strip().split(" ") for c in cols[3].get_text().split(", ")]

        if len(teams_scores) < 2:
            pass
        else:
            # print("%s%% done. \r" % round((float(r/len(rows))*100), 4))
            abbrs = abbrevs_year[date.year]
            try:
                name = abbrs[loc.lower()]
            except KeyError:
                name = [abbrs[x] for x in abbrs if x.find(loc.lower()[:1]) > -1][0]

            team1 = teams_scores[0]

            team2 = teams_scores[1]
            team2s = team2[len(team2) - 1].split("\xa0")

            team1_name = " ".join(team1[:len(team1) - 1])
            team2_name = " ".join(team2[:len(team2) - 1])

            if name.find(team1_name.strip()) > -1:
                home_team = team1_name
                home_score = int(team1[len(team1) - 1])

                away_team = team2_name
                away_score = int(team2s[0])
                winner = "home"
                diff = home_score - away_score

                if away_score == home_score:
                    winner = "tie"
                    diff = 0
                else:
                    pass

            elif name.find(team2_name.strip()) > -1:

                home_team = team2_name
                home_score = int(team2s[0])

                away_team = team1_name
                away_score = int(team1[len(team1) - 1])
                winner = "away"
                diff = away_score - home_score

                if away_score == home_score:
                    winner = "tie"
                    diff = 0
                else:
                    pass
            else:
                raise AttributeError("Could not find team_name")

            if len(team2s) > 1:
                ot = True
                numots = 0
                n = re.search('([0-9])', team2s[1])
                if n is None:
                    numots += 1
                else:
                    numots += int(n.group(0))
            else:
                ot = False
                numots = 0

            game_id = "_".join([league.lower(), date.strftime("%Y%m%d"), home_team])
            season_yrs = season.split("-")
            yr1 = str(season_yrs[0])
            yr2 = "".join([str(yr1[:1]), str(season_yrs[1])])
            row = {"game_id": game_id, "league": league.lower(),
                   "season": "-".join([yr1, yr2]),
                   "game_date": date.strftime("%Y-%m-%d"),
                   "year": date.year, "month": date.month, "day": date.day,
                   "dayofweek": date.strftime("%A"), "loc_abbr": loc,
                   "location": " ".join(team1[:len(team1) - 1]),
                   "winner": winner, "home_score": home_score,
                   "home_team": home_team, "away_team": away_team,
                   "away_score": away_score, "overtime": ot,
                   "overtime_count": numots, "margin": diff}

            if check_game_id(game_id, datatable) is True:
                pass
            else:
                yield row

