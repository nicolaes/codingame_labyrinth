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
control: Union[Point, None] = None

def log(*args):
    print(*args, file=sys.stderr, flush=True)

def in_range(center, to):
    rx, ry = sub_loc(center, to)
    return abs(rx) <= 2 and abs(ry) <= 2

def add_loc(dir1, dir2):
    return (dir1[0] + dir2[0], dir1[1] + dir2[1])

def sub_loc(dir1, dir2):
    return (dir1[0] - dir2[0], dir1[1] - dir2[1])

def first_undiscovered_direction(map: Map, rick_loc: Loc):
    rick_frontier = FrontierPoint(rick_loc, None)

    frontier: queue.SimpleQueue[FrontierPoint] = queue.SimpleQueue()
    frontier.put(rick_frontier)
    reached: set[Loc] = set()
    reached.add(rick_loc)

    while not frontier.empty():
        current = frontier.get()
        
        if map[current.loc].c == "?":
            return current.used_direction

        for direction in directions_around(map, current.loc, lambda c, _: c in {'.', 'T', '?'}):
            next_loc = add_loc(current.loc, direction)
            if next_loc not in reached:
                # A* params
                next_map_point = map[next_loc]
                if not next_map_point.coming_from or \
                        cast(int, next_map_point.steps_to_start) > \
                        cast(int, map[current.loc].steps_to_start) + 1:
                    next_map_point.coming_from = map[current.loc]
                    next_map_point.steps_to_start = cast(int, map[current.loc].steps_to_start) + 1

                # Add next frontiers
                next_frontier_point = FrontierPoint(next_loc, \
                    current.used_direction if current.used_direction else direction)
                frontier.put(next_frontier_point)
                reached.add(next_loc)

    return None

    # > for frontier (start at current position)
    # >   if is_question_mark, return "used_direction"
    # >   get next frontiers (., ? or T - starting point)
    # >   if not MapPoint.coming_from and MapPoint.steps_to_start: compute it
    # >   if not FrontierPoint.coming_from and FrontierPoint.steps_to_start: compute it
    # >   create new FrontierPoint (only has "used_direction") and add it to queue
    #       steps_to_start is not required anymore, because FrontierPoint is computet at every iteration
    #       so you can't get to that point in any better way

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
    
    if start.c == "-":
        start = map[rick_loc]
        start.coming_from = start
        start.steps_to_start = 0

    # Discover
    next_dir = first_undiscovered_direction(map, rick_loc)
    
    # Plan each round:
    # > ### 1. Exploration: get next step
    # > get next frontier (., ? or T - starting point)
    # >   if not Point.coming_from and Point.steps_to_start: compute it
    # >   if is_question_mark, go in this direction:
    #        track the "coming_from" of current point until RICK, then compute direction
    # >   add next frontiers

    # 2. Go to control point
    # 3. Track back to T using "coming_from"

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # Rick's next move (UP DOWN LEFT or RIGHT).
    print(commands[next_dir])
