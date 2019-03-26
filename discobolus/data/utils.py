import json
import os
from urllib import request
from bs4 import BeautifulSoup as bsoup
import requests

dir_path = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(dir_path, 'config.json')


def get_gameIDs(season, max_games, game_type='reg'):
    game_type_map = {"pre": "01", "reg": "02"}
    for i in range(1, max_games+1):
        yield str(season)+game_type_map.get(game_type, '02') + str(i).zfill(4), i


def get_logos_by_season(start_year, end_year, league, logos_dir):

    league_map = {"mlb": 4, "nhl": 1, "nba": 6, "nfl": 7, "mls": 9}
    try:
        league_id = league_map[league.lower()]
    except KeyError:
        raise KeyError("No matching league configured")
    else:
        for yr in range(start_year, end_year+1):
            prev = str(yr - 1)
            nxt = str(yr)
            season_str = "-".join([prev, nxt])

            print("Retrieving Logos from Year %s" % (season_str))

            base_url = "http://www.sportslogos.net/teams/list_by_year/{lg}{yr}"
            url = base_url.format(lg=league_id, yr=nxt)

            req = requests.get(url)

            soup = bsoup(req.text, "html5lib")

            content_tag = soup.find("div", {"class": "section", "id": "team",
                                            "style": "overflow: hidden;"})
        
            li_tags = content_tag.findAll("li", dict(style="height:125px;"))
            teams = [(li.get_text().strip(), li.find("img").attrs['src']) for li in li_tags]

            for team in teams:
                team_dir = os.path.join(logos_dir, team[0])
                if os.path.isdir(team_dir):
                    pass
                else:
                    os.mkdir(team_dir)

                logo_file = os.path.join(team_dir, season_str+".gif")
                if os.path.isfile(logo_file):
                    print("Logo Already Saved")
                    pass
                else:
                    request.urlretrieve(team[1], logo_file)
                    print("Got %s %s Logo" % (team[0], season_str))


def load_config(league, rtn='local'):

    f = open(config_file, mode='r')
    js = json.load(f)
    f.close()
    l = league.lower()
    try:
        lx = js[l]
    except KeyError or AttributeError:
        raise KeyError("Invalid league value. No configuration found.")
    else:
        if rtn == 'all':
            return js
        else:
            return lx


def _write_data(js):
    fo = open(config_file, mode='w')
    json.dump(js, fo)


def update_config(league, new_info, info_type, start_keys=None):
    old_info = load_config(league=league, rtn='all')
    league_data = old_info[league.lower()]
    league_sources = league_data['sources']
    league_metadata = league_data['metadata']
    if info_type == "metadata":
        if type(start_keys) is str:
            l = league_metadata
            try:
                l[start_keys]
            except KeyError:
                l.update({start_keys: {}})
                l = l[start_keys]
            else:
                l = l[start_keys]

            l.update(**new_info)
        elif type(start_keys) is list:
            l = league_metadata
            for k in start_keys:
                try:
                    l[k]
                except KeyError:
                    l.update({k: {}})
                    l = l[k]
                else:
                    l = l[k]
            l.update(**new_info)
        else:
            league_metadata.update(**new_info)
    elif info_type == 'sources':
        if type(start_keys) is str:
            l = league_sources
            try:
                l[start_keys]
            except KeyError:
                l.update({start_keys: {}})
                l = l[start_keys]
            else:
                l = l[start_keys]

            l.update(**new_info)
        elif type(start_keys) is list:
            l = league_sources
            for k in start_keys:
                try:
                    l[k]
                except KeyError:
                    l.update({k: {}})
                    l = l[k]
                else:
                    l = l[k]
            l.update(**new_info)
        else:
            league_sources.update(**new_info)

    old_info.update({league.lower(): {"sources": league_sources, "metadata": league_metadata}})


    print("Config Metadata updated.")
