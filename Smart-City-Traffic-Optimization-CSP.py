import pygame
import sys
import random
# import constraints


WIDTH, HEIGHT = 1200, 800
GRID_COLS = 5
GRID_ROWS = 4
CELL_SIZE = 200  # Increased cell size for better visibility
MARGIN = 40
FONT_SIZE = 25
SIGNAL_SIZE = 40
VEHICLE_SIZE = 12
PEDESTRIAN_SIZE = 15
ROAD_COLOR = (50, 50, 50)
LIGHT_OFF = (50, 50, 50)
LIGHT_GREEN = (0, 200, 0)
LIGHT_RED = (200, 0, 0)
EMERGENCY_COLOR = (255, 255, 0)  # Yellow for emergency
BUS_COLOR = (255, 165, 0)
CAR_COLOR = (100, 149, 237)  # Cornflower blue
PEDESTRIAN_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (120, 120, 120)

car_img = pygame.image.load("car.png")
car_img = pygame.transform.scale(car_img, (60, 30))
ambulance_img = pygame.image.load("ambulance.png")
ambulance_img = pygame.transform.scale(ambulance_img, (70, 40))
pedestrian_img = pygame.image.load("pedestrians.png")
pedestrian_img = pygame.transform.scale(pedestrian_img, (40, 40))

class Traffic_system:
    def __init__(self, block, emergency_vehicle, pedestrian_value, route, green_ns, green_ew, pedestrian_green):
        self.Block = block
        self.Total_cycles = 120
        self.Green_ns = green_ns
        self.Green_ew = green_ew
        self.Pedstrian_Green = pedestrian_green
        
        
        self.Emergency_vehicle = emergency_vehicle
        self.Much_pedertrian = pedestrian_value
        self.Bus_route = route

        self.Ns_domain = range(15, 61, 5)  # Green light for NS
        self.Ew_domain = range(15, 61, 5)  # Green light for EW
        self.Peds_domain = range(15, 61, 5)  # Green light for pedestrians
    
    
    # Getter functions

    def get_green_ns(self):
        return self.Green_ns
    
    def get_green_ew(self):
        return self.Green_ew
    
    def get_pede_value(self):
        return self.Pedstrian_Green
    
    
    # Setter functions

    def set_green_ns(self, new_value):
        if new_value in self.Ns_domain:
            self.Green_ns = new_value
        else:
            print("value out of domain")

    def set_green_ew(self, new_value):
        if new_value in self.Ew_domain:
            self.Green_ew = new_value
        else:
            print("value out of domain")

    def set_Peds(self, new_value):
        if new_value in self.Peds_domain:
            self.Pedstrian_Green = new_value
        else:
            print("value out of domain")

    # To get duration of red light
    def get_red_ns(self):
        if self.Green_ns is not None:
            return self.Total_cycles - self.Green_ns
        else:
            return None
    
    def get_red_ew(self):
        if self.Green_ns is not None:
            return self.Total_cycles - self.Green_ew
        else:
            return None
        
    def get_peds_red_durations(self):
        if self.Pedstrian_Green is not None:
            return self.Total_cycles - self.Pedstrian_Green
        else:
            return None 
    
    def __repr__(self):
        return f"Block {self.Block} | NS: {self.Green_ns}s | EW: {self.Green_ew}s | Ped: {self.Pedstrian_Green}s"


class CSP_System:
    def __init__(self):
        self.Variables = dict()
        self.Constraints = dict()
        self.Assignment = dict()
        self.Domains = dict()
        
    def add_variable(self, name, domain):
        self.Variables[name] = domain
        self.Domains[name] = domain
        if name not in self.Constraints:
            self.Constraints[name] = []

    def add_constraint(self, var, constr_fn):
        if var in self.Constraints:
            self.Constraints[var].append(constr_fn)
        else:
            self.Constraints[var] = [constr_fn]

    def is_consistent(self, var, value, assignment):
        temp = assignment.copy()
        temp[var] = value

        for constraint in self.Constraints.get(var, []):
            if not constraint(temp):
                return False
            
        return True

    def get_neighbours(self, var):
        neighbours = set()
        for (var1, var2) in self.Constraints:
            if var1 == var:
                neighbours.add(var2)
            elif var2 == var:
                neighbours.add(var1)
        return list(neighbours)

    def next_variable_selection(self, assignment):
        for i in self.Variables:
            if i not in assignment:
                return i

    def domain_values(self, var, domains):
        return list(domains[var])

    def backtracking(self, assignment, domain):
        if len(self.Variables) == len(assignment):
            return assignment
        
        var = self.next_variable_selection(assignment)
        for i in self.domain_values(var, domain):
            if self.is_consistent(var, i, assignment):
                assignment[var] = i

                result = self.backtracking(assignment, domain)

                if result is not None:
                    return result
                
                del assignment[var]
        
        return None

    def give_solution(self):
        assignment = {}  # Start with an empty assignment
        result = self.backtracking(assignment, self.Domains)
    
        if result is not None:
            print("Solution Found:")
            for var in sorted(result):
                print(f"{var}: {result[var]}")
            return result
        else:
            print("No solution found.")
            return None

    def no_conflict_constraint(self,ns, ew):
        if ns is None or ew is None:
            return True
        return not (ns > 0 and ew > 0)

    def emergency_priority_constraint(self, assignment, block):
        ns = assignment.get(f"{block}_NS")
        ew = assignment.get(f"{block}_EW")
        if ns is None or ew is None:
            return True
        return ns <= ew  # Less strict and satisfiable


    
    def pedestrian_window_constraint(self, ns, ew, ped):
        if ns is None or ew is None or ped is None:
            return True
        # Ensure pedestrian has a chance to walk during all-red window
        return ped <= min(ns, ew) // 2




GRID_ROWS = 4
GRID_COLS = 5
YELLOW_DURATION = 3  # Seconds for yellow light

def draw_grid(screen):
    for row in range(GRID_ROWS + 1):
        pygame.draw.line(screen, (0, 0, 0), (MARGIN, row * CELL_SIZE + MARGIN), (WIDTH - MARGIN, row * CELL_SIZE + MARGIN), 2)
    for col in range(GRID_COLS + 1):
        pygame.draw.line(screen, (0, 0, 0), (col * CELL_SIZE + MARGIN, MARGIN), (col * CELL_SIZE + MARGIN, HEIGHT - MARGIN), 2)

def draw_roads(screen):
    road_width = CELL_SIZE // 3
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            # Horizontal roads
            pygame.draw.rect(screen, ROAD_COLOR, (col * CELL_SIZE + MARGIN, row * CELL_SIZE + MARGIN + CELL_SIZE // 2 - road_width // 2, CELL_SIZE, road_width))
            # Vertical roads
            pygame.draw.rect(screen, ROAD_COLOR, (col * CELL_SIZE + MARGIN + CELL_SIZE // 2 - road_width // 2, row * CELL_SIZE + MARGIN, road_width, CELL_SIZE))

def draw_traffic_lights(screen, obj_list, solution, light_states):
    light_radius = 6
    offset = 10
    pedestrian_offset = 20  # Further away from center

    # For blinking effect
    blink_interval = 500  # milliseconds
    blink_on = (pygame.time.get_ticks() // blink_interval) % 2 == 0

    for i, obj in enumerate(obj_list):
        row = i // GRID_COLS
        col = i % GRID_COLS
        cx = col * CELL_SIZE + CELL_SIZE // 2 + MARGIN
        cy = row * CELL_SIZE + CELL_SIZE // 2 + MARGIN

        block_id = obj.Block
        state = light_states.get(block_id, ("red", "red", "stop"))
        ns, ew, ped = state if len(state) == 3 else (*state, "stop")

        # NS light
        pygame.draw.circle(screen, LIGHT_GREEN if ns == "green" else LIGHT_RED, (cx - offset, cy), light_radius)

        # EW light
        pygame.draw.circle(screen, LIGHT_GREEN if ew == "green" else LIGHT_RED, (cx + offset, cy), light_radius)

        # Pedestrian light logic
        if ped == "walk":
            # Blink white pedestrian light when allowed to walk
            pedestrian_color = (255, 255, 255)
        else:
            # Dim pedestrian light when stop
            pedestrian_color = (80, 80, 80)

        pygame.draw.circle(screen, pedestrian_color, (cx, cy + pedestrian_offset), light_radius)


def draw_vehicles_pedestrians(screen):
    screen.blit(car_img, (MARGIN + CELL_SIZE // 4, MARGIN + CELL_SIZE // 4))  # Car in cell I01 area
    screen.blit(car_img, (MARGIN + 4 * CELL_SIZE + CELL_SIZE // 4, MARGIN + CELL_SIZE + CELL_SIZE // 4))  # Car in cell I10 area
    screen.blit(ambulance_img, (MARGIN + 3 * CELL_SIZE + CELL_SIZE // 4, MARGIN + CELL_SIZE + CELL_SIZE // 4))  # Ambulance in cell I09 area
    screen.blit(pedestrian_img, (MARGIN + CELL_SIZE // 4, MARGIN + 3 * CELL_SIZE + CELL_SIZE // 4))  # Pedestrian in cell I16 area
    screen.blit(pedestrian_img, (MARGIN + CELL_SIZE // 4 + 20, MARGIN + 3 * CELL_SIZE + CELL_SIZE // 4))  # Another Pedestrian near the first one in I16 area

    new_car_x = MARGIN + 1 * CELL_SIZE + CELL_SIZE // 4
    new_car_y = MARGIN + 1 * CELL_SIZE + CELL_SIZE // 4
    screen.blit(car_img, (new_car_x, new_car_y))

    new_ambulance_x = MARGIN + 2 * CELL_SIZE + CELL_SIZE // 4
    new_ambulance_y = MARGIN + 3 * CELL_SIZE + CELL_SIZE // 4
    screen.blit(ambulance_img, (new_ambulance_x, new_ambulance_y))

   
    new_ped_x = MARGIN + 1 * CELL_SIZE + CELL_SIZE // 3 
    new_ped_y = MARGIN + 2 * CELL_SIZE + CELL_SIZE // 3 
    screen.blit(pedestrian_img, (new_ped_x, new_ped_y))

def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=10, gap_length=5):
    from math import hypot, atan2, cos, sin

    x1, y1 = start_pos
    x2, y2 = end_pos
    total_length = hypot(x2 - x1, y2 - y1)
    angle = atan2(y2 - y1, x2 - x1)

    dx = cos(angle) * dash_length
    dy = sin(angle) * dash_length
    gap_dx = cos(angle) * gap_length
    gap_dy = sin(angle) * gap_length

    current_x, current_y = x1, y1
    drawn = 0

    while drawn + dash_length < total_length:
        end_x = current_x + dx
        end_y = current_y + dy
        pygame.draw.line(surface, color, (current_x, current_y), (end_x, end_y), 3)
        current_x += dx + gap_dx
        current_y += dy + gap_dy
        drawn += dash_length + gap_length


def draw_emergency_route(screen):
    dash_length = 10
    gap_length = 5
    emergency_blocks = [2, 6, 10, 14, 18]

    for i in range(len(emergency_blocks) - 1):
        start = emergency_blocks[i]
        end = emergency_blocks[i + 1]

        # Calculate grid positions
        start_row = (start - 1) // GRID_COLS
        start_col = (start - 1) % GRID_COLS
        end_row = (end - 1) // GRID_COLS
        end_col = (end - 1) % GRID_COLS

        x1 = start_col * CELL_SIZE + CELL_SIZE // 2
        y1 = start_row * CELL_SIZE + CELL_SIZE // 2
        x2 = end_col * CELL_SIZE + CELL_SIZE // 2
        y2 = end_row * CELL_SIZE + CELL_SIZE // 2

        draw_dashed_line(screen, (0, 255, 0), (x1, y1), (x2, y2), dash_length, gap_length)

def draw_legend(screen):
    font = pygame.font.Font(None, FONT_SIZE)
    y_offset = 10
    x_offset = WIDTH - 160

    items = [
        ((200, 0, 0), "Traffic Light (Red)"),
        ((0, 200, 0), "Traffic Light (Green)"),
        ((255, 255, 0), "Traffic Light (Yellow)"),
        (CAR_COLOR, "Car"),
        ((0, 0, 0), "Car (another)"),
        (EMERGENCY_COLOR, "Emergency Vehicle"),
        (PEDESTRIAN_COLOR, "Pedestrian"),
        ((0, 255, 0), "Emergency Route")
    ]

    for color, text in items:
        pygame.draw.rect(screen, color, (x_offset, y_offset, 20, 20))
        text_surface = font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (x_offset + 30, y_offset + 5))
        y_offset += 30

def draw_traffic_flow(screen):
    arrow_size = 10
    arrow_color = (0, 0, 0)

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            center_x = col * CELL_SIZE + CELL_SIZE // 2 + MARGIN
            center_y = row * CELL_SIZE + CELL_SIZE // 2 + MARGIN

            # Simplified flow - adjust based on your needs
            pygame.draw.polygon(screen, arrow_color, [(center_x + CELL_SIZE // 4, center_y - arrow_size // 2), (center_x + CELL_SIZE // 4 + arrow_size, center_y), (center_x + CELL_SIZE // 4, center_y + arrow_size // 2)]) # Right
            pygame.draw.polygon(screen, arrow_color, [(center_x - CELL_SIZE // 4, center_y - arrow_size // 2), (center_x - CELL_SIZE // 4 - arrow_size, center_y), (center_x - CELL_SIZE // 4, center_y + arrow_size // 2)]) # Left
            pygame.draw.polygon(screen, arrow_color, [(center_x - arrow_size // 2, center_y + CELL_SIZE // 4), (center_x, center_y + CELL_SIZE // 4 + arrow_size), (center_x + arrow_size // 2, center_y + CELL_SIZE // 4)]) # Down
            pygame.draw.polygon(screen, arrow_color, [(center_x - arrow_size // 2, center_y - CELL_SIZE // 4), (center_x, center_y - CELL_SIZE // 4 - arrow_size), (center_x + arrow_size // 2, center_y - CELL_SIZE // 4)]) # Up

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Traffic System Visualization")
    screen.fill(BACKGROUND_COLOR)

    obj_list = []
    csp = CSP_System()

    
    for i in range(1, GRID_ROWS * GRID_COLS + 1):
        block = f"I{i:02d}"  
        emergency_vehicle = (i == 4 or i == 9)  
        pedestrian_value = (i % 4 == 0)
        route = (i in [2, 6, 10, 14, 18])
        green_ns = 10
        green_ew = 15
        pedestrian_green = 5

        
        obj = Traffic_system(block, emergency_vehicle, pedestrian_value, route, green_ns, green_ew, pedestrian_green)
        obj_list.append(obj)

        # Add CSP variables
        csp.add_variable(f"{block}_NS", list(obj.Ns_domain))
        csp.add_variable(f"{block}_EW", list(obj.Ew_domain))
        csp.add_variable(f"{block}_PED", list(obj.Peds_domain))

        
        csp.add_constraint(f"{block}_NS", lambda a, b=block: a.get(f"{b}_NS", 0) + a.get(f"{b}_EW", 0) <= 120)

        
        if emergency_vehicle:
            csp.add_constraint(f"{block}_NS", lambda a, b=block: csp.emergency_priority_constraint(a, b))
            csp.add_constraint(f"{block}_EW", lambda a, b=block: csp.emergency_priority_constraint(a, b))

        
        csp.add_constraint(f"{block}_PED", lambda a, b=block: csp.pedestrian_window_constraint(
            a.get(f"{b}_NS"), a.get(f"{b}_EW"), a.get(f"{b}_PED")))


    solution = csp.give_solution()
    if solution is None:
        print("No solution found. Exiting...")
        pygame.quit()
        sys.exit()

    
    light_states = {}
    light_timers = {}
    

    for obj in obj_list:
        block_id = obj.Block

        
        if random.choice([True, False]):
            light_states[block_id] = ("green", "red", "stop")
        else:
            light_states[block_id] = ("red", "green", "stop")

        # Apply random phase offset to desynchronize timers (0–5 seconds)
        light_timers[block_id] = pygame.time.get_ticks() - random.randint(0, 15000)

        # Use durations from CSP solution (with fallback default values)
        light_timers[f"{block_id}_ns_green_duration"] = solution.get(f"{block_id}_NS", 10) * 1000
        light_timers[f"{block_id}_ew_green_duration"] = solution.get(f"{block_id}_EW", 15) * 1000


    DEFAULT_PED_SECONDS = 5

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen)
        draw_roads(screen)
        # Pass the updated light_states to the drawing function
        draw_traffic_lights(screen, obj_list, solution, light_states)
        draw_vehicles_pedestrians(screen)
        draw_emergency_route(screen)
        draw_traffic_flow(screen)
        draw_legend(screen)

        font = pygame.font.Font(None, FONT_SIZE + 5)
        for i in range(1, GRID_ROWS * GRID_COLS + 1):
            row = (i - 1) // GRID_COLS
            col = (i - 1) % GRID_COLS
            text_surface = font.render(f"I{i:02d}", True, (0, 0, 0))
            screen.blit(text_surface, (col * CELL_SIZE + MARGIN + 5, row * CELL_SIZE + MARGIN + 5))

        #// real time traffic light system
        current_time = pygame.time.get_ticks()
        for obj in obj_list:
            block_id = obj.Block

            ns_green_duration = light_timers.get(f"{block_id}_ns_green_duration", 10000)
            ew_green_duration = light_timers.get(f"{block_id}_ew_green_duration", 15000)
            pedestrian_duration = solution.get(f"{block_id}_PED", DEFAULT_PED_SECONDS) * 1000 # Convert seconds to ms

            # Get current state and time elapsed in this state
            current_state = light_states.get(block_id, ("red", "red", "stop")) 
            ns_light, ew_light, *rest = current_state
            ped_light = rest[0] if rest else "stop"
            time_elapsed = current_time - light_timers.get(block_id, current_time)

            

            if ns_light == "red" and ew_light == "red" and ped_light == "walk":
                if time_elapsed >= pedestrian_duration:
                   
                    next_green = light_timers.get(f"{block_id}_next_green", "NS")
                    if next_green == "NS":
                        light_states[block_id] = ("green", "red", "stop")
                    else: 
                        light_states[block_id] = ("red", "green", "stop")
                    light_timers[block_id] = current_time
                
            elif ns_light == "green":
                if time_elapsed >= ns_green_duration:
                    light_states[block_id] = ("yellow", "red", "stop")
                    light_timers[block_id] = current_time
                    
            elif ns_light == "yellow":
                if time_elapsed >= YELLOW_DURATION * 1000:
                    light_states[block_id] = ("red", "red", "walk")
                    light_timers[block_id] = current_time 
                    light_timers[f"{block_id}_next_green"] = "EW" 

            elif ew_light == "green":
                if time_elapsed >= ew_green_duration:
                    light_states[block_id] = ("red", "yellow", "stop")
                    light_timers[block_id] = current_time

            elif ew_light == "yellow":
                if time_elapsed >= YELLOW_DURATION * 1000:
                    light_states[block_id] = ("red", "red", "walk")
                    light_timers[block_id] = current_time 
                    light_timers[f"{block_id}_next_green"] = "NS" 

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()