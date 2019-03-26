import os
import requests
from bs4 import BeautifulSoup as bsoup
from random import choices
from discobolus.nhl import logos_dir


def lookup_team_id(teams, team_name):
    ID = None
    for t in teams:
        if ID is None:
            if team_name.lower() in [t['name'].lower(), t['abbreviation'].lower(), t['teamName'].lower()]:
                ID = t['id']
            else:
                pass
        else:
            break
    return ID


def get_logo(team, season=None):
    team_dir = os.path.join(logos_dir, team)
    img = None
    if os.path.isdir(team_dir):
        season_str = "-".join([str(season-1), str(season)])
        logos = os.listdir(team_dir)
        if season is None:
            pass
        else:
            for logo_file in logos:
                fname = os.path.splitext(logo_file)
                if season_str == fname:
                    img=os.path.join(team_dir, logo_file)
                else:
                    pass
        if img is None:
            img = os.path.join(team_dir, logos[len(logos)-1])

    else:
        img = os.path.join(logos_dir, 'alt.png')

    return img


def get_team_colors(team):
    url = "https://teamcolorcodes.com/nhl-team-color-codes/"
    resp = requests.get(url)
    soup = bsoup(resp.text, 'lxml')
    main = soup.find('div', {"class": "entry-content", "itemprop": "text"})
    teams = main.findAll('a')
    alt_color_set = ["#808000", "#00FF00", "#00FFFF", "#ff0000", "#7F0000", "#00007F", "#000000",
                     "#e5e5f2", "#cccce5", "7f7f00", "#4c4c00", "#4C004C"]
    primary, secondary = None, None
    for t in teams:
        if team == t.get_text().strip():
            colors = t.attrs['style'].split("; ")
            colorsx = [p.split(":") for p in colors]
            colors_dict = {c[0].strip(): c[1].strip().replace("4px solid ", "").replace(";", "") for c in colorsx}
            primary = colors_dict['background-color']

            secondary = colors_dict['border-bottom']

        else:
            pass
    if primary is None:
        primary, secondary = choices(alt_color_set, k=2)
    else:
        pass

    return primary, secondary


def get_num_regular_games(yr):
    prev = str(yr - 1)
    nxt = str(yr)
    season_str = "-".join([prev, nxt])
    if season_str == '2004-2005':
        return 0
    elif season_str == '2012-2013':
        return 48 * 30
    else:
        base_url = "http://www.sportslogos.net/teams/list_by_year/1{yr}"
        url = base_url.format(yr=nxt)

        req = requests.get(url)

        soup = bsoup(req.text, "html5lib")

        content_tag = soup.find("div", {"class": "section", "id": "team",
                                        "style": "overflow: hidden;"})

        li_tags = content_tag.findAll("li", dict(style="height:125px;"))
        teams = [li.get_text().strip() for li in li_tags]
        num_teams = len(teams)
        return 82 * num_teams


def get_num_preseason_games(yr):
    prev = str(yr - 1)
    nxt = str(yr)
    season_str = "-".join([prev, nxt])
    if season_str == '2004-2005' or season_str == '2012-2013':
        return 0
    else:
        base_url = "http://www.sportslogos.net/teams/list_by_year/1{yr}"
        url = base_url.format(yr=nxt)

        req = requests.get(url)

        soup = bsoup(req.text, "html5lib")

        content_tag = soup.find("div", {"class": "section", "id": "team",
                                        "style": "overflow: hidden;"})

        li_tags = content_tag.findAll("li", dict(style="height:125px;"))
        teams = [li.get_text().strip() for li in li_tags]
        num_teams = len(teams)
        return 5 * num_teams


def get_game_ids(yr, num_games, type='reg'):
    type_map = {"reg": "02", 'pre': "01", "post": "03"}
    assert len(yr) == 4, ValueError("Invalid year must be length 4")
    assert int(yr), TypeError("year must be valid integer")
    assert int(num_games), TypeError("num_games must be valid integer")
    assert num_games > -1, ValueError("num_games must be positive value or 0")

    if num_games > 0:
        try:
            t = type_map[type]
        except KeyError:
            raise KeyError("Invalid season type must be (reg, pre, or post)")
        else:
            return [str(yr)+t+str(g).zfill(4) for g in range(1, num_games+1)]
    else:
        return []