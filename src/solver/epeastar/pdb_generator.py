from typing import NewType, List, Tuple, Dict

from src.solver.epeastar.heuristic import Heuristic
from src.util.direction import Direction
from src.util.grid import Grid

PDBRow = NewType('PDBRow', Tuple[List[Direction], int])
PDBTable = NewType('PDBTable', List[PDBRow])


class PDB:
    """
    Pattern Database (PDB) that can be used by the operator selection function (OSF).
    """

    def __init__(self, heuristic: Heuristic, grid: Grid):
        """
        Creates and fills a Pattern Database
        :param heuristic:   Precomputed heuristic function
        :param grid:        2D grid of the problem
        """
        self.pdb: Dict[int, List[List[PDBTable]]] = dict()

        for color in heuristic.grouped_goals.keys():
            self.calculate_single_color_pdb(color, grid, heuristic)

    def calculate_single_color_pdb(self, color: int, grid: Grid, heuristic: Heuristic) -> None:
        """
        Precomputes the Pattern Database (PDB) for all agents of a single color.
        (or one agent in the case of MAPF / Exhaustive matching)
        :param color:       Color of the agent
        :param grid:        2D grid of the problem instance
        :param heuristic:   Precomputed heuristic function
        """
        single_color_osf: List[List[PDBTable]] = []
        for y in range(grid.height):
            osf_grid_row = []
            for x in range(grid.width):
                h = heuristic.heuristic[color][y][x]
                if h != float('inf'):
                    osf_table = self.generate_osf_table(grid, x, y, heuristic, color)
                    osf_grid_row.append(osf_table)
                else:
                    osf_grid_row.append(PDBTable([]))
            assert len(osf_grid_row) == grid.width
            single_color_osf.append(osf_grid_row)

        assert len(single_color_osf) == grid.height
        self.pdb[color] = single_color_osf

    def generate_osf_table(self, grid: Grid, x: int, y: int, heuristic: Heuristic, color: int) -> PDBTable:
        """
        Generates an operator selection function (OSF) table for a single color and vertex in the grid
        :param grid:            2D grid of the problem instance
        :param x:               x-coordinate of the vertex
        :param y:               y-coordinate of the vertex
        :param heuristic:       heuristic for the color at the given (x,y).
        :param color:           color for the OSF
        :returns:               OSF table with Δf values for each move, sorted on Δf
        """
        location_heuristic = heuristic.heuristic[color][y][x]
        expanded_table = []
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            dx, dy = direction.value
            new_x: int = x + dx
            new_y: int = y + dy
            if grid.traversable_coords(new_x, new_y):
                delta_f: int = 1 + heuristic.heuristic[color][new_y][new_x] - location_heuristic
                expanded_table.append((direction, delta_f))

        expanded_table.append((Direction.WAIT, 1))
        expanded_table.sort(key=(lambda row: row[1]))  # Sorting is very important for the algorithm in operator_finder
        return PDBTable(self.collapse_osf_table(expanded_table))

    @staticmethod
    def collapse_osf_table(table: List[Tuple[Direction, int]]) -> PDBTable:
        """
        Collapses directions with the same Δf value into the same row
        :param table:   Table sorted on Δf value
        :return:        Collapsed table sorted on Δf value
        """
        if len(table) == 0:
            print("Empty table")
            return PDBTable([])

        osf_table = []
        last_df = table[0][1]
        last_directions: List[Direction] = [table[0][0]]
        for direction, df in table[1:]:
            if df == last_df:
                last_directions.append(direction)
            else:
                osf_table.append(PDBRow((last_directions, last_df)))
                last_directions = [direction]
                last_df = df
        osf_table.append(PDBRow((last_directions, last_df)))
        return PDBTable(osf_table)
