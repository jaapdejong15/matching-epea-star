import math
import re
from typing import List, Dict

import numpy
from matplotlib import pyplot as plt

# Define a default line style for lines in runtime plots
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

# Define a line style for lines in memory plots
memory_line_style = dict()
memory_line_style['EPEA*'] = '^', 'darkred', '-'
memory_line_style['A*+OD+ID'] = 'X', 'dodgerblue', '-'


def get_evaluations_data(name: str):
    """
    Retrieves the amount of evaluations from a file
    :param name:    The filename
    :return:        Dictionary with the data separated by number of teams
    """
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
    """
    Retrieves the runtime results from a file.
    :param name:        The filename
    :return:            Dictionary with the data separated by number of teams
    """
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
    """
    Turns a dictionary with float lists into a dict with mean values of all non-NaN list entries.
    :param data:        Input dictionary with float lists
    :return:            Output dictionary with float mean values
    """
    res = dict()
    for key in data.keys():
        length = len(list(filter(lambda x: not math.isnan(x), data[key])))
        res[key] = None if length == 0 else sum(filter(lambda x: not math.isnan(x), data[key])) / length
    return res


def get_max(data: Dict[int, List[float]]) -> Dict[int, float]:
    """
    Turns a dictionary with float lists into a dict with max values.
    :param data:        Input dictionary with float lists
    :return:            Output dictionary with float max values
    """
    res = dict()
    for key in data.keys():
        length = len(list(filter(lambda x: not math.isnan(x), data[key])))
        res[key] = None if length == 0 else max(filter(lambda x: not math.isnan(x), data[key]))
    return res


def get_min(data: Dict[int, List[float]]) -> Dict[int, float]:
    """
    Turns a dictionary with float lists into a dict with min values.
    :param data:        Input dictionary with float lists
    :return:            Output dictionary with float min values
    """
    res = dict()
    for key in data.keys():
        length = len(list(filter(lambda x: not math.isnan(x), data[key])))
        res[key] = None if length == 0 else min(filter(lambda x: not math.isnan(x), data[key]))
    return res


def get_completion(data: Dict[int, List[float]]) -> Dict[int, float]:
    """
    Turns a dictionary with float lists into a dict with the percentage of non-NaN values.
    :param data:        Input dictionary with float lists
    :return:            Output dictionary with the percentage of non-NaN values
    """
    res = dict()
    for key in data.keys():
        res[key] = (1 - len(list(filter(math.isnan, data[key]))) / len(data[key])) * 100
    return res


def get_evaluations(data: Dict[int, List[int]]) -> Dict[int, float]:
    """
    Turns a dictionary with float lists into a dict with mean values.
    :param data:        Input dictionary with float lists
    :return:            Output dictionary with float mean values
    """
    res = dict()
    for key in data.keys():
        completed = list(filter(lambda x: x is not None, data[key]))
        res[key] = sum(completed) / len(completed)
    return res


def compare_goal_assignments(data: Dict[str, Dict[int, List[int]]], title: str, name: str) -> None:
    """
    Creates a plot of the average number of goal assignments and displays and stores it.
    :param data:        Dictionary with data dicts, with algorithm names as keys
    :param title:       Title of the plot
    :param name:        Filename of the output file
    """
    figure = plt.figure(figsize=(6, 3))
    ax = figure.add_axes((0.12, 0.18, 0.83, 0.7))
    max_value = 0
    for data_name, algorithm_data in data.items():
        evaluations = get_evaluations(algorithm_data)
        max_agents = max(evaluations.keys())
        line = [None] * (max_agents + 1)
        x = range(0, max_agents + 1)
        for key, value in evaluations.items():
            line[key] = value
            max_value = max(max_value, value)
        marker, color = line_style[data_name]
        ax.plot(x, line, label=data_name, marker=marker, color=color)

    ax.legend()
    ax.set_yrange([0, max_value])
    ax.set_ylabel('Goal assignments evaluated')
    ax.set_xlabel('Number of agents')
    ax.set_title(title)
    plt.grid()
    plt.show()
    figure.savefig(f'../../plots/{name}.pdf', format='pdf')


def compare_memory(data: Dict[str, Dict[int, List[float]]], map_type: str, num_teams: int, name: str) -> None:
    """
    Shows and stores a plot of the average amount of memory used, including ranges for the minimum and maximum
    amount used.
    :param data:        Dictionary with data dicts, with algorithm names as keys
    :param map_type:    Type of map
    :param num_teams:   The number of teams of the map
    :param name:        Filename of the output file
    """
    figure = plt.figure(figsize=(6, 3))
    ax = figure.add_axes((0.12, 0.18, 0.83, 0.7))
    x_length = 0
    for data_name, teams_data in data.items():
        plot_mean_data = get_mean(teams_data)
        plot_max_data = get_max(teams_data)
        plot_min_data = get_min(teams_data)
        max_agents = max(plot_mean_data.keys())
        line_mean = [None] * (max_agents + 1)
        line_max = [None] * (max_agents + 1)
        line_min = [None] * (max_agents + 1)
        x = range(0, max_agents + 1)
        for key, value in plot_mean_data.items():
            line_mean[key] = value / 1000
        for key, value in plot_max_data.items():
            line_max[key] = value / 1000
        for key, value in plot_min_data.items():
            line_min[key] = value / 1000

        marker, color, dashes = memory_line_style[data_name]
        ax.plot(x, line_mean, label=data_name, marker=marker, color=color, linestyle=dashes)
        ax.fill_between(x[1:], line_min[1:], line_max[1:], color=color, alpha=0.2)

        x_length = max(x_length, max(plot_mean_data.keys()))

    ax.legend()
    ax.set_ylabel('Memory usage (MB)')
    ax.set_xticks(numpy.arange(1, x_length, 1))
    ax.set_xlim([1, x_length])
    ax.set_xlabel('Number of agents')
    team_str = f'agents spread over {num_teams} teams' if num_teams != 1 else f'all agents in 1 team'
    ax.set_title(f'Memory usage on {map_type} maps with {team_str}')
    plt.grid()
    plt.show()
    figure.savefig(f'../../plots/{name}.pdf', format='pdf')


def compare_percentage_solved(data: Dict[str, Dict[int, List[float]]], map_type: str, num_teams: int,
                              name: str) -> None:
    """
    Shows and stores a plot of the percentage of maps solved.
    :param data:        Dictionary with data dicts, with algorithm names as keys
    :param map_type:    Type of map
    :param num_teams:   The number of teams of the map
    :param name:        Filename of the output file
    """
    figure = plt.figure(figsize=(6, 3))
    ax = figure.add_axes((0.1, 0.18, 0.85, 0.7))
    x_length = 0
    for data_name, teams_data in data.items():
        plot_data = get_completion(teams_data)
        # mean = get_mean(teams_data)
        max_agents = max(plot_data.keys())
        line = [None] * (max_agents + 1)
        x = range(0, max_agents + 1)
        for key, value in plot_data.items():
            line[key] = value
        marker, color = line_style[data_name]
        ax.plot(x, line, label=data_name, marker=marker, color=color)
        x_length = max(x_length, max(plot_data.keys()))

    ax.legend()
    ax.set_ylim([0, 100]) if data_type == '% solved' else None
    ax.set_ylabel('% solved')
    ax.set_xlim([1, x_length])
    ax.set_xticks(numpy.arange(0, x_length, 1))
    ax.set_xlabel('Number of agents')
    team_str = f'agents spread over {num_teams} teams' if num_teams != 1 else f'all agents in 1 team'
    ax.set_title(f'% solved out of 200 {map_type} maps with {team_str}')
    plt.grid()
    plt.show()
    figure.savefig(f'../../plots/{name}.pdf', format='pdf')


if __name__ == '__main__':
    # Retrieve data from files
    # Maze maps runtimes
    maze_exhaustive = get_runtime_data('results/maze_exhaustive')
    maze_exhaustive_sorting = get_runtime_data('results/maze_sorting')
    maze_exhaustive_sorting_id = get_runtime_data('/results/maze_sorting_id')
    maze_heuristic = get_runtime_data('/results/maze_heuristic')
    maze_astar = get_runtime_data('/results/astar_maze')
    maze_mstar = get_runtime_data('/results/mstar_maze')
    maze_icts = get_runtime_data('/results/icts_maze')
    maze_cbs = get_runtime_data('/results/cbs_maze')

    # Obstacle maps runtimes
    obs_exhaustive = get_runtime_data('/results/obstacle_exhaustive')
    obs_exhaustive_sorting = get_runtime_data('/results/obstacle_exhaustive_sorting')
    obs_exhaustive_sorting_id = get_runtime_data('/results/obstacle_exhaustive_sorting_id')
    obs_heuristic = get_runtime_data('/results/obstacle_heuristic')
    obs_astar = get_runtime_data('/results/astar_obstacle')
    obs_mstar = get_runtime_data('/results/mstar_obstacle')
    obs_icts = get_runtime_data('/results/icts_obstacle')
    obs_cbs = get_runtime_data('/results/cbs_obstacle')

    # Goal assignment evaluations data
    obs_exhaustive_evaluations = get_evaluations_data('results/obstacle_exhaustive_evaluations')
    obs_exhaustive_sorting_evaluations = get_evaluations_data('results/obstacle_exhaustive_sorting_evaluations')

    # Memory usage data
    epeastar_memory = get_runtime_data('/results/epeastar_memory')
    astar_memory = get_runtime_data('/results/astar_memory')

    # Combine data for plots
    obs_1a = dict()
    obs_1a['Exhaustive'] = obs_exhaustive[1]
    obs_1a['Exhaustive with sorting'] = obs_exhaustive_sorting[1]
    obs_1a['Exhaustive with sorting and ID'] = obs_exhaustive_sorting_id[1]
    obs_1a['Heuristic'] = obs_heuristic[1]

    obs_3a = dict()
    obs_3a['Exhaustive'] = obs_exhaustive[3]
    obs_3a['Exhaustive with sorting'] = obs_exhaustive_sorting[3]
    obs_3a['Exhaustive with sorting and ID'] = obs_exhaustive_sorting_id[3]
    obs_3a['Heuristic'] = obs_heuristic[3]

    maze_1a = dict()
    maze_1a['Exhaustive'] = maze_exhaustive[1]
    maze_1a['Exhaustive with sorting'] = maze_exhaustive_sorting[1]
    maze_1a['Exhaustive with sorting and ID'] = maze_exhaustive_sorting_id[1]
    maze_1a['Heuristic'] = maze_heuristic[1]

    maze_3a = dict()
    maze_3a['Exhaustive'] = maze_exhaustive[3]
    maze_3a['Exhaustive with sorting'] = maze_exhaustive_sorting[3]
    maze_3a['Exhaustive with sorting and ID'] = maze_exhaustive_sorting_id[3]
    maze_3a['Heuristic'] = maze_heuristic[3]

    obs_1b = dict()
    obs_1b['CBS'] = obs_cbs[1]
    obs_1b['ICTS'] = obs_icts[1]
    obs_1b['A*+OD+ID'] = obs_astar[1]
    obs_1b['M*'] = obs_mstar[1]
    obs_1b['EPEA*'] = obs_exhaustive_sorting_id[1]

    obs_3b = dict()
    obs_3b['CBS'] = obs_cbs[3]
    obs_3b['ICTS'] = obs_icts[3]
    obs_3b['A*+OD+ID'] = obs_astar[3]
    obs_3b['M*'] = obs_mstar[3]
    obs_3b['EPEA*'] = obs_exhaustive_sorting_id[3]

    maze_1b = dict()
    maze_1b['CBS'] = maze_cbs[1]
    maze_1b['ICTS'] = maze_icts[1]
    maze_1b['A*+OD+ID'] = maze_astar[1]
    maze_1b['M*'] = maze_mstar[1]
    maze_1b['EPEA*'] = maze_exhaustive_sorting_id[1]

    maze_3b = dict()
    maze_3b['CBS'] = maze_cbs[3]
    maze_3b['ICTS'] = maze_icts[3]
    maze_3b['A*+OD+ID'] = maze_astar[3]
    maze_3b['M*'] = maze_mstar[3]
    maze_3b['EPEA*'] = maze_exhaustive_sorting_id[3]

    mem = dict()
    mem['A*+OD+ID'] = astar_memory[3]
    mem['EPEA*'] = epeastar_memory[3]

    assignment_eval = dict()
    assignment_eval['Exhaustive'] = obs_exhaustive_evaluations[1]
    assignment_eval['Exhaustive with sorting'] = obs_exhaustive_sorting_evaluations[1]

    # Create plots
    compare_percentage_solved(obs_1a, 'obstacle', 1, 'obs_1a')
    compare_percentage_solved(obs_3a, 'obstacle', 3, 'obs_3a')
    compare_percentage_solved(maze_1a, 'maze', 1, 'maze_1a')
    compare_percentage_solved(maze_3a, 'maze', 3, 'maze_3a')
    compare_percentage_solved(obs_1b, 'obstacle', 1, 'obs_1b')
    compare_percentage_solved(obs_3b, 'obstacle', 3, 'obs_3b')
    compare_percentage_solved(maze_1b, 'maze', 1, 'maze_1b')
    compare_percentage_solved(maze_3b, 'maze', 3, 'maze_3b')
    compare_memory(mem, 'maze', 3, 'memory_comparison')
    compare_goal_assignments(assignment_eval, 'Evaluated goal assignments on obstacle maps with agents in 1 team    ',
                             'goal_assignments')
