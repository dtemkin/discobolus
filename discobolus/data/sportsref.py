from datetime import datetime


class League(object):

    def __init__(self, name):
        self.name = name.lower().strip()
        self._endpoints = self._lookup(name=self.name)

    def years(self, s, e=None):
        if e is None:
            return s
        else:
            for x in range(s, e+1):
                yield x

    def _lookup(self, name):
        if name == 'nba':
            from sportsreference.nba import teams, boxscore, roster, schedule
            return teams, boxscore, roster, schedule
        elif name == 'mlb':
            from sportsreference.mlb import teams, boxscore, roster, schedule
            return teams, boxscore, roster, schedule
        elif name == 'nhl':
            from sportsreference.nhl import teams, boxscore, roster, schedule
            return teams, boxscore, roster, schedule
        elif name == 'nfl':
            from sportsreference.nfl import teams, boxscore, roster, schedule
            return teams, boxscore, roster, schedule
        elif name == 'ncaab':
            from sportsreference.ncaab import teams, boxscore, roster, schedule
            return teams, boxscore, roster, schedule
        elif name == "ncaaf":
            from sportsreference.ncaaf import teams, boxscore, roster, schedule
            return teams, boxscore, roster, schedule
        else:
            raise ValueError("League invalid, must be (nba, mlb, nhl, nfl, ncaab, ncaaf)")

    def abbreviations_teamnames(self, year):
        tms = self.teams(year=year)
        compiled = {}
        for abbr in tms['abbreviation']:
            name = tms['name'][abbr]
            compiled.update({abbr.lower(): name})
        return compiled

    def teamnames_abbreviations(self, year):
        tms = self.teams(year=year)
        compiled = {}
        for abbr in tms['abbreviation']:
            compiled.update({tms['name'][abbr].lower(): abbr.lower()})
        return compiled

    def boxscores(self, sdate, edate):
        if self.name == 'nfl':
            print("Please use nfl_boxscores() function endpoint instead")

        else:
            bx_scores = self._endpoints[1].Boxscores(date=sdate, end_date=edate)
            return bx_scores.games

    def nfl_boxscores(self, week, year, end_week):
        bx_scores = self._endpoints[1].Boxscores(week=week, year=year, end_week=end_week)
        return bx_scores.games

    def teams(self, year):
        tms = self._endpoints[0].Teams(year=year)
        dfs = tms.dataframes.to_dict()
        return dfs

    def schedule(self, team, year):
        sched = self._endpoints[2].Schedule(team, year)
        return sched.dataframe.to_dict()

    def schedule_extended(self, team, year):
        sched = self._endpoints[2].Schedule(team, year)
        return sched.dataframe_extended.to_dict()
