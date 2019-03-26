import os
import numpy as np

from discobolus.nhl.api.objects import Teams, Team, Schedule
from discobolus.nhl.api.utils import lookup_team_id

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
        playX, playY = tup[0], tup[1]

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

    return mtrx


def goalCoords(team=None, season_start=2014, season_end=2019):
    mtrx = gen_grid_matrix()
    print("constructing goal matrix")
    agg_coords = []

    if os.path.isfile('sample_data.txt'):
        with open('sample_data.txt', 'r') as d:
            tuples = d.readlines()

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

    if os.path.isfile('sample_data.txt'):
        with open("sample_data.txt", mode='w') as f:
            for t in tuples:
                tup_str = str(t) +'\n'
                f.write(tup_str)
    else:
        with open("sample_data.txt", mode='a') as f:
            for t in tuples:
                tup_str = str(t) +'\n'
                f.write(tup_str)

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

def gen_heatmap(z):
    bg = os.path.join(img_dir, 'hockeyrink.gif')

    heatmap = go.Heatmap(z=z, colorscale=scale_yellow_red)
    layout = dict(
        images=[dict(
            source=bg,
            xref="x",
            yref="y",
            sizex=86,
            sizey=100,
            x=0,
            y=86,
            sizing="stretch",
            opacity=1,
            layer="below",
            visible=True,
            xanchor="left",
            yanchor="top"
        )]
    )

    fig = go.Figure(data=[heatmap], layout=layout)
    py.plot(fig)


matrix = goalCoords(season_start=2018, season_end=2018)
gen_heatmap(z=matrix)


