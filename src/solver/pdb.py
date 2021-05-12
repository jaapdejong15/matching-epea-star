from __future__ import annotations

from typing import Tuple, List, Dict, NewType
import itertools

from src.util.coordinate import Direction, Coordinate
from src.util.grid import Grid

"""
Row of a Pattern DataBase (PDB) table. Contains:
 - A move that applies to one or more agents (A direction for each agent)
 - A Δf value that represents the change in heuristic
"""
PDBRow = NewType('PDBRow', Tuple[Tuple[Direction, ...], int])

"""
Pattern Database (PDB) table of PDB rows
"""
PDBTable = NewType('PDBTable', List[PDBRow])


class PDB:

    def __init__(self, child_databases: List[SingleColorPDB] = None):
        self.cache: Dict[List[Coordinate], PDBTable] = dict()
        self.child_databases = child_databases

    def get(self, coords: List[Coordinate]) -> PDBTable:
        # Check if it is worth caching:
        for coords in coords:



        # Check if table has been calculated already
        cached = self.cache.get(coords, default=None)
        if cached is not None:
            return cached

        # Calculate new table
        osf_table = PDBTable(itertools.product(map(lambda x: x.get(coords), self.child_databases)))
        osf_table.sort(key=(lambda row: row[1]))
        print(f"Table size: {len(osf_table)}")

        # Store new table
        self.cache[coords] = osf_table
        return osf_table

class SingleColorPDB(PDB):

    def __init__(self, color, grid: Grid):
        super().__init__([color])
        self.grid = grid
        self.osf: List[List[PDBTable]] = []
        self.calculate_pdb(color)

    def calculate_pdb(self, color: int):
        """
        Calculates the Pattern DataBase (PDB) for the operator selection function
        :param color:
        :return:
        """
        heuristics = self.grid.heuristic[color]
        # For each location in the grid
        for y in range(self.grid.height):
            grid_row: List[PDBTable] = []
            for x in range(self.grid.width):
                h = heuristics[y][x]
                if h != float('inf'):
                    # If location is traversable, create OSF table
                    osf_table = self.generate_osf_table(x, y, h, color)
                    grid_row.append(osf_table)
                else:
                    # Don't add possible moves if on a non-traversable position
                    grid_row.append(PDBTable([]))
            self.osf.append(grid_row)

    def generate_osf_table(self, x: int, y: int, heuristic: int, color: int) -> PDBTable:
        """
        Generates an operator selection function (OSF) table for a single color and vertex in the grid
        :param x:               x-coordinate of the vertex
        :param y:               y-coordinate of the vertex
        :param heuristic:       heuristic for the color at the given (x,y).
        :param color:           color for the OSF
        :returns:               OSF table with Δf values for each move, sorted on Δf
        """
        pdb_table: List[PDBRow] = []
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            # For each possible move
            dx, dy = direction.value
            new_x: int = x + dx
            new_y: int = y + dy
            if self.grid.traversable_coords(new_x, new_y):
                # Only add move if it moves to a traversable position
                delta_f: int = 1 + self.grid.heuristic[color][new_y][new_x] - heuristic # Δf
                pdb_table.append(PDBRow((direction, delta_f)))

        pdb_table.append(PDBRow((Direction.WAIT, 1)))
        pdb_table.sort(key=(lambda row: row[1]))
        return PDBTable(pdb_table)

    def get(self, coords: List[Coordinate]) -> PDBTable:
        """
        Gets the pattern database table
        :param coords:  Coordinates of the position to get the table for
        :return:        Pattern Database Table
        """
        assert len(coords) == 1
        return self.osf[coords[0].y][coords[0].x]





