import math
import re
from typing import List, Dict

from matplotlib import pyplot as plt


line_style = dict()
line_style['Exhaustive'] = 'o', 'blue'
line_style['Exhaustive with sorting'] = 's', 'green'
line_style['Exhaustive with sorting and ID'] = '^', 'orange'
line_style['Heuristic'] = 'D', 'red'

line_style['EPEA*'] = '^', 'orange'
line_style['A*+OD+ID'] = 'X', 'darkolivegreen'
line_style['CBS'] = 'D', 'darkblue'
line_style['M*'] = 's', 'darkred'
line_style['ICTS'] = 'o', 'deepskyblue'


def get_evaluations_data(name: str):
    with open(f'../../{name}.txt') as f:
        data = dict()
        for line in f.readlines():
            matches: List[re.Match] = re.findall(
                '^\w+-\d+x\d+-A(\d+)_T(\d+), \w+-\d+x\d+-A\d+_T\d+-(\d+).map, ([\d.]+|None), (\d+|None)$', line)
            agents = int(matches[0][0])
            teams = int(matches[0][1])
            evaluations = None if matches[0][4] == 'None' else int(matches[0][4])
            if teams in data.keys():
                if agents in data[teams].keys():
                    data[teams][agents].append(evaluations)
                else:
                    data[teams][agents] = [evaluations]
            else:
                data[teams] = dict()
                data[teams][agents] = [evaluations]
    return data

def get_runtime_data(name: str):
    with open(f'../../{name}.txt') as f:
        data = dict()
        for line in f.readlines():
            matches: List[re.Match] = re.findall(
                '^\w+-\d+x\d+-A(\d+)_T(\d+), \w+-\d+x\d+-A\d+_T\d+-(\d+).map, ([\d.]+|None)$', line)
            agents = int(matches[0][0])
            teams = int(matches[0][1])
            time = float('nan' if matches[0][3] == 'None' else matches[0][3])
            if teams in data.keys():
                if agents in data[teams].keys():
                    data[teams][agents].append(time)
                else:
                    data[teams][agents] = [time]
            else:
                data[teams] = dict()
                data[teams][agents] = [time]
    return data

def get_mean(data: Dict[int, List[float]]) -> Dict[int, float]:
    res = dict()
    for key in data.keys():
        length =  len(list(filter(lambda x: not math.isnan(x), data[key])))
        res[key] = None if length == 0 else sum(filter(lambda x: not math.isnan(x), data[key])) / length
    return res

def get_completion(data: Dict[int, List[float]]) -> Dict[int, float]:
    res = dict()
    for key in data.keys():
        res[key] = (1 - len(list(filter(math.isnan, data[key]))) / len(data[key])) * 100
    return res

def get_evaluations(data: Dict[int, List[int]]) -> Dict[int, float]:
    res = dict()
    for key in data.keys():
        completed = list(filter(lambda x: x is not None, data[key]))
        average = sum(completed) / len(completed)
        res[key] = average
    return res


def compare_goal_assignments(data: Dict[str, Dict[int, List[int]]], title: str):
    #fix, ax = plt.plot()
    x_length = 0
    for data_name, algorithm_data in data.items():
        evaluations = get_evaluations(algorithm_data)
        max_agents = max(evaluations.keys())
        line = [None] * (max_agents + 1)
        x = range(0, max_agents + 1)
        for key, value in evaluations.items():
            line[key] = value
        marker, color = line_style[data_name]
        plt.plot(x, line, label=data_name, marker=marker, color=color)
        x_length = max(x_length, max_agents)

    plt.legend()
    plt.ylabel('Goal assignments evaluated')
    plt.xlabel('Number of agents')
    plt.title(title)
    plt.show()



def compare_data(data: Dict[str, Dict[int, List[float]]], map_type: str, num_teams: int, f, data_type: str):
    figure = plt.figure(figsize=(6,3))
    ax = figure.add_axes((0.1, 0.18, 0.85, 0.7))
    x_length = 0
    for data_name, teams_data in data.items():
        plot_data = f(teams_data)
        #mean = get_mean(teams_data)
        max_agents = max(plot_data.keys())
        line = [None] * (max_agents + 1)
        x = range(0, max_agents + 1)
        for key, value in plot_data.items():
            line[key] = value
        marker, color = line_style[data_name]
        ax.plot(x, line, label=data_name, marker=marker, color=color)
        x_length = max(x_length, max(plot_data.keys()))

    ax.legend()
    ax.set_ylim([0,100]) if data_type == '% solved' else None
    ax.set_ylabel(f'{data_type}')
    ax.set_xlim([1,x_length])
    ax.set_xlabel('Number of agents')
    team_str = f'agents spread over {num_teams} teams' if num_teams != 1 else f'all agents in 1 team'
    ax.set_title(f'{data_type} out of 200 {map_type} maps with {team_str}')
    plt.show()



if __name__ == '__main__':
    maze_exhaustive = get_runtime_data('results/maze_exhaustive')
    maze_exhaustive_sorting = get_runtime_data('results/maze_sorting')
    maze_exhaustive_sorting_id = get_runtime_data('/results/maze_sorting_id')
    maze_heuristic = get_runtime_data('/results/maze_heuristic')
    maze_astar = get_runtime_data('/results/astar_maze')
    maze_mstar = get_runtime_data('/results/mstar_maze')
    maze_icts = get_runtime_data('/results/icts_maze')
    maze_cbs = get_runtime_data('/results/cbs_maze')

    obs_exhaustive = get_runtime_data('/results/obstacle_exhaustive')
    obs_exhaustive_sorting = get_runtime_data('/results/obstacle_exhaustive_sorting')
    obs_exhaustive_sorting_id = get_runtime_data('/results/obstacle_exhaustive_sorting_id')
    obs_heuristic = get_runtime_data('/results/obstacle_heuristic')
    obs_astar = get_runtime_data('/results/astar_obstacle')
    obs_mstar = get_runtime_data('/results/mstar_obstacle')
    obs_icts = get_runtime_data('/results/icts_obstacle')
    obs_cbs = get_runtime_data('/results/cbs_obstacle')


    plot1 = dict()
    plot1['Exhaustive'] = maze_exhaustive[3]
    plot1['Exhaustive with sorting'] = maze_exhaustive_sorting[3]
    plot1['Exhaustive with sorting and ID'] = maze_exhaustive_sorting_id[3]
    plot1['Heuristic'] = maze_heuristic[3]

    compare_data(plot1, 'maze', 3, get_completion, '% solved')

    plot2 = dict()
    plot2['Exhaustive'] = maze_exhaustive[1]
    plot2['Exhaustive with sorting'] = maze_exhaustive_sorting[1]
    plot2['Exhaustive with sorting and ID'] = maze_exhaustive_sorting_id[1]
    plot2['Heuristic'] = maze_heuristic[1]

    compare_data(plot2, 'maze', 1, get_completion, '% solved')

    plot3 = dict()
    plot3['Exhaustive'] = obs_exhaustive[3]
    plot3['Exhaustive with sorting'] = obs_exhaustive_sorting[3]
    plot3['Exhaustive with sorting and ID'] = obs_exhaustive_sorting_id[3]
    plot3['Heuristic'] = obs_heuristic[3]

    compare_data(plot3, 'obstacle', 3, get_completion, '% solved')

    plot4 = dict()
    plot4['Exhaustive'] = obs_exhaustive[1]
    plot4['Exhaustive with sorting'] = obs_exhaustive_sorting[1]
    plot4['Exhaustive with sorting and ID'] = obs_exhaustive_sorting_id[1]
    plot4['Heuristic'] = obs_heuristic[1]

    compare_data(plot4, 'obstacle', 1, get_completion, '% solved')


    obs_exhaustive_evaluations = get_evaluations_data('results/obstacle_exhaustive_evaluations')
    obs_exhaustive_sorting_evaluations = get_evaluations_data('results/obstacle_exhaustive_sorting_evaluations')

    plot5 = dict()
    plot5['Exhaustive'] = obs_exhaustive_evaluations[1]
    plot5['Exhaustive with sorting'] = obs_exhaustive_sorting_evaluations[1]

    compare_goal_assignments(plot5, 'Evaluated goal assignments on obstacle maps with all agents in 1 team')

    plot6 = dict()
    plot6['CBS'] = obs_cbs[1]
    plot6['ICTS'] = obs_icts[1]
    plot6['A*+OD+ID'] = obs_astar[1]
    plot6['M*'] = obs_mstar[1]
    plot6['EPEA*'] = obs_exhaustive_sorting_id[1]
    compare_data(plot6, 'obstacle', 1, get_completion, '% solved')

    plot7 = dict()
    plot7['CBS'] = obs_cbs[3]
    plot7['ICTS'] = obs_icts[3]
    plot7['A*+OD+ID'] = obs_astar[3]
    plot7['M*'] = obs_mstar[3]
    plot7['EPEA*'] = obs_exhaustive_sorting_id[3]
    compare_data(plot7, 'obstacle', 3, get_completion, '% solved')

    plot8 = dict()
    plot8['CBS'] = maze_cbs[1]
    plot8['ICTS'] = maze_icts[1]
    plot8['A*+OD+ID'] = maze_astar[1]
    plot8['M*'] = maze_mstar[1]
    plot8['EPEA*'] = maze_exhaustive_sorting_id[1]
    compare_data(plot8, 'maze', 1, get_completion, '% solved')

    plot9 = dict()
    plot9['CBS'] = maze_cbs[3]
    plot9['ICTS'] = maze_icts[3]
    plot9['A*+OD+ID'] = maze_astar[3]
    plot9['M*'] = maze_mstar[3]
    plot9['EPEA*'] = maze_exhaustive_sorting_id[3]
    compare_data(plot9, 'maze', 3, get_completion, '% solved')


