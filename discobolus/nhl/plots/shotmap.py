import os
import numpy as np

from discobolus.data.nhlapi.objects import Teams, Team, Schedule
from discobolus.data.nhlapi.utils import lookup_team_id
import csv
from discobolus.nhl import img_dir
import plotly.plotly as py
import plotly.graph_objs as go


def gen_grid_matrix(gridshape=(100, 86), x_increment=1, y_increment=1):
    inc = (int(x_increment**-1), int(y_increment**-1))

    mat = np.zeros((int(100*inc[0]), int(86*inc[1])))
    return mat


def matrix_counts2pct(mat, total):
    pct_mat = np.zeros(mat.shape)
    for row_idx in range(len(mat)):
        for col_idx in range(len(mat[row_idx])):
            pct_mat[row_idx, col_idx] = float(mat[row_idx, col_idx]/total)
    return pct_mat


def process_grid_coords(tuples):
    mtrx = gen_grid_matrix()

    for tup in tuples:
        playX, playY = float(tup[0]), float(tup[1])

        playX_grid = int(abs(playX))
        playY_grid = int(playY + 42.0)

        grid_coord = (playX_grid, playY_grid)
        try:
            x = mtrx[playX_grid,]
        except KeyError:
            print("N rows", len(mtrx))
            print("Failed to find %s in y range on grid" % str(playX_grid))
            pass
        except IndexError:
            print("N rows", len(mtrx))
            print("Failed to find %s in y range on grid" % str(playX_grid))
            pass
        else:
            try:
                x = mtrx[playX_grid, playY_grid]
            except KeyError:
                print(len(mtrx[:, playY_grid]))
                print("Failed to find %s in x range on grid" % str(playX_grid))
                pass
            except IndexError:
                print(len(mtrx[:, playY_grid]))
                print("Failed to find %s in x range on grid" % str(playX_grid))
                pass
            else:
                mtrx[playX_grid, playY_grid] += 1

    return mtrx, len(tuples)


def goalCoords(team=None, season_start=2014, season_end=2019):
    mtrx = gen_grid_matrix()
    print("constructing goal matrix")
    agg_coords = []

    if os.path.isfile('sample_data.csv'):
        with open('sample_data.csv', 'r') as d:
            readr = csv.reader(d)
            tuples = [row for row in readr]

    else:
        tuples = []
        for season in range(season_start, season_end+1):
            if team:
                teams = Teams()
                teams.get_all(active_only=True)
                tm_id = lookup_team_id(teams, team_name=team)
                t = Team()
                t.get(tm_id)
                sched = t.regular_schedule(season=season)
            else:
                sched = Schedule()
                sched.get(season=season)

            print('getting plays')
            for game in sched:
                tuples.extend([(p.coordinates['x'], p.coordinates['y']) for p in game.plays.scoring if len(p.coordinates) == 2])

    if os.path.isfile('sample_data.csv'):
        with open("sample_data.csv", mode='w') as f:
            writr = csv.writer(f)
            tups_strings = [[str(t[0]), str(t[1])] for t in tuples]
            writr.writerows(tups_strings)

    else:
        with open("sample_data.csv", mode='a') as f:
            writr = csv.writer(f)
            tups_strings = [[str(t[0]), str(t[1])] for t in tuples]
            writr.writerows(tups_strings)

    return process_grid_coords(tuples=tuples)


# yellow/red scale
scale_yellow_red = [[1.0, "rgb(249, 21, 21)"],
                    [0.9, "rgb(249, 49, 21)"],
                    [0.8, "rgb(249, 78, 21)"],
                    [0.7, "rgb(249, 107, 21)"],
                    [0.6, "rgb(249, 136, 22)"],
                    [0.5, "rgb(249, 150, 22)"],
                    [0.4, "rgb(249, 164, 22)"],
                    [0.3, "rgb(249, 178, 22)"],
                    [0.2, "rgb(249, 193, 22)"],
                    [0.1, "rgb(253, 234, 177)"],
                    [0.0, "rgb(255, 255, 255)"]][::-1]


scale_red = [[0.0, "rgb(255,255,255)"],
             [0.1, "rgb(249,229,229)"],
             [0.2, "rgb(243,204,204)"],
             [0.3, "rgb(237,178,178)"],
             [0.4, "rgb(232,153,153)"],
             [0.5, "rgb(226,127,127)"],
             [0.6, "rgb(220,102,102)"],
             [0.7, "rgb(215,76,76)"],
             [0.8, "rgb(209,51,51)"],
             [0.9, "rgb(203,25,25)"],
             [1.0, "rgb(198,0,0)"]]


scale_orange_red = [[0.0, '#FFFFFF'],
                    [0.1, '#F09C00'],
                    [0.2, "#E28A00"],
                    [0.3, "#D57800"],
                    [0.4, "#C76600"],
                    [0.5, "#BA5400"],
                    [0.6, "#AD4200"],
                    [0.7, "#9F3000"],
                    [0.8, "#921E00"],
                    [0.9, "#850D00"],
                    [1.0, "#610A00"]]


scale_red_green = [[1.0, '#FF0000'],
                   [0.95, '#F20C00'],
                   [0.90, '#E51900'],
                   [0.85, "#D82600"],
                   [0.8, '#CC3300'],
                   [0.75, '#BF3F00'],
                   [0.7, "#B24C00"],
                   [0.65, "#A55900"],
                   [0.6, "#996600"],
                   [0.55, "#8C7200"],
                   [0.50, "#7F7F00"],
                   [0.45, "#728C00"],
                   [0.40, "#669900"],
                   [0.35, "#59A500"],
                   [0.30, '#4CB200'],
                   [0.25, '#3FBF00'],
                   [0.20, '#33CC00'],
                   [0.15, '#26D800'],
                   [0.10, '#19E500'],
                   [0.05, '#0CF200'],
                   [0.0, '#FFFFFF']][::-1]

# #blue gradient scale
# color_scale = [[0., "rgb(255,255,255)"],
#                [0.1, "rgb(160, 162, 247)"],
#                [.2, "rgb(108, 111, 226)"],
#                [.3, 'rgb(77, 80, 198)'],
#                [.4, "rgb(52, 55, 168)"],
#                [.5, "rgb(32, 35, 124)"],
#                [.6, "rgb(135, 139, 255)"],
#                [.7, "rgb(91, 95, 211)"],
#                [.8, "rgb(20, 23, 99)"],
#                [.9, "rgb(14, 16, 81)"],
#                [1.0, "rgb(5, 6, 43)"]]
#

def gen_heatmap(z, plot_title):
    bg = "https://github.com/dtemkin/discobolus/blob/master/discobolus/nhl/img/hockeyrink.gif"
    heatmap = go.Heatmap(z=z, colorscale=scale_red_green, opacity=1.0)
    layout = dict(
        title=plot_title,
        images=[dict(
            visible=True,
            source=bg,
            xref="paper",
            yref="paper",
            sizex=1.0,
            sizey=1.0,
            x=.50,
            y=0,
            sizing="stretch",
            opacity=.2,
            layer='above',
            xanchor="center",
            yanchor="bottom"
        )]
    )

    fig = go.Figure(data=[heatmap], layout=layout)
    py.plot(fig)


matrix, total = goalCoords(season_start=2012, season_end=2019)
gen_heatmap(z=matrix, plot_title="NHL Regular Season Goals Heatmap (2012-2019) [All Teams]")


