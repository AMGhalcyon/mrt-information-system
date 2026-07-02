# MRT Information System

A terminal-based MRT route planning and visualisation tool for Singapore's rail network. It parses real station, line, and fare data into a weighted graph, computes routes using Dijkstra-style search, and renders the resulting path with live Turtle graphics - complete with line colours, interchanges, and station labels.

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Shortest-distance route** | Finds and visualises the route minimising total km travelled |
| 2 | **Estimated travel time** | Computes journey duration based on per-line speeds |
| 3 | **Fare calculator** | Looks up Adult / Student / Senior fare based on distance slabs |
| 4 | **Last train feasibility** | Checks whether a journey starting at a given time can be completed before the last train on each line/interchange |
| 5 | **First train timing** | Reports the earliest possible departure time from the start station |
| 6 | **Minimum travel-time route** | Runs a separate search optimising for time rather than distance |
| 7 | **Stations reachable within a time limit** | Walks the shortest path and lists every station reachable within a user-given number of minutes |
| 8 | **Interchange detection** | Lists every line change along the computed route |
 
All options are driven from a single interactive menu, and any route-drawing option opens a Turtle window showing the path, colour-coded by line, with interchange stations displayed cleanly.


## How it Works
**Data model** - `load_mrt_data()` parses a semicolon-delimited station/line file into three structures:
- `stations`: station -> codes, lines served and neighbour edges
- `code_to_name`: station code (e.g. `NS1`) -> full station name
- `lines`: line name -> list of connected station pairs

**Station lookup** — `match_station()` resolves user input against station codes, exact names, and name prefixes, verifying interactively when multiple stations match.
 
**Pathfinding** — `graph_builder()` turns the parsed data into an ordered list. Routes are computed with a priority-queue search (`a_star` / `a_star_min_time`) with heuristic `h(n) = 0`, which makes it functionally **Dijkstra's algorithm** run once over distance weights and once over time weights (computed from each line's given speed).
 
**Fares** — `load_fare()` parses tiered fare tables per passenger type, and `get_fare()` matches total route distance to the correct fare category.
 
**Timetable checks** — first/last train times are parsed per edge and per direction, with `check_last_train()` walking the route leg-by-leg to verify feasibility against boarding and interchange cut-off times.
 
**Visualisation** — `draw_path()` lays the route out left-to-right, shifting vertically at each interchange, and draws it with Turtle, colouring each segment by line.

##  Supported Lines
 
| Line | Colour | Speed (km/h) |
|------|--------|--------------|
| North-South | Red | 41 |
| East-West | Green | 43 |
| Circle | Orange | 36 |
| Downtown | Blue | 38 |
| North East | Purple | 34 |
| Thomson-East Coast | Brown | 40 |


## Getting Started

> File paths are resolved relative to the script's own location, so `MRT.txt` and `FareStructure.txt` must sit alongside `dec_mini_project.py`

### Prerequisites 
- Python 3.x ( Turtle graphics ships with the standard library)

### Run it

```bash
git clone https://github.com/AMGhalcyon/mrt-information-system.git
cd mrt-information-system/source
python dec_mini_project.py
```

You will be dropped into an interactive menu:

```
MRT INFORMATION SYSTEM
1. Shortest-distance route
2. Estimated travel time
3. Fare between stations
4. Last train feasibility
5. First train timing
6. Path with Minimum Travel Time
7. Stations reachable within time limit on shortest path
8. Interchange stations on route
0. Exit
```
 
Enter a station **name, prefix, or code** (e.g. `Jurong East`, `jur`, or `NS1`) when prompted — the system will clarify for you if there's more than one match.

##  Data File Format
 
**`MRT.txt`** (semicolon-delimited, one connection per line):
```
No.;Station Pair;Line;Distance(km);First Train;Last Train;First Train (Opp);Last Train (Opp)
1;NS1 Jurong East<->NS2 Bukit Batok;North-South;2.3;0530;2359;0530;2359
```
 
**`FareStructure.txt`** (grouped by passenger type, each with distance-band slabs):
```
Adult Fare
Up to 3.2 km;120
3.2 - 4.2 km;130
Over 40.2 km;250
```
 
 ## Built With
- **Python** - entirety of the codebase
- **`heapq`** - priority-queue-based Dijkstra search
- **`turtle`** - route visualisation

## Notes

This project was built as an exercise to understand graph algorithms - the core shortest-path search was developed with AI assistance while the author was learning the technique, and the visualisation was similarly AI-assisted for display polish. Core data modelling, parsing, dare/timetable logic, and the menu system are original.

---

*An exploration of graph-based pathfinding applied to a real-world transit network*
