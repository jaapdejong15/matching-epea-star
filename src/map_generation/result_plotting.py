from typing import List

from matplotlib import pyplot as plt


def get_data(name: str, num_teams: int) -> List[List[float]]:
    with open(f'../../results/{name}.txt') as f:
        data = []
        for i in range(num_teams):
            data.append([None] * i)
        for l in f:
            line = l.split(' ')
            value = float(line[1])
            team = int(line[0][-2])
            data[team - 1].append(value)
    return data


def line_plot(data: List[List[float]]):
    font = {'fontname': 'Consolas'}
    fig = plt.figure()
    fig.patch.set_facecolor('#D9D9D9')

    x = range(1, len(data[0]) + 1)
    for i, row in enumerate(data):
        plt.plot(x, row, label=f'{i + 1} team{"" if i + 1 == 1 else "s"}')

    plt.title('Exhaustive matching performance for different amounts of teams', font)
    plt.xlabel('Number of agents', font)
    plt.ylabel('Fraction of problems solved within 30 seconds', font)

    plt.legend()
    plt.show()


if __name__ == '__main__':
    line_plot(get_data('results-20210514-110335', 4))
