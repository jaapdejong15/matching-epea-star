# MAPF with Matching using EPEA*

## A*
A* is a search algorithm that uses a heuristic function to prioritize promising places to search.
In MAPF, there are several heuristics possible, such as
- Sum of Manhattan distances from all agents to their goals
- Sum of shortest path distance from all agents to their goals

Every state (combination of agent positions) corresponds to a node in A*
Every node has its own cost (what it costs to reach the node) and heuristic (estimated cost to the goal)
The node with the lowest cost+heuristic is evaluated first.
This can be done using a [priority queue](https://en.wikipedia.org/wiki/Priority_queue).

Several child nodes can be created by applying operators. 
For example, for one agent, an operator could be `move to the right`.
For multiple agents, it is the cartesian product of all operators of the individual agents.

## PEA*
Partial Expansion A* improves the memory efficiency of A* by reducing the queue size.
This is done by collapsing less promising nodes, i.e. with a low `cost+heuristic`, into their parent node. 

## ID

## EPEA*

# Credits
Thanks to [Ivar de Bruin](https://github.com/ivardb) for helping with [ID and A*](https://github.com/ivardb/Astar-OD-ID):