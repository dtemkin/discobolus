from discobolus.nhl.api import UserList
from discobolus.nhl.api.base import BaseAPI
from discobolus.nhl.api.utils import get_num_regular_games
from datetime import datetime


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


class Schedule(UserList, BaseAPI):

    def __init__(self, data=[]):
        UserList.__init__(self, initlist=data)
        BaseAPI.__init__(self, url_ext='schedule')

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
