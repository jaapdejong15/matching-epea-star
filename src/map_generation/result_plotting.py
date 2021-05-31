import re
from typing import List

from matplotlib import pyplot as plt


def get_data(name: str):
    with open(f'../../{name}.txt') as f:
        data = []
        for line in f.readlines():
            matches: List[re.Match] = re.findall(
                f'^\w+-\d+x\d+-A(\d+)_T(\d+): \w+: (\d+.\d+|nan), [\w ]+: (\d+.\d+|nan), [\w ]+: (\d+.\d+|nan)$', line)
            data.append((int(matches[0][0]),
                         int(matches[0][1]),
                         float(matches[0][2]),
                         float(matches[0][3]),
                         float(matches[0][4]))
                        )
    return data


def split_teams(data, parameter, num_agents):
    res = ([float('nan')] * num_agents, [float('nan')] * num_agents)
    for row in data:
        if row[1] == 1:
            res[0][row[0] - 1] = row[parameter]
        elif row[1] == 3:
            res[1][row[0] - 1] = row[parameter]
    return res


def line_plot(data, num_agents, maze_type, plot_type='completed'):
    font = {'fontname': 'Consolas'}
    fig, ax1 = plt.subplots()
    fig.patch.set_facecolor('#D9D9D9')

    if plot_type == 'completed':
        t1, t3 = split_teams(data, 2, num_agents)
        t11, t31 = split_teams(data, 3, num_agents)
        x = range(1, num_agents + 1)

        print(f"x: {len(x)}\nt1: {len(t1)}\nt3: {len(t3)}")

        ax1.set_xlabel('Number of agents')
        ax1.set_ylabel('Fraction of problems solved within 30 seconds')
        ax1.plot(x, t1, label=f'amount solved (1 team)', color='#0000ff', linestyle='--')
        ax1.plot(x, t3, label=f'amount solved (3 teams)', color='#ff0000', linestyle='--')
        ax1.legend(loc=(0, 0.4))

        ax2 = ax1.twinx()
        plt.ylim([0, 30])
        ax2.set_ylabel('Average runtime (s)')
        ax2.plot(x, t11, label=f'average runtime (1 team)', color='#5555ff')
        ax2.plot(x, t31, label=f'average runtime (3 teams)', color='#ff5555')
        ax2.legend(loc=(0, 0.6))

    plt.title(f'Heuristic matching performance for {maze_type} maps', font)

    plt.show()


if __name__ == '__main__':
    line_plot(get_data('results/HEU-maze0'), 10, 'maze')
