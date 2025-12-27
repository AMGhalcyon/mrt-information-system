
"""
MRT INFORMATION SYSTEM

@author: anish
"""

import os
import heapq
import turtle

SCREEN = turtle.Screen()
SCREEN.title("MRT Route Visualisation")
SCREEN.bgcolor("white")
SCREEN.setup(width=1200, height=700)


line_speeds = {
    "North-South": 41,
    "East-West": 43,
    "Circle": 36,
    "Thomson-East Coast": 40,
    "North East": 34,
    "Downtown": 38}
LINE_COLORS = {
    "North-South": "red",
    "East-West": "green",
    "Circle": "orange",
    "Downtown": "blue",
    "North East": "purple",
    "Thomson-East Coast": "brown"
}


def get_file_path(filename):
    
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    return os.path.join(script_dir, filename)

#will use 3 dictionaries as my data structure
def load_mrt_data(file_name):
    
    stations = {}
    code_to_name = {}
    lines = {}
    
    file = get_file_path(file_name)
    with open(file, 'r') as f:
        next(f) #skips first header line
        
        for line in f:
            line = line.strip()
            
            if not line:
                continue
            
            parts = line.split(';')
            
            if len(parts) != 8:
                continue  #as there should be eight items 
                
            num, pair, line_name, dist, first, last, first_opp, last_opp = parts
            try:
                dist = float(dist)
            except ValueError:   #to escape the nextg header line, as string cannot be converted to float
                continue
            
            c1_and_s1, c2_and_s2 = pair.split('<->')
            c1_and_s1 = c1_and_s1.strip()
            c2_and_s2 = c2_and_s2.strip()
            
            c1, s1 = c1_and_s1.split(' ', 1)
            c2, s2 = c2_and_s2.split(' ', 1)
            
            for st, code in [(s1,c1), (s2,c2)]:  #adding data in stations and code_to_name
                if st not in stations:
                    stations[st] = {
                        'codes': [],
                        'lines': set(),
                        "neighbours": []
                        }
                    
                if code not in stations[st]['codes']:
                    stations[st]['codes'].append(code)
                code_to_name[code] = st
                
                
            #now adding line information
            
            stations[s1]['lines'].add(line_name)
            stations[s2]['lines'].add(line_name)
            
            if line_name not in lines:
                lines[line_name] = []
            lines[line_name].append((s1,s2))
            
            stations[s1]["neighbours"].append({
                "station": s2,
                "distance": dist,
                "line": line_name,
                "first_train": first,
                "last_train": last,
                "first_opp": first_opp,
                "last_opp": last_opp
            })

            stations[s2]["neighbours"].append({
                "station": s1,
                "distance": dist,
                "line": line_name,
                "first_train": first_opp,
                "last_train": last_opp,
                "first_opp": first,
                "last_opp": last
            })
            
            
    for st in stations:
        stations[st]['lines'] = list(stations[st]['lines'])
        
    return stations, code_to_name, lines


#now for matching stations from codes, names and prefixes
def text_normal(text):
    return text.strip().lower()


def match_station(user_input, stations, code_to_name):
    user_input = user_input.strip()
    
    if user_input.upper() in code_to_name:
        return code_to_name[user_input.upper()]
    
    key = text_normal(user_input)
    
    for st in stations:
        if text_normal(st) == key:
            return st
        
    matches = [st for st in stations if text_normal(st).startswith(key) ]
    
    return matches

def resolve_match_from_user(prompt, stations, code_to_name):
    while True:
        user_input = input(prompt)
        result = match_station(user_input, stations, code_to_name)

        if isinstance(result, str):
            return result

        if len(result) == 0:
            print("Station not found. Try again.")
        elif len(result) == 1:
            return result[0]
        else:
            print("Ambiguous. Did you mean:")
            for i, st in enumerate(result, 1):
                print(f"{i}. {st}")

            try:
                choice = int(input("Choose number: "))
                if 1 <= choice <= len(result):
                    return result[choice - 1]
            except:
                pass
        
        
        
        

#Build graph for A* algorithm

def graph_builder(stations):
    graph = {}

    for st in stations:
      graph[st] = []
      for n in stations[st]["neighbours"]:
          graph[st].append({
              "to": n["station"],
              "distance": n["distance"],
              "line": n["line"],
              "first": n["first_train"],
              "last": n["last_train"],
              "first_opp": n["first_opp"],
              "last_opp": n["last_opp"]
          })

    return graph
    

#fare structure loading into data structures for usage

def load_fare(filename):
    fares = {}
    current = None 
    
    file = get_file_path(filename)
    
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "Adult Fare" in line:
                current = "Adult"
                fares[current] = []
                next(f)
            elif "Senior Citizen" in line:
                current = "Senior"
                fares[current] = []
                next(f)
            elif "Student Fare" in line:
                current = "Student"
                fares[current] = []
                next(f)
            elif ";" in line and current:
                fares[current].append(line)
    return fares
        

#used AI's help for developing core algorithm as I am learning this algorithm too
#core logic below
def a_star(graph, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_cost = {start:0}
    visited = set()
    
    while open_set:
        current_f, current = heapq.heappop(open_set)

        if current in visited:
            continue

        visited.add(current)  #because it is a set

        # Goal reached
        if current == goal:
            return reconstruct_path(came_from, start, goal), g_cost[goal]

        for edge in graph[current]:
            neighbour = edge["to"]
            distance = edge["distance"]

            tentative_g = g_cost[current] + distance

            if neighbour not in g_cost or tentative_g < g_cost[neighbour]:
                g_cost[neighbour] = tentative_g
                came_from[neighbour] = current

                # h(n) = 0
                f_cost = tentative_g
                heapq.heappush(open_set, (f_cost, neighbour))

    return None, float("inf")


#giving entire path
def reconstruct_path(came_from, start, goal):
    path = [goal]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return path


#computing travel time
def compute_travel_time(path, graph, line_speeds):
    total_time_hours = 0.0
    for i in range(len(path)-1):
        current = path[i]
        next_node = path[i+1]
        for edge in graph[current]:
            if edge["to"] == next_node:
                speed = line_speeds[edge["line"]]
                total_time_hours += edge["distance"]/ speed
                break
    return total_time_hours * 60 #get travel time in minutes


#parsing fare slabs to get required fare for a specific route
def parse_fare_slabs(fare_lines):
    slabs = []
    for line in fare_lines:
        dist_part, cost = line.split(';')
        cost = int(cost)
        
        if 'Up to' in dist_part:
            max_d = float(dist_part.split()[2])
            slabs.append((0, max_d, cost))

        elif "Over" in dist_part:
           min_d = float(dist_part.split()[1])
           slabs.append((min_d, float("inf"), cost))

        else:
           a, b = dist_part.split("-")
           min_d = float(a.split()[0])
           max_d = float(b.split()[0])
           slabs.append((min_d, max_d, cost))

    return slabs

def get_fare(distance, fare_table, passenger_type="Adult"):
    slabs = parse_fare_slabs(fare_table[passenger_type])

    for low, high, cost in slabs:
        if low <= distance <= high:
            return cost

    return None


            
            

#menu skeleton
def print_menu():
    print("\nMRT INFORMATION SYSTEM")
    print("1. Shortest-distance route")
    print("2. Estimated travel time")
    print("3. Fare between stations")
    print("4. Last train feasibility")
    print("5. First train timing")
    print("6. Path with Minimum Travel Time")
    print("7. Stations reachable within time limit on shortest path")
    print("8. Interchange stations on route")
    print("0. Exit")
    
#Query 1
def handle_shortest_route(path, graph, total_distance):
    print("\nShortest-distance route:")

    previous_line = None

    for i in range(len(path) - 1):
        current = path[i]
        next_station = path[i + 1]

        # get the edge used
        for edge in graph[current]:
            if edge["to"] == next_station:
                line = edge["line"]
                break

        if i == 0:
            print(f"Start on {line} Line from {current}")
        else:
            if line != previous_line:
                print(f"→ {current} [INTERCHANGE to {line} Line]")
            else:
                print(f"→ {current}")

        previous_line = line

    # print final station
    print(f"→ {path[-1]}\n")
    
    print(f"Total Distance: {total_distance:.2f} km")
    
    draw_path(path, graph)
    

#Query 2
def handle_travel_time(path, graph):
    time = compute_travel_time(path, graph, line_speeds)
    print(f"\nEstimated travel time: {time:.1f} minutes")
    print()
    

#Query 3
def get_passenger_type():
    while True:
        p = input("Passenger type (Adult/Student/Senior): ").strip().capitalize()
        if p in ("Adult", "Student", "Senior"):
            return p
        print("Invalid type. Try again.")

def handle_fare_query(path, total_distance, fares):
    p_type = get_passenger_type()
    fare = get_fare(total_distance, fares, p_type)

    print(f"\nPassenger type: {p_type}")
    print(f"Distance travelled: {total_distance:.2f} km")
    print(f"Fare: {fare} cents")
    

#Query 4
def time_to_minutes(t):
    return int(t[:2])*60 + int(t[2:])


def adjust_train_time(time_str):
    minutes = time_to_minutes(time_str)
    if time_str.startswith("00"):
        minutes += 1440
    return minutes

def check_last_train(path, graph, start_time, line_speeds):
    current_time = adjust_train_time(start_time)
    current_line = None

    for i in range(len(path) - 1):
        current = path[i]
        next_station = path[i + 1]

        edge_used = None
        for edge in graph[current]:
            if edge["to"] == next_station:
                edge_used = edge
                break

        if edge_used is None:
            return False, "No path found"

        next_line = edge_used["line"]

        # Check last train ONLY when boarding or interchanging
        if current_line != next_line:
            last_train_time = adjust_train_time(edge_used["last"])

            if current_time > last_train_time:
                return False, (
                    f"Missed last train when boarding {next_line} Line at {current} "
                    f"(last train {edge_used['last']})"
                )

            current_line = next_line  # boarded new line

        # travel happens AFTER boarding
        speed = line_speeds[next_line]
        travel_time = (edge_used["distance"] / speed) * 60
        current_time += travel_time

    return True, "Journey possible before last train!"


def handle_last_train_feasibility(path, graph):
    start_time = input("Enter departure time (HHMM): ").strip()
    
    possible, message = check_last_train(path, graph, start_time, line_speeds)
    
    if possible:
        print(message)
        print()
    
    else:
        print("Journey not feasible")
        print("Reason: ", message)
        print()
    

#Query 5
def handle_first_train_query(path, graph):
    start = path[0]
    next_station = path[1]
    edge_used = None
    
    for edge in graph[start]:
        if edge['to'] == next_station:
            edge_used = edge
            break
    if edge_used is None:
        print('No connection from start to next station\n')
        return
    
    first_time_string = edge_used['first']
    
    first_time_minutes = adjust_train_time(first_time_string)
    
    hours = first_time_minutes // 60
    minutes = first_time_minutes % 60
    
    print(f"Earliest train from {start} is at {hours:02d}:{minutes:02d} on {edge['line']} line")
    

#Query 6
#for this query I had to use a A* variant to find minimum time path
def a_star_min_time(graph, start, goal, line_speeds):
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_cost = {start:0}
    visited = set()
    
    while open_set:
        current_f, current = heapq.heappop(open_set)
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current == goal:
            return reconstruct_path(came_from, start, goal), g_cost[goal]
        
        for edge in graph[current]:
            neighbour = edge['to']
            speed = line_speeds[edge['line']]
            
            time_cost = (edge['distance']/speed) * 60
            tentative_g = g_cost[current] + time_cost
            
            if neighbour not in g_cost or tentative_g < g_cost[neighbour]:
                g_cost[neighbour] = tentative_g
                came_from[neighbour] = current
                
                #h(n) = 0 is Dijkstra in time domain
                heapq.heappush(open_set, (tentative_g, neighbour))
    
    return None, float("inf")

def handle_min_time_query(graph, stations, start, end):
    path, total_time = a_star_min_time(graph, start, end, line_speeds)
    
    if path is None:
        print("No route found.")
    
    previous_line = None
    
    for i in range(len(path) - 1):
        current = path[i]
        next_station = path[i+1]
        
        for edge in graph[current]:
            if edge['to'] == next_station:
                line = edge['line']
                break
            
        if i == 0:
            print(f"Start on {line} Line from {current}")
        
        else:
            if line != previous_line:
                print(f"→ {current} [INTERCHANGE to {line} Line]")
            else:
                print(f"→ {current}")

        previous_line = line

    print(f"→ {path[-1]}")
    print(f"\nEstimated travel time: {total_time:.1f} minutes")
    draw_path(path, graph)

#Query 8
def handle_interchange_query(path, graph):
    interchanges = []
    previous_line = None

    for i in range(len(path) - 1):
        current = path[i]
        next_station = path[i + 1]

        for edge in graph[current]:
            if edge["to"] == next_station:
                line = edge["line"]
                break

        if previous_line and line != previous_line:
            interchanges.append((current, previous_line, line))

        previous_line = line

    if not interchanges:
        print("No interchanges on this route.")
    else:
        print("\nInterchange stations:")
        for st, l1, l2 in interchanges:
            print(f"→ {st} ({l1} → {l2})")
            
#Query 7
def handle_reachable_within_time_simple(path, graph, line_speeds, time_limit):
    print(f"\nStations reachable within {time_limit} minutes along shortest path:")

    total_time = 0.0
    for i in range(len(path) - 1):
        curr = path[i]
        next_station = path[i + 1]

        # find the edge
        for edge in graph[curr]:
            if edge['to'] == next_station:
                speed = line_speeds[edge['line']]
                travel_time = (edge['distance'] / speed) * 60
                break

        if total_time + travel_time > time_limit:
            break

        total_time += travel_time
        print(f"→ {next_station} ({total_time:.1f} min)")


#turtle graphics 
#used AI only for optimising display


def draw_station(t, x, y, name, above=False):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.dot(10, "black")

    offset = 15 if above else -20
    t.penup()
    t.goto(x, y + offset)
    t.write(name, align='center', font=("Arial", 8, "normal"))

    
def draw_connection(t, x1, y1, x2, y2, line):
    t.color(LINE_COLORS.get(line, "black"))
    t.width(3)
    t.penup()
    t.goto(x1, y1)
    t.pendown()
    t.goto(x2, y2)
    
def compute_path_layout(path, graph):
    x, y = 0, 0
    step_x = 120
    step_y = 80

    positions = {}
    positions[path[0]] = (x, y)

    min_x = max_x = x
    min_y = max_y = y

    current_line = None

    for i in range(len(path) - 1):
        current = path[i]
        next_station = path[i + 1]

        for edge in graph[current]:
            if edge["to"] == next_station:
                line = edge["line"]
                break

        # vertical shift on interchange
        if current_line and line != current_line:
            y -= step_y

        x += step_x
        positions[next_station] = (x, y)

        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

        current_line = line

    return positions, min_x, max_x, min_y, max_y

def centre_positions(positions, min_x, max_x, min_y, max_y):
    centre_x = (min_x + max_x) / 2
    centre_y = (min_y + max_y) / 2

    centred = {}
    for station, (x, y) in positions.items():
        centred[station] = (x - centre_x, y - centre_y)

    return centred

def get_bounds(positions):
    xs = [x for x, y in positions.values()]
    ys = [y for x, y in positions.values()]
    return min(xs), max(xs), min(ys), max(ys)










#drawing entire path now
#used AI help for proper visual
def draw_path(path, graph):
    SCREEN.clear()
    SCREEN.bgcolor("white")

    positions, _, _, _, _ = compute_path_layout(path, graph)
    positions = centre_positions(positions, 0, 0, 0, 0)

    min_x, max_x, min_y, max_y = get_bounds(positions)

    margin = 120
    SCREEN.setworldcoordinates(
        min_x - margin, min_y - margin,
        max_x + margin, max_y + margin
    )

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    t.width(3)

    for i in range(len(path) - 1):
        current = path[i]
        next_station = path[i + 1]

        x1, y1 = positions[current]
        x2, y2 = positions[next_station]

        for edge in graph[current]:
            if edge["to"] == next_station:
                line = edge["line"]
                break

        t.color(LINE_COLORS.get(line, "black"))
        t.penup()
        t.goto(x1, y1)
        t.pendown()
        t.goto(x2, y2)

        draw_station(t, x1, y1, current, above=(i % 2 == 0))


    draw_station(t, *positions[path[-1]], path[-1], above=((len(path) + 1) % 2 == 0))




    

        
#main menu
def main():
    stations, code_to_name, lines = load_mrt_data("MRT.txt")
    graph = graph_builder(stations)
    fares = load_fare("FareStructure.txt")

    while True:
        print_menu()
        choice = input("Select option: ")

        if choice == "0":
            break

        start = resolve_match_from_user("Enter start station: ", stations, code_to_name)
        end = resolve_match_from_user("Enter end station: ", stations, code_to_name)

        path, total_distance = a_star(graph, start, end)

        if path is None:
            print("No route found.")
            continue

        if choice == "1":
            handle_shortest_route(path, graph, total_distance)

        elif choice == "2":
            handle_travel_time(path, graph)
        
        elif choice == "3":
            handle_fare_query(path, total_distance, fares)
        
        elif choice == "4":
            handle_last_train_feasibility(path, graph)
        
        elif choice == "5":
            handle_first_train_query(path, graph)
        
        elif choice == "6":
            handle_min_time_query(graph, stations, start, end)
        
        elif choice == "7":
            time_limit = float(input("Enter time limit (minutes): "))
            handle_reachable_within_time_simple(path, graph, line_speeds, time_limit)
            
            
        elif choice == "8":
            handle_interchange_query(path, graph)
            
        
        

        else:
            print("Invalid input")


    
        
            
        







main()
            
            
          
            
            
            
            
            
            
        
    