import itertools
from typing import List, Tuple

from src.astar.agent import Agent
from src.astar.state import State
from src.util.grid import Grid


class MAPFProblem:
    def __init__(self, agents: List[Agent], grid: Grid, goals):
        self.agents = agents
        self.grid = grid
        self.goals = goals

    def on_goal(self, agent: Agent) -> bool:
        for goal in self.goals:
            if goal.x == agent.coord.x and goal.y == agent.coord.y and goal.color == agent.color:
                return True
        return False

    def heuristic(self, state: State) -> int:
        heuristic = 0
        if self.grid.calculate_heuristic:
            for agent in state.agents:
                heuristic += self.grid.heuristic[agent.color][agent.coord.y][agent.coord.x]
        else:
            # Sum of distance to closest goal of same color for each agent
            for agent in state.agents:
                goal_distance = float('inf')
                for goal in self.goals:
                    if goal.color == agent.color:
                        goal_distance = min(goal_distance, abs(agent.coord.x - goal.x) + abs(agent.coord.y - goal.y))
                heuristic += goal_distance
        return heuristic

    def is_solved(self, state) -> bool:
        return all(self.on_goal(agent) for agent in state.agents)

    def expand(self, state: State) -> List[Tuple[State, int]]:
        agents_moves = []
        for agent in state.agents:
            agent_moves = [(Agent(neighbor, agent.color), 1 + agent.waiting_cost) for neighbor in
                           self.grid.get_neighbors(agent.coord)]
            if self.on_goal(agent):
                agent_moves.append((Agent(agent.coord, agent.color, agent.waiting_cost + 1), 0))
            else:
                agent_moves.append((Agent(agent.coord, agent.color), 1 + agent.waiting_cost))
            agents_moves.append(agent_moves)

        possible_moves = itertools.product(*agents_moves)

        # Check constraints
        states = []
        for move in possible_moves:
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
