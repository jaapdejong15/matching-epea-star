from typing import NewType, List, Tuple, Dict

from src.util.direction import Direction

OSFRow = NewType('OSFRow', Tuple[List[Direction], int])
OSFTable = NewType('OSFTable', List[OSFRow])


class OSF:

    def __init__(self, grid):
        self.osf: Dict[int, List[List[OSFTable]]] = dict()

        for color in grid.colors.keys():
            self.calculate_single_color_osf(color, grid)


    def calculate_single_color_osf(self, color, grid) -> None:
        """
        Precomputes the operator selection function (OSF) for individual agents.
        Results are stored in self.osf

        """
        single_color_osf: List[List[OSFTable]] = []
        for y in range(grid.height):
            osf_grid_row = []
            for x in range(grid.width):
                h = grid.heuristic[color][y][x]
                if h != float('inf'):
                    osf_table = self.generate_osf_table(x, y, h, color, grid)
                    osf_grid_row.append(osf_table)
                else:
                    osf_grid_row.append(OSFTable([]))
            assert len(osf_grid_row) == grid.width
            single_color_osf.append(osf_grid_row)

        assert len(single_color_osf) == grid.height
        self.osf[color] = single_color_osf

    def generate_osf_table(self, x: int, y: int, heuristic: int, color: int, grid) -> OSFTable:
        """
        Generates an operator selection function (OSF) table for a single color and vertex in the grid
        :param grid:
        :param x:               x-coordinate of the vertex
        :param y:               y-coordinate of the vertex
        :param heuristic:       heuristic for the color at the given (x,y).
        :param color:           color for the OSF
        :returns:               OSF table with Δf values for each move, sorted on Δf
        """
        expanded_table = []
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            dx, dy = direction.value
            new_x: int = x + dx
            new_y: int = y + dy
            if grid.traversable_coords(new_x, new_y):
                delta_f: int = 1 + grid.heuristic[color][new_y][new_x] - heuristic
                expanded_table.append((direction, delta_f))

        expanded_table.append((Direction.WAIT, 1))
        expanded_table.sort(key=(lambda row: row[1]))  # Sorting is very important for the algorithm in operator_finder
        return OSFTable(self.collapse_osf_table(expanded_table))

    @staticmethod
    def collapse_osf_table(table: List[Tuple[Direction, int]]) -> OSFTable:
        """
        Collapses directions with the same Δf value into the same row
        :param table:   Table sorted on Δf value
        :return:        Collapsed table sorted on Δf value
        """
        if len(table) == 0:
            print("Empty table")
            return OSFTable([])

        osf_table = []
        last_df = table[0][1]
        last_directions: List[Direction] = [table[0][0]]
        for direction, df in table[1:]:
            if df == last_df:
                last_directions.append(direction)
            else:
                osf_table.append(OSFRow((last_directions, last_df)))
                last_directions = [direction]
                last_df = df
        osf_table.append(OSFRow((last_directions, last_df)))
        return OSFTable(osf_table)