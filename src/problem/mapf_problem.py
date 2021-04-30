import itertools
from typing import List, Tuple

from src.astar.agent import Agent
from src.astar.state import State
from src.util.grid import Grid


class MAPFProblem:
    def __init__(self, grid: Grid):
        self.grid = grid

    def on_goal(self, agent: Agent) -> bool:
        for goal in self.grid.goals:
            if goal.x == agent.coord.x and goal.y == agent.coord.y and goal.color == agent.color:
                return True
        return False

    def is_solved(self, state) -> bool:
        return all(self.on_goal(agent) for agent in state.agents)

    def expand(self, state: State) -> List[Tuple[State, int]]:
        agents_moves = []
        for agent in state.agents:
            agent_moves = [(Agent(neighbor, agent.color, i), 1 + agent.waiting_cost) for i, neighbor in
                           enumerate(self.grid.get_neighbors(agent.coord))]
            if self.on_goal(agent):
                agent_moves.append(
                    (Agent(agent.coord, agent.color, agent.identifier, waiting_cost=agent.waiting_cost + 1), 0))
            else:
                agent_moves.append((Agent(agent.coord, agent.color, agent.identifier), 1 + agent.waiting_cost))
            agents_moves.append(agent_moves)

        operators = itertools.product(*agents_moves)

        # Check constraints
        states = []
        for move in operators:
            coords = set()
            edge_conflict = False
            vertex_conflict = False
            for i, (agent, cost) in enumerate(move):
                # Check vertex conflict
                if agent.coord in coords:
                    vertex_conflict = True
                    break
                coords.add(agent.coord)

                # Check edge conflicts
                for j in range(i + 1, len(state.agents)):
                    if move[i][0].coord == state.agents[j].coord and move[j][0].coord == state.agents[i].coord:
                        edge_conflict = True
                        break
                if edge_conflict:
                    break

            if (not vertex_conflict) and (not edge_conflict):
                agents = []
                added_cost = 0
                for agent, agent_cost in move:
                    agents.append(agent)
                    added_cost += agent_cost
                move = State(agents)
                states.append((move, added_cost))
        return states

    def heuristic(self, state):
        total = 0
        for agent in state.agents:
            total += self.grid.heuristic[agent.color][agent.coord.y][agent.coord.x]
        return total