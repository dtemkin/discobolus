from discobolus.nhl.api import UserList, UserDict
from discobolus.nhl.api.base import BaseEndpoint
from discobolus.nhl.api.utils import get_logo, get_team_colors, get_num_regular_games
from datetime import datetime

class Plays(UserDict, BaseEndpoint):

    def __init__(self, data={}):
        UserDict.__init__(self, data)
        BaseEndpoint.__init__(self, "game")

    def get(self, ID):
        url = "/".join([self.url, ID, "feed", "live"])
        try:
            resp = self._request(url)
        except Exception as err:
            raise Exception(err)
        else:
            r = self._check_response(resp)
            if r:
                game = Game(r)
                self.update(game.plays)

    @staticmethod
    def _event_code_filter(events, code):
        for event in events:
            ev = Play(event)
            if ev.result['eventTypeId'] == code:
                yield ev
            else:
                pass

    @staticmethod
    def _subevent_code_filter(events, primary_code, secondary_code):

        for event in Plays._event_code_filter(events=events, code=primary_code):
            ev = Play(event)
            try:
                sectype = ev.result['secondaryType']
            except KeyError:
                pass
            else:
                if secondary_code == sectype:
                    yield ev
                else:
                    pass

    @property
    def all(self):
        return self['allPlays']

    @property
    def scoring(self):
        return [Play(self['allPlays'][i]) for i in self['scoringPlays']]

    @property
    def penalty(self):
        return [Play(self['allPlays'][i]) for i in self['penaltyPlays']]

    @property
    def byPeriod(self):
        return [Play(self['allPlays'][i]) for i in self['playsByPeriod']]

    @property
    def latest(self):
        return self['allPlays'][self['currentPlay']]


    # @property
    # def takeaways(self):
    #     return iter(Plays._event_code_filter(self.all, "TAKEAWAY"))
    #
    # @property
    # def giveaways(self):
    #     return iter(Plays._event_code_filter(self.all, "GIVEAWAY"))
    #
    # @property
    # def shots(self):
    #     return iter(Plays._event_code_filter(self.all, "SHOT"))
    #
    # @property
    # def stops(self):
    #     return iter(Plays._event_code_filter(self.all, "STOP"))
    #
    # @property
    # def slapshots(self):
    #     return iter(Plays._subevent_code_filter(self.all, primary_code='SHOT', secondary_code='Slap Shot'))
    #
    # @property
    # def snapshots(self):
    #     return iter(Plays._subevent_code_filter(self.all, primary_code='SHOT', secondary_code="Snap Shot"))
    #
    # @property
    # def wristshots(self):
    #     return iter(Plays._subevent_code_filter(self.all, primary_code='SHOT', secondary_code='Wrist Shot'))
    #
    # @property
    # def backhand_shots(self):
    #     return iter(Plays._subevent_code_filter(self.all, primary_code='SHOT', secondary_code='Backhand'))
    #
    # @property
    # def shot_blocks(self):
    #     return iter(Plays._event_code_filter(self.all, "BLOCKED_SHOT"))
    #
    # @property
    # def missed_shots(self):
    #     return iter(Plays._event_code_filter(self.all, "MISSED_SHOT"))
    #
    # @property
    # def hits(self):
    #     return iter(Plays._event_code_filter(self.all, 'HIT'))
    #
    # @property
    # def fights(self):
    #     return iter(Plays._subevent_code_filter(self.all, "PENALTY", "Fighting"))
    #


class Play(UserDict):

    def __init__(self, data={}):
        super().__init__(data)

    @property
    def ID(self):
        return self['about']['eventId']

    @property
    def index(self):
        return self['about']['eventIdx']

    @property
    def coordinates(self):
        return self['coordinates']

    @property
    def about(self):
        return self['about']

    @property
    def result(self):
        return self['result']


class Game(UserDict, BaseEndpoint):

    def __init__(self, data={}):
        BaseEndpoint.__init__(self, url_ext='game')
        UserDict.__init__(self, data)

    def get(self, ID):
        url = "/".join([self.url, str(ID), "feed", "live"])

        try:
            resp = self._request(url)
        except Exception as err:
            raise Exception(err)
        else:
            r = self._check_response(resp)
            if r is not None:
                self.update(r)
                print("Got %s" % str(self))


    @property
    def gameData(self):
        return self['gameData']

    @property
    def liveData(self):
        return self['liveData']

    @property
    def lineScore(self):
        return self.liveData['linescore']

    @property
    def boxscore(self):
        return self.liveData['boxscore']

    @property
    def current_period(self):
        if int(self.lineScore['currentPeriod']) == 3:
            if self.lineScore['currentPeriodTimeRemaining'] == 'Final':
                return 99
            else:
                return 3
        else:
            return int(self.lineScore['currentPeriod'])
    @property
    def ID(self):
        return self.gameData['game']['id']

    @property
    def date(self):
        orig_str = self.gameData['datetime']['dateTime'].replace("T", " ").replace("Z", "")
        return datetime.strptime(orig_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

    @property
    def season(self):
        return self.gameData['game']['season']

    @property
    def game_type(self):
        return self.gameData['game']['type']

    @property
    def teams(self):
        return {t: Team(self.gameData['teams'][t]) for t in self.gameData['teams']}

    @property
    def home_team(self):
        return self.teams['home']

    @property
    def home_score(self):
        return self.liveData['linescore']['teams']['home']['goals']

    @property
    def away_score(self):
        return self.liveData['linescore']['teams']['away']['goals']

    @property
    def winner(self):
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        else:
            return None

    @property
    def is_tie(self):
        if self.winner is None:
            return True
        else:
            return False

    @property
    def away_team(self):
        return self.teams['away']

    @property
    def players(self):
        return self.gameData['players']

    @property
    def venue(self):
        return self.gameData['venue']['name']

    @property
    def plays(self):
        return Plays(data=self.liveData['plays'])

    def __dict__(self):
        return self

    def __str__(self):
        return "Game({date} @ {home} v. {away} [Final: {home_score} - {away_score}])".format(date=self.date, home=self.home_team, away=self.away_team,
                                                                                             home_score=str(self.home_score), away_score=str(self.away_score))

class Games(UserList):

    def __init__(self, initlist=[]):
        super().__init__(initlist=initlist)

    def _get_ids(self, yr, num_games, type):

        type_map = {"reg": "02", 'pre': "01", "post": "03"}

        assert len(str(yr)) == 4, ValueError("Invalid year must be length 4")
        assert int(yr), TypeError("year must be valid integer")
        if num_games == 'max':
            if type == "reg":
                num = get_num_regular_games(yr=yr)
            else:
                print("number of preseason and post season games are not yet configured.")

        else:
            assert int(num_games), TypeError("num_games must be valid integer or 'max'")
            assert num_games > -1, ValueError("num_games must be positive value or 0")
            num = num_games

        if num > 0:
            try:
                t = type_map[type]
            except KeyError:
                raise KeyError("Invalid season type must be (reg, pre, or post)")
            else:

                return ["".join([str(yr), str(t), str(g).zfill(4)]) for g in range(1, num + 1)]
        else:
            return []

    def _team_filter(self, data, tm, side='any'):
        away_names = [data.away_team.full_name.lower(), data.away_team.abbr.lower(), data.away_team.name.lower()]
        home_names = [data.home_team.full_name.lower(), data.home_team.abbr.lower(), data.home_team.name.lower()]

        if side == 'any':
            if tm.lower() in away_names or tm.lower() in home_names:
                return data
            else:
                return None

        elif side == 'away' and tm.lower() in away_names:
            return data
        elif side == 'home' and tm.lower() in home_names:
            return data
        else:
            return None

    def get_multi(self, IDs, **kwargs):
        for i in IDs:
            game = Game()
            game.get(ID=i)
            if len(game) > 0:
                self.append(game)
            else:
                break

    def get_all(self, **kwargs):
        ssn = kwargs.get("season", None)
        tm1 = kwargs.get("team1", None)
        team1_side=kwargs.get('team1_side', 'any')
        tm2 = kwargs.get("team2", None)
        team2_side = kwargs.get('team2_side', "any")

        if ssn is None:
            raise ValueError("must specify season if IDs=='all'")
        else:
            IDs = self._get_ids(yr=ssn, type=kwargs.get("game_type", "reg"), num_games=kwargs.get("num_games", "max"))

            for i in IDs:
                game = Game()
                game.get(i)
                data = game
                if len(game) > 0:
                    if tm1 is not None and data is not None:
                        data = self._team_filter(data, tm1, team1_side.lower())

                    if tm2 is not None and data is not None:
                        data = self._team_filter(data, tm2, team2_side.lower())

                    if data is None:
                        pass
                    else:
                        self.append(data)

                else:
                    break


class Schedule(UserList, BaseEndpoint):

    def __init__(self, data=[]):
        UserList.__init__(self, initlist=data)
        BaseEndpoint.__init__(self, url_ext='schedule')

    def get(self, season, game_type='reg', team_id='all', expand=None):

        reg_dates = [(season-1, 10, 1), (season, 4, 1)]
        pre_dates = [(season-1, 9, 10), (season-1, 10, 10)]
        post_dates = [(season, 4, 1), (season, 6, 30)]
        game_type_map = {"reg": ("R", reg_dates),
                         "pre": ("PR", pre_dates),
                         "post": ("P", post_dates)}

        gtypes = game_type_map[game_type]

        dates = gtypes[1]
        stdate = datetime(int(dates[0][0]), int(dates[0][1]), int(dates[0][2])).strftime("%Y-%m-%d")
        eddate = datetime(int(dates[1][0]), int(dates[1][1]), int(dates[1][2])).strftime("%Y-%m-%d")

        self.params.update({"startDate": stdate, "endDate": eddate})
        if type(team_id) is list:
            assert all([int(i) for i in team_id]), TypeError("Invalid team id")
            tm_ids = ",".join([str(t) for t in team_id])
            self.params.update({"teamId": tm_ids})

        elif team_id == 'all':
            pass
        else:
            assert int(team_id), TypeError("Invalid team id. must be valid integer")
            tm_ids = team_id
            self.params.update({"teamId": tm_ids})
        try:
            resp = self._request(self.url)
        except Exception as err:
            raise Exception(err)
        else:
            r = self._check_response(resp)
            if r and len(r['dates']) > 0:
                for date in r['dates']:
                    games = Games()
                    games.get_multi(IDs=[g['gamePk'] for g in date['games'] if g['gameType'] == gtypes[0]])
                    self.extend(games)


class Player(UserDict, BaseEndpoint):

    def __init__(self, data={}):
        UserDict.__init__(self, data)
        BaseEndpoint.__init__(self, url_ext ="people")

    def get(self, ID):
        assert int(ID), AssertionError("ID must be valid integer")
        try:
            url = "/".join([self.url, str(ID)])
            data = self._request(url)
        except Exception as err:
            raise Exception(err)
        else:
            if self._check_response(data=data) is not None:
                self.update(data['people'][0])

    @property
    def ID(self):
        return self['id']

    @property
    def full_name(self):
        return self['fullName']

    @property
    def link(self):
        return "".join([self.baseurl, self['link']])

    @property
    def fname(self):
        return self['firstName']

    @property
    def lname(self):
        return self['lastName']

    @property
    def jersey_number(self):
        return int(self['primaryNumber'])

    @property
    def birthdate_datetime(self):
        return datetime.strptime(self['birthDate'], "%Y-%m-%d")

    @property
    def birthdate_string(self):
        return self['birthDate']

    @property
    def age(self):
        return self['currentAge']

    @property
    def birthCity(self):
        return self['birthCity']

    @property
    def birthCountry(self):
        return self['birthCountry']

    @property
    def nationality(self):
        return self['nationality']

    @property
    def height(self):
        return self['height']

    @property
    def weight(self):
        return self['weight']

    @property
    def active(self):
        return self['active']

    @property
    def is_asstcaptain(self):
        return self['alternateCaptain']

    @property
    def is_captain(self):
        return self['captain']

    @property
    def is_rookie(self):
        return self['rookie']

    @property
    def shoots(self):
        v = self['shootsCatches']
        if v == 'L':
            return 'left'
        else:
            return 'right'
    @property
    def roster_status(self):
        return self['rosterStatus']

    @property
    def position(self):
        return self['primaryPosition']['abbreviation']

    @property
    def current_team(self):
        return self['current_team']

    @property
    def stats(self):
        url = "/".join([self.url, self.ID, 'stats'])
        resp = self._request(url)
        return resp

    def __dict__(self):
        return self


class Roster(UserList, BaseEndpoint):

    def __init__(self, initlist=[]):
        UserList.__init__(self, initlist)
        BaseEndpoint.__init__(self, url_ext="teams")

    def get(self, teamID, detailed=False):
        assert int(teamID), AssertionError("ID must be valid integer")
        try:
            url = "/".join([self.url, str(teamID)])
            data = self._request(url)
        except Exception as err:
            raise Exception(err)
        else:
            if type(data) is str:
                print("Failed to create player", data)
            else:

                if detailed:
                    for pid in [d['person']['id'] for d in data['roster']]:
                        plyr = Player().get(pid)
                        self.append(plyr)
                else:
                    for d in data['roster']:
                        dx = {**d['person']}
                        dx.update(**d['jerseyNumber'])
                        dx.update(**d['position']['abbreviation'])
                        plyr = Player(dx)
                        self.add_player(plyr)

    def add_player(self, x):
        if len(self) == 0 or x.ID not in [s.ID for s in self]:
            self.append(x)

    def drop_player(self, x):
        if type(x) == int:
            plyr_id = x
        elif isinstance(x, Player):
            plyr_id = x.ID
        else:
            raise TypeError("x must be valid int or Player object")

        if len(self) == 0:
            print("Player not found. Roster appears to be empty.")
        elif x.id not in [s.id for s in self]:
            print("%s not found in roster." % x)
        else:
            plyr_idx = [i for i in range(len(self)) if self[i].id==plyr_id]
            if len(plyr_idx) == 0:
                print("Ooops! An unexpected error occurred when trying to drop a player from the roster.")
            self.pop(plyr_idx[0])


class Teams(UserList, BaseEndpoint):

    def __init__(self, data=[]):
        UserList.__init__(self, initlist=data)
        BaseEndpoint.__init__(self, url_ext='teams')

    def get_multi(self, IDs, active_only=True):
        if type(IDs) is list:
            assert all([int(i) for i in IDs]), "All ids must be valid integer"
            self.params.update(dict(teamId=IDs))

        elif type(IDs) is int or type(IDs) is str:
            assert int(IDs) & int(IDs) > 0, TypeError("IDs must be valid int greater than 0")
            self.params.update(dict(teamId=int(IDs)))


    def get_all(self, active_only=True):
        resp = self._request(url=self.url)
        if resp:
            self.extend(resp['teams'])
        else:
            print("No teams returned, check IDs and try again")

    def filter_by_division(self, **kwargs):
        ID = kwargs.get("id", None)
        name = kwargs.get("name", None)

        assert ID != name, AssertionError("must specify division name or id")
        self.get()

        if ID:
            assert int(ID) & int(ID) > 0, TypeError("id must be valid int and > 0")
            try:
                tms = [t for t in self if t['division']['id'] == int(ID)]
            except Exception as err:
                raise Exception("Whoops an unexpected error occurred when trying to filter. \n", err)
            else:
                if len(tms) == 0:
                    print("No teams found. Check division id value and try again.")

                else:
                    self.clear()
                    self.extend(tms)

        elif name:
            if len(name) == 1:
                tms = [t for t in self if t['division']['abbreviation'].lower() == name.lower()]
            elif 3 >= len(name) <= 5:
                tms = [t for t in self if t['division']['nameShort'].lower() == name.lower()]
            elif len(name) > 6:
                tms = [t for t in self if t['division']['name'].lower() == name.lower()]

            else:
                raise ValueError("Cannot infer which name style is being used, (i.e. full name, short name, abbreviation).")

            if len(tms) == 0:
                print("No teams found. Check division name value and try again.")

            else:
                self.clear()
                self.extend(tms)


class Team(UserDict, BaseEndpoint):

    def __init__(self, data={}):
        UserDict.__init__(self, dict=data)
        BaseEndpoint.__init__(self, url_ext='teams')

    def get(self, ID, expand=None):
        self.params.update({"teamId": ID})
        try:
            resp = self._request(self.url)
        except Exception as err:
            raise Exception(err)
        else:
            r = self._check_response(resp)
            if r:
                self.update(**r['teams'][0])
                print("Found %s" % str(self))
            else:
                print("No matching team found.")

    @property
    def ID(self):
        return self['id']

    @property
    def name(self):
        return self['teamName']

    @property
    def full_name(self):
        return self['name']

    @property
    def abbr(self):
        return self['abbreviation']

    @property
    def conference(self):
        return self['conference']

    @property
    def division(self):
        return self['division']

    @property
    def franchise(self):
        return self['franchise']

    @property
    def short_name(self):
        return self['shortName']

    @property
    def location(self):
        return self['locationName']

    @property
    def venue(self):
        return self['venue']

    @property
    def triCode(self):
        return self['triCode']

    @property
    def firstYear(self):
        return int(self['firstYearOfPlay'])

    @property
    def is_active(self):
        return self['active']

    @property
    def api_link(self):
        return "".join([self.baseurl, self['link']])

    def get_logo(self, season=datetime.today().year):
        logo = get_logo(team=self.full_name, season=season)
        if logo is None:
            print("No logo found please check season and try again. ")
        else:
            return logo

    def get_team_colors(self):
        colors = get_team_colors(team=self.full_name)
        return colors

    def get_roster(self, detailed=False):
        rstr = Roster().get(teamID=self.ID, detailed=detailed)
        return rstr

    def regular_schedule(self, season, upcoming_only=False):
        sched = Schedule()
        sched.get(season=season, team_id=self.ID, game_type='reg')
        return sched

    def get_pre_schedule(self, season, upcoming_only=False):
        sched = Schedule()
        sched.get(season=season, team_id=self.ID, game_type='pre')
        return sched

    def get_post_schedule(self, season, upcoming_only=False):
        sched = Schedule()
        sched.get(season=season, team_id=self.ID, game_type='post')
        return sched

    def season_record(self, type):
        pass

    def __str__(self):
        return self.short_name

    def __dict__(self):
        return self