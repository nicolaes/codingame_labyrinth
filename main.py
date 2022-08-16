from __future__ import annotations
import sys
import queue
from typing import Optional, Union, cast
import numpy as np
from dataclasses import dataclass

Loc = tuple[int, int]

@dataclass
class Point:
    c: str
    loc: Loc
    coming_from: Optional[Point] = None
    steps_to_start: Optional[int] = None

@dataclass
class FrontierPoint:
    loc: Loc
    used_direction: Optional[Loc]

Map = dict[Loc, Point]

all_directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
commands = dict(zip(all_directions, ["LEFT", "DOWN", "RIGHT", "UP"]))

# Globals: start
start: Point = Point('-', (0, 0))

def log(*args):
    print(*args, file=sys.stderr, flush=True)

def add_loc(dir1, dir2):
    return (dir1[0] + dir2[0], dir1[1] + dir2[1])

def sub_loc(dir1, dir2):
    return (dir1[0] - dir2[0], dir1[1] - dir2[1])

def discover_and_reach_control(map: Map, rick_loc: Loc, back_to_start = False) -> Optional[Loc]:
    rick_frontier = FrontierPoint(rick_loc, None)

    frontier: queue.SimpleQueue[FrontierPoint] = queue.SimpleQueue()
    frontier.put(rick_frontier)
    reached: set[Loc] = set()
    reached.add(rick_loc)

    # Remember if current search includes the Control point
    control_frontier: Optional[FrontierPoint] = None
    
    while not frontier.empty():
        current = frontier.get()
        
        if map[current.loc].c == "?":
            # Go to first undiscovered direction
            return current.used_direction

        if back_to_start and map[current.loc].c == 'T':
            return current.used_direction

        for direction in directions_around(map, current.loc, \
                lambda c, _: c != '#'):
            next_loc = add_loc(current.loc, direction)
            next_map_point = map[next_loc]

            if next_loc not in reached:
                # A* params
                if not next_map_point.coming_from or \
                        cast(int, next_map_point.steps_to_start) > \
                        cast(int, map[current.loc].steps_to_start) + 1:
                    next_map_point.coming_from = map[current.loc]
                    next_map_point.steps_to_start = cast(int, map[current.loc].steps_to_start) + 1

                
                reached.add(next_loc)
                next_frontier_point = FrontierPoint(next_loc, \
                    current.used_direction if current.used_direction else direction)
                if next_map_point.c != 'C':
                    # Add next frontier
                    # Don't go to C until rest is explored
                    frontier.put(next_frontier_point)    
                else:
                    control_frontier = next_frontier_point

    # If no undiscovered point was found, send Rick to control
    if control_frontier != None:
        return control_frontier.used_direction

    return None

def directions_around(map: Map, rick: Loc, point_filter = None):
    directions = []
    for direction in all_directions:
        next_loc = add_loc(rick, direction)
        if next_loc in map and \
            (point_filter == None or point_filter(map[next_loc].c, next_loc)):
            directions.append(direction)
    return directions


# r: number of rows.
# c: number of columns.
# a: number of rounds between the time the alarm countdown is activated and the time the alarm goes off.
r, c, a = [int(i) for i in input().split()]

# game loop
is_discovery_mode = True # if not, it's going back to start
map = dict()
while True:
    # kr: row where Rick is located.
    # kc: column where Rick is located.
    kr, kc = [int(i) for i in input().split()]
    rick_loc = (kc, kr)
    
    for map_y in range(r):
        for map_x, point_char in enumerate(input()):
            map_loc = (map_x, map_y)
            if map_loc not in map:
                map[map_loc] = Point(point_char, map_loc)
            elif map[map_loc].c != point_char:
                map[map_loc].c = point_char

    # Get start on first round
    if start.c == "-":
        start = map[rick_loc]
        start.coming_from = start
        start.steps_to_start = 0
    
    next_dir: Optional[Loc] = None
    if is_discovery_mode and map[rick_loc].c != 'C':
        next_dir = discover_and_reach_control(map, rick_loc)
    else:
        # This means all labyrinth was discovered, and Rick reached control
        # Switch to retreat mode
        is_discovery_mode = False
        next_dir = discover_and_reach_control(map, rick_loc, True)
    
    
    # Rick's next move (UP DOWN LEFT or RIGHT).
    print(commands[next_dir])
