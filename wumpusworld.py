import pygame as pg
import sys
import random
from pygame.locals import *

#Colors
bg = [(255,222,35), (255,80,164)]
c1 = '#000000' #black
c2 = '#FFDF3A'  #yellow
c3 = '#0CCF9A'  #light blue
c4 = '#9F0D0D'  #red
c5 = '#468202'  #green
c6 = '#FF5400'  #red orange

#Dimensions
width = 700
height = 650

#Initialize Pygame
pg.init()
window = pg.display.set_mode((width, height))
pg.display.set_caption("Wumpus World")

#Fonts
f1 = pg.font.Font(None, 120)
f2 = pg.font.Font(None, 50)
f3 = pg.font.Font(None, 30)
f4 = pg.font.Font(None, 40)
f5 = pg.font.Font(None, 35)

#Global Variables
grid_size = 4
cell_size = 120
ENVIRONMENT = []
SOLVING_PHASE = False
TRAPPED = False
GOLD_FOUND = False
ARROW = 1
POINTS = 0
AGENT_OUTSIDE_CAVE = False
AGENT_KNOWLEDGE_BASE = {} #NAKA USUAL POS 

AGENT_POS = (1,1) #NAKA CUSTOM POS 
WUMPUS_POS = ()
PIT_POS = []
GOLD_POS = ()
START_POS = (1,1)

DIAGONALS = [
    [(0, 0), (1, 1)],
    [(0, 1), (1, 0)],
    [(0, 1), (1, 2)],
    [(0, 2), (1, 1)],
    [(0, 2), (1, 3)],
    [(0, 3), (1, 2)],
    [(1, 1), (2, 0)],
    [(1, 0), (2, 1)],
    [(1, 1), (2, 2)],
    [(1, 2), (2, 1)],
    [(1, 2), (2, 3)],
    [(1, 3), (2, 2)],
    [(2, 0), (3, 1)],
    [(2, 1), (3, 0)],
    [(2, 1), (3, 2)],
    [(2, 2), (3, 1)],
    [(2, 2), (3, 3)],
    [(2, 3), (3, 2)]
]

VISITED_DIAGONALS = [] #Usual POS
QUEUE = [] #For backtracking | USUAL POS
AGENT_AT_START = False


def bg_gradient():
    bgSurface = pg.Surface((width, height))
    colorsLen = len(bg) - 1
    color_segments = height // colorsLen

    #Make a gradient background color
    for i in range(colorsLen):
        start_color = bg[i]
        end_color = bg[i + 1]

        for y in range(i * color_segments, (i + 1) * color_segments):
            ratio = (y - (i * color_segments)) / color_segments
            color = tuple(int(start + ratio * (end - start)) for start, end in zip(start_color, end_color))
            pg.draw.line(bgSurface, color, (0, y), (width, y))

    return bgSurface

def custom_to_usual_pos(custom_x, custom_y):
    usual_x = -1  # Default value 
    usual_y = -1

    if custom_x == 1 and custom_y == 4:
        usual_x = 0
        usual_y = 0
    elif custom_x == 2 and custom_y == 4:
        usual_x = 0
        usual_y = 1
    elif custom_x == 3 and custom_y == 4:
        usual_x = 0
        usual_y = 2
    elif custom_x == 4 and custom_y == 4:
        usual_x = 0
        usual_y = 3
    elif custom_x == 1 and custom_y == 3:
        usual_x = 1
        usual_y = 0
    elif custom_x == 2 and custom_y == 3:
        usual_x = 1
        usual_y = 1
    elif custom_x == 3 and custom_y == 3:
        usual_x = 1
        usual_y = 2
    elif custom_x == 4 and custom_y == 3:
        usual_x = 1
        usual_y = 3
    elif custom_x == 1 and custom_y == 2:
        usual_x = 2
        usual_y = 0
    elif custom_x == 2 and custom_y == 2:
        usual_x = 2
        usual_y = 1
    elif custom_x == 3 and custom_y == 2:
        usual_x = 2
        usual_y = 2
    elif custom_x == 4 and custom_y == 2:
        usual_x = 2
        usual_y = 3
    elif custom_x == 1 and custom_y == 1:
        usual_x = 3
        usual_y = 0
    elif custom_x == 2 and custom_y == 1:
        usual_x = 3
        usual_y = 1
    elif custom_x == 3 and custom_y == 1:
        usual_x = 3
        usual_y = 2
    elif custom_x == 4 and custom_y == 1:
        usual_x = 3
        usual_y = 3
    
    return usual_x, usual_y

def usual_to_custom_pos(usual_x, usual_y):
    custom_x = -1  # Default value 
    custom_y = -1

    if usual_x == 0 and usual_y == 0:
        custom_x = 1
        custom_y = 4
    elif usual_x == 0 and usual_y == 1:
        custom_x = 2
        custom_y = 4
    elif usual_x == 0 and usual_y == 2:
        custom_x = 3
        custom_y = 4
    elif usual_x == 0 and usual_y == 3:
        custom_x = 4
        custom_y = 4
    elif usual_x == 1 and usual_y == 0:
        custom_x = 1
        custom_y = 3
    elif usual_x == 1 and usual_y == 1:
        custom_x = 2
        custom_y = 3
    elif usual_x == 1 and usual_y == 2:
        custom_x = 3
        custom_y = 3
    elif usual_x == 1 and usual_y == 3:
        custom_x = 4
        custom_y = 3
    elif usual_x == 2 and usual_y == 0:
        custom_x = 1
        custom_y = 2
    elif usual_x == 2 and usual_y == 1:
        custom_x = 2
        custom_y = 2
    elif usual_x == 2 and usual_y == 2:
        custom_x = 3
        custom_y = 2
    elif usual_x == 2 and usual_y == 3:
        custom_x = 4
        custom_y = 2
    elif usual_x == 3 and usual_y == 0:
        custom_x = 1
        custom_y = 1
    elif usual_x == 3 and usual_y == 1:
        custom_x = 2
        custom_y = 1
    elif usual_x == 3 and usual_y == 2:
        custom_x = 3
        custom_y = 1
    elif usual_x == 3 and usual_y == 3:
        custom_x = 4
        custom_y = 1

    return custom_x, custom_y

def still():
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

def gameOver():
    
    if AGENT_POS == WUMPUS_POS:
        print("******* Agent got eaten by the Wumpus. *******")
        return True
    elif AGENT_POS in PIT_POS:
        print("******* Agent fell in a pit. *******")
        return True
    elif GOLD_FOUND:
        True
    elif (GOLD_FOUND and AGENT_AT_START) or (TRAPPED and AGENT_AT_START):
        return True
    else:
        return False

def show_visited():
    for i in range(grid_size):
        for j in range(grid_size):
            if AGENT_KNOWLEDGE_BASE[(i,j)]['visited']: #Check if the cell has been visited
                pos_x, pos_y = custom_to_usual_pos(i + 1, grid_size - j)
                pos_x = 108 + pos_x * cell_size + cell_size // 2
                pos_y = 30 + pos_y * cell_size + cell_size // 2
                states_in_cell = [pos[2] for pos in ENVIRONMENT if custom_to_usual_pos(pos[0], pos[1]) == (i, j)]
                total_states = len(states_in_cell)
                if total_states > 1:
                    total_height = total_states * (cell_size // 4)
                    for idx, state in enumerate(states_in_cell):
                        adjusted_pos_y = pos_y - total_height // 2 + (idx * (cell_size // 4))
                        text = f3.render(state, True, c1)
                        text_rect = text.get_rect(center=(pos_x, adjusted_pos_y))
                        window.blit(text, text_rect)
                elif total_states == 1:
                    text = f3.render(states_in_cell[0], True, c1)
                    text_rect = text.get_rect(center=(pos_x, pos_y))
                    window.blit(text, text_rect)
                else:
                    pass

def draw_visited():
    blocks = [[c3] * grid_size for _ in range(grid_size)]  # Initial colors for each block

    for i in range(grid_size):
        for j in range(grid_size):
            rect = pg.Rect(108 + j * cell_size, 30 + i * cell_size, cell_size, cell_size)
            if AGENT_KNOWLEDGE_BASE[(i,j)]['visited']:  #If the cell has been visited
                pg.draw.rect(window, c2, rect)  #Fill the cell with a different color
            else:
                pg.draw.rect(window, blocks[i][j], rect)  # Draw block fill

            pg.draw.rect(window, c1, rect, 1)  # Draw border
    
    show_visited()

def visited_diagonals():
    global VISITED_DIAGONALS

    for cell1, cell2 in DIAGONALS:
        if AGENT_KNOWLEDGE_BASE[cell1]['visited'] and AGENT_KNOWLEDGE_BASE[cell2]['visited']:
            VISITED_DIAGONALS.append([cell1, cell2])

def get_opposite_diagonal(diagonal):
    opp = []

    if diagonal == [(0, 0), (1, 1)]:
        opp = [(0, 1), (1, 0)]
    elif diagonal == [(0, 1), (1, 0)]:
        opp = [(0, 0), (1, 1)]
    elif diagonal == [(0, 1), (1, 2)]:
        opp = [(0, 2), (1, 1)]
    elif diagonal == [(0, 2), (1, 1)]:
        opp = [(0, 1), (1, 2)]
    elif diagonal == [(0, 2), (1, 3)]:
        opp = [(0, 3), (1, 2)]
    elif diagonal == [(0, 3), (1, 2)]:
        opp = [(0, 2), (1, 3)]
    elif diagonal == [(1, 1), (2, 0)]:
        opp = [(1, 0), (2, 1)]
    elif diagonal == [(1, 0), (2, 1)]:
        opp = [(1, 1), (2, 0)]
    elif diagonal == [(1, 1), (2, 2)]:
        opp = [(1, 2), (2, 1)]
    elif diagonal == [(1, 2), (2, 1)]:
        opp = [(1, 1), (2, 2)]
    elif diagonal == [(1, 2), (2, 3)]:
        opp = [(1, 3), (2, 2)]
    elif diagonal == [(1, 3), (2, 2)]:
        opp = [(1, 2), (2, 3)]
    elif diagonal == [(2, 0), (3, 1)]:
        opp = [(2, 1), (3, 0)]
    elif diagonal == [(2, 1), (3, 0)]:
        opp = [(2, 0), (3, 1)]
    elif diagonal == [(2, 1), (3, 2)]:
        opp = [(2, 2), (3, 1)]
    elif diagonal == [(2, 2), (3, 1)]:
        opp = [(2, 1), (3, 2)]
    elif diagonal == [(2, 2), (3, 3)]:
        opp = [(2, 3), (3, 2)]
    elif diagonal == [(2, 3), (3, 2)]:
        opp = [(2, 2), (3, 3)]
    
    return opp

def get_unvisited_opp_diagonal(diagonal):
    opposite_diagonal = get_opposite_diagonal(diagonal)
    
    for cell in opposite_diagonal:
        if not AGENT_KNOWLEDGE_BASE[cell]['visited']:
            return cell

    return None

def initialize_knowledge():
    global AGENT_KNOWLEDGE_BASE

    for i in range(grid_size):
        for j in range(grid_size):
            # Initialize knowledge base for each cell
            cell_coordinates = (i, j)
            AGENT_KNOWLEDGE_BASE[cell_coordinates] = {
                'stench': False,
                'breeze': False,
                'glitter': False,
                'bump': False,
                'scream': False,
                'visited': False,
                'safe': False, 
                'unsafe': False,
                'wumpus_possible': False,
                'pit_possible': False
            }

def update_knowledge():
    global AGENT_KNOWLEDGE_BASE, GOLD_POS, PIT_POS, WUMPUS_POS, QUEUE

    current_cell_coordinates = custom_to_usual_pos(AGENT_POS[0], AGENT_POS[1])
    #Check if there is stench, breeze, or glitter in the current cell
    for pos in ENVIRONMENT:
        x, y, state = pos
        if (x,y) == AGENT_POS:
            if state == 'Stench':
                AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['stench'] = True
            if state == 'Breeze':
                AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['breeze'] = True
                GOLD_POS = AGENT_POS
            if state == 'Glitter(Au)':
                AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['glitter'] = True

    #Check for bump if the agent is at the edge of the grid
    if AGENT_POS[0] == 1:
        AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['bump'] = True  #Bump at left
    elif AGENT_POS[0] == grid_size:
        AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['bump'] = True  #Bump at right
    elif AGENT_POS[1] == 1:
        AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['bump'] = True  #Bump at bottom
    elif AGENT_POS[1] == grid_size:
        AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['bump'] = True  #Bump at top

    # Check if there is a scream
    if (AGENT_POS[0] + 1, AGENT_POS[1]) == WUMPUS_POS or \
       (AGENT_POS[0] - 1, AGENT_POS[1]) == WUMPUS_POS or \
       (AGENT_POS[0], AGENT_POS[1] + 1) == WUMPUS_POS or \
       (AGENT_POS[0], AGENT_POS[1] - 1) == WUMPUS_POS:
        AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['scream'] = True  # Scream

    #Mark the current cell as visited
    AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['visited'] = True
    QUEUE.append(current_cell_coordinates)

    possible_moves = []
    #check possible moves
    for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
        new_x, new_y = AGENT_POS[0] + dx, AGENT_POS[1] + dy
        if 1 <= new_x <= grid_size and 1 <= new_y <= grid_size:
            possible_moves.append((new_x, new_y))

    #check if adjacent cells are safe
    current_cell_coordinates = custom_to_usual_pos(AGENT_POS[0], AGENT_POS[1])
    if not AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['stench'] and \
            not AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['breeze']:
        for new_x, new_y in possible_moves:
            adj_cell_coordinates = custom_to_usual_pos(new_x, new_y)
            if not AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['visited']:
                AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['safe'] = True #Mark as safe
    elif AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['stench']:
        for new_x, new_y in possible_moves:
            adj_cell_coordinates = custom_to_usual_pos(new_x, new_y)
            if not AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['visited']:
                if not AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['safe']:
                    AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['wumpus_possible'] = True #Mark as wumpus_possible
    elif AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['breeze']:
        for new_x, new_y in possible_moves:
            adj_cell_coordinates = custom_to_usual_pos(new_x, new_y)
            if not AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['visited']:
                if not AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['safe']:
                    AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['pit_possible'] = True #Mark as pit_possible
    elif AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['stench'] and AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['breeze']:
        for new_x, new_y in possible_moves:
            adj_cell_coordinates = custom_to_usual_pos(new_x, new_y)
            if not AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['visited']:
                if not AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['safe']:
                    AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['wumpus_possible'] = True #Mark as unsafe
                    AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['pit_possible'] = True #Mark as pit_possible


    #Checks pattern, and mark cell as safe or set as wumpus or pit pos
    visited_diagonals()
    if VISITED_DIAGONALS: 
        for CELL in VISITED_DIAGONALS: 
            if ((AGENT_KNOWLEDGE_BASE[CELL[0]]['stench'] and not AGENT_KNOWLEDGE_BASE[CELL[0]]['breeze']) and \
                (AGENT_KNOWLEDGE_BASE[CELL[1]]['breeze'] and not AGENT_KNOWLEDGE_BASE[CELL[1]]['stench'])) or \
                ((AGENT_KNOWLEDGE_BASE[CELL[0]]['breeze'] and not AGENT_KNOWLEDGE_BASE[CELL[0]]['stench']) and \
                (AGENT_KNOWLEDGE_BASE[CELL[1]]['stench'] and not AGENT_KNOWLEDGE_BASE[CELL[1]]['breeze'])):

                opp_cellx, opp_celly = get_opposite_diagonal(CELL)
                print(f"marked as safe: {CELL}, {opp_cellx}, {opp_celly}")
                AGENT_KNOWLEDGE_BASE[opp_cellx]['safe'] = True
                AGENT_KNOWLEDGE_BASE[opp_celly]['safe'] = True

            elif ((AGENT_KNOWLEDGE_BASE[CELL[0]]['breeze'] and not AGENT_KNOWLEDGE_BASE[CELL[0]]['stench']) and \
                (AGENT_KNOWLEDGE_BASE[CELL[1]]['breeze'] and not AGENT_KNOWLEDGE_BASE[CELL[1]]['stench'])):

                unvisited_oppX,  unvisited_oppY = get_unvisited_opp_diagonal(CELL)
                pos = usual_to_custom_pos(unvisited_oppX, unvisited_oppY)
                print(f">> Found a PIT at {pos}")
                PIT_POS.append(pos) #append pit position
                

            elif ((AGENT_KNOWLEDGE_BASE[CELL[0]]['stench'] and not AGENT_KNOWLEDGE_BASE[CELL[0]]['breeze']) and \
                (AGENT_KNOWLEDGE_BASE[CELL[1]]['stench'] and not AGENT_KNOWLEDGE_BASE[CELL[1]]['breeze'])) or \
                ((AGENT_KNOWLEDGE_BASE[CELL[0]]['stench'] and AGENT_KNOWLEDGE_BASE[CELL[0]]['breeze']) and \
                (AGENT_KNOWLEDGE_BASE[CELL[1]]['stench'] and AGENT_KNOWLEDGE_BASE[CELL[1]]['breeze'])):

                unvisited_oppX,  unvisited_oppY= get_unvisited_opp_diagonal(CELL)
                WUMPUS_POS = usual_to_custom_pos(unvisited_oppX, unvisited_oppY)
                print(f">> Found WUMPUS at {WUMPUS_POS}")
                if WUMPUS_POS: #Set all wumpus possible to False, since theres only 1 wumpus
                    for i in range(grid_size):
                        for j in range(grid_size):
                            cell_coordinates = (i, j)
                            AGENT_KNOWLEDGE_BASE[cell_coordinates]['wumpus_possible'] = False    



    print("")
    coord = usual_to_custom_pos(current_cell_coordinates[0], current_cell_coordinates[1])
    print(f"AGENT'S KNOWLEDGE in {coord}: {AGENT_KNOWLEDGE_BASE[current_cell_coordinates]}")

def update_agent_position():
    global ENVIRONMENT

    #Find 'Agent' and change POS    
    for idx, cell in enumerate(ENVIRONMENT):
        if cell[2] == 'Agent':
            ENVIRONMENT[idx] = (AGENT_POS[0], AGENT_POS[1], 'Agent')
            break

def choose_action():
    global AGENT_KNOWLEDGE_BASE, GOLD_POS

    current_cell_coordinates = custom_to_usual_pos(AGENT_POS[0], AGENT_POS[1])

    if AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['glitter']:
        GOLD_POS = AGENT_POS
        return 'grab'

    if AGENT_KNOWLEDGE_BASE[current_cell_coordinates]['bump']:
        return 'move'

    #wumpus is found and agent is in same row and column as the wumpus
    if WUMPUS_POS and (AGENT_POS[0] == WUMPUS_POS[0] or AGENT_POS[1] == WUMPUS_POS[1]): 
        return 'shoot_arrow'
    
    if TRAPPED:
        return 'climb'

    return 'move'

def backtrack():
    global AGENT_POS, PREV_POS_STACK

    while AGENT_POS != START_POS:
        current_cell_coordinates = custom_to_usual_pos(AGENT_POS[0], AGENT_POS[1])
        PREV_POS_STACK.append(AGENT_POS)  # Push current position to stack
        possible_moves = []

        # Check adjacent cells for possible moves
        for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            new_x, new_y = AGENT_POS[0] + dx, AGENT_POS[1] + dy
            if 1 <= new_x <= grid_size and 1 <= new_y <= grid_size:
                possible_moves.append((new_x, new_y))

        # Check if there are unvisited safe cells in adjacent cells
        for new_x, new_y in possible_moves:
            adj_cell_coordinates = custom_to_usual_pos(new_x, new_y)
            if not AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['visited'] and AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['safe']:
                AGENT_POS = (new_x, new_y)
                print(f"Agent backtracked to cell {AGENT_POS}")
                return

        # If no unvisited safe cells found, backtrack further
        AGENT_POS = PREV_POS_STACK.pop()

    # If backtracked to start position and still no unvisited safe cells, reset to start
    print("No unvisited safe cells found in backtracking, resetting to start position.")
    AGENT_POS = START_POS

def move():
    global AGENT_POS, AGENT_KNOWLEDGE_BASE, POINTS, TRAPPED, QUEUE

    possible_moves = [] #CUSTOM POS 

    # Check possible moves
    for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
        new_x, new_y = AGENT_POS[0] + dx, AGENT_POS[1] + dy
        if 1 <= new_x <= grid_size and 1 <= new_y <= grid_size:
            possible_moves.append((new_x, new_y))
    print(f">> POSSIBLE MOVES IN POS{AGENT_POS}: {possible_moves}")

    # Choose the next move based on knowledge
    next_move = None
    safe_unvisited_cells = []
    for new_x, new_y in possible_moves:
        adj_cell_coordinates = custom_to_usual_pos(new_x, new_y)
        if AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['safe'] and not AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['visited']: #USUAL POS
            safe_unvisited_cells.append((new_x, new_y)) #CUSTOM POS 
    print(f">> SAFE UNVISITED CELLS: {safe_unvisited_cells}")

    if safe_unvisited_cells:
        next_move = random.choice(safe_unvisited_cells)
        print("1")
    # else:
    #     wumpus_possible_moves = []
    #     pit_possible_moves = []
    #     for move in possible_moves:
    #         coord = custom_to_usual_pos(move[0], move[1])
    #         if AGENT_KNOWLEDGE_BASE[coord]['wumpus_possible']:
    #             wumpus_possible_moves.append(move)
    #         elif AGENT_KNOWLEDGE_BASE[coord]['pit_possible']:
    #             pit_possible_moves.append(move)
        
    #     # Remove cells with Wumpus or Pit possible from possible moves
    #     safe_possible_moves = []
    #     safe_possible_moves = [move for move in possible_moves if move not in wumpus_possible_moves and move not in pit_possible_moves]            
    #     if safe_possible_moves:
    #         next_move = random.choice(safe_possible_moves)
    #         print("2")

    # If all adjacent unvisited cells are unsafe, backtrack to visited cells
    if next_move is None:
        # next_move = QUEUE.pop()

        backtrack = True
        visited_cells = []
        visited_adjacent = []
        while backtrack: 

            for x, y in possible_moves: #Check visited cells
                adj_cell_coordinates = custom_to_usual_pos(x, y)
                if AGENT_KNOWLEDGE_BASE[adj_cell_coordinates]['visited']:
                    visited_cells.append((x, y))
            
            for posx, posy in visited_cells:   
                for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
                    new_x, new_y = posx + dx, posy + dy
                    if 1 <= new_x <= grid_size and 1 <= new_y <= grid_size:
                        if not AGENT_KNOWLEDGE_BASE[(new_x, new_y)]['visited']:
                            visited_adjacent.append((new_x, new_y))
                
                for cellx, celly in visited_adjacent:
                    coord = custom_to_usual_pos(cellx, celly)
                    print(posx, posy)
                    print(f"ADJACENT OF VISITED CELLS: {coord}")

                    if not AGENT_KNOWLEDGE_BASE[coord]['visited'] and AGENT_KNOWLEDGE_BASE[coord]['safe']:
                        next_move = (posx, posy)
                        print("3")
                        backtrack = False
                        break
                    elif (not AGENT_KNOWLEDGE_BASE[coord]['visited'] and AGENT_KNOWLEDGE_BASE[coord]['pit_possible']) or \
                        (not AGENT_KNOWLEDGE_BASE[coord]['visited'] and AGENT_KNOWLEDGE_BASE[coord]['wumpus_possible']) or\
                        (not AGENT_KNOWLEDGE_BASE[coord]['visited'] and AGENT_KNOWLEDGE_BASE[coord]['wumpus_possible'] and AGENT_KNOWLEDGE_BASE[coord]['pit_possible']):
                        TRAPPED = True
                        backtrack = False
                    else: 
                        next_move = random.choice(visited_cells)
                        print("4")
                        backtrack = False

    # Move the agent to the chosen cell
    if next_move:
        AGENT_POS = next_move
        POINTS -= 1
        print(f">> NEXT MOVE: {next_move}")
        print(f">> AGENT MOVE TO CELL {AGENT_POS}")
        print(f">> POINTS: {POINTS}")
        new_cell_coordinates = custom_to_usual_pos(AGENT_POS[0], AGENT_POS[1])
        AGENT_KNOWLEDGE_BASE[new_cell_coordinates]['visited'] = True
        update_agent_position()
    else:
        TRAPPED = True
        print("AGENT IS TRAPPED! NO LOGICAL MOVE TO MAKE.")

def grab():
    global GOLD_FOUND, POINTS

    GOLD_FOUND = True
    POINTS += 1000
    print(f">> POINTS: {POINTS}")
    climb()

def shoot_arrow():
    global ARROW, WUMPUS_POS, ENVIRONMENT

    print(">> Agent shoot an arrow and killed the Wumpus.")
    ARROW -= 1
    WUMPUS_POS = None

    #Remove wumpus from the environment
    for idx, cell in enumerate(ENVIRONMENT):
        if cell[2] == 'Wumpus':
            ENVIRONMENT.pop(idx)
            break

def climb():
    global QUEUE, AGENT_AT_START, AGENT_POS, POINTS

    # while len(QUEUE) != 0:

    #     next_move = QUEUE.pop()
    #     AGENT_POS = next_move
    #     POINTS -= 1
    #     print(f">> NEXT MOVE: {next_move}")
    #     print(f">> AGENT MOVE TO CELL {AGENT_POS}")
    #     print(f">> POINTS: {POINTS}")
    #     update_agent_position()
    #     update_knowledge()
    #     draw_visited()

    if AGENT_POS == START_POS:
        if GOLD_FOUND:
            print("***** AGENT FOUND THE GOLD AND CLIMB OUT OF THE CAVE! *****")
        else: 
            print("***** AGENT WAS TRAPPED AND CLIMB OUT OF THE CAVE! *****")
        AGENT_AT_START = True
    else:
        print("Agent can only climb out from the starting position.")

def solve_wumpus_world():
    bgColor = bg_gradient()
    window.blit(bgColor, (0, 0))

    header = f2.render("WUMPUS WORLD AGENT", True, c1)
    headerRect = header.get_rect(center=(width / 2, 550))
    window.blit(header, headerRect)

    s1 = f3.render("'Kindly refer to terminal for Agent's detailed", True, c4)
    s1Rect = s1.get_rect(center=(width / 2, 585))
    window.blit(s1, s1Rect)
    s2 = f3.render("move description and points.'", True, c4)
    s2Rect = s2.get_rect(center=(width / 2, 610))
    window.blit(s2, s2Rect)

    initialize_knowledge()

    running = True
    while running:
        update_knowledge()
        draw_visited()  # draw and show visited cells
        
        action = choose_action()
        if action == 'move':
            move()
        elif action == 'shoot_arrow':
            shoot_arrow()
        elif action == 'grab':
            grab()
        # elif action == 'climb':
        #     climb()
       
        pg.time.delay(1000) #delay showing
        
        if gameOver():
            still()
            running = False

        pg.display.flip()

    print("--- GAME OVER ---")

    for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                sys.exit()

def draw_grid(show_board):

    blocks = [[c3] * grid_size for _ in range(grid_size)]  #Initial colors for each block
    
    for i in range(grid_size):
        for j in range(grid_size):
            rect = pg.Rect(108 + j * cell_size, 30 + i * cell_size, cell_size, cell_size)
            if show_board == False:
                pg.draw.rect(window, blocks[i][j], rect)  #Draw block fill

            pg.draw.rect(window, c1, rect, 1)  #Draw border
            
def draw_positions():
    encountered_positions = {}  #Keep track of encountered positions and their states

    # Store positions of each state first
    for pos in ENVIRONMENT:
        print(pos)
        x, y, state = pos
        pos_x = 108 + (x - 1) * cell_size + cell_size // 2
        pos_y = 30 + (grid_size - y) * cell_size + cell_size // 2  # Invert y to match custom grid

        if (x, y) in encountered_positions:
            encountered_positions[(x, y)].append((pos_x, pos_y, state))
        else:
            encountered_positions[(x, y)] = [(pos_x, pos_y, state)]

    # Display states with adjusted positions
    for pos_list in encountered_positions.values():
        total_states = len(pos_list)
        if total_states > 1:
            total_height = total_states * (cell_size // 4)
            for idx, (pos_x, pos_y, state) in enumerate(pos_list):
                adjusted_pos_y = pos_y - total_height // 2 + (idx * (cell_size // 4))
                text = f3.render(state, True, c1)
                text_rect = text.get_rect(center=(pos_x, adjusted_pos_y))
                window.blit(text, text_rect)
        else:
            pos_x, pos_y, state = pos_list[0]
            text = f3.render(state, True, c1)
            text_rect = text.get_rect(center=(pos_x, pos_y))
            window.blit(text, text_rect)

def generate_positions(): #Generate valid position of states
    global ENVIRONMENT

    ENVIRONMENT.append((1, 1, 'Agent')) #Agent's position

    #Generate random positions for wumpus, pit, and gold
    num_pits = random.randint(1, grid_size)  #At least 1 pit
    num_wumpus = 1  #Only 1 wumpus
    for item, num in [('Pit', num_pits), ('Wumpus', num_wumpus), ('Glitter(Au)', 1)]:
        for _ in range(num):
            x = random.randint(1, grid_size)
            y = random.randint(1, grid_size)
            while (x, y) in [pos[:2] for pos in ENVIRONMENT] or \
                    (item == 'Wumpus' and (x, y) == (1, 2)) or \
                    (item == 'Wumpus' and (x, y) == (2, 1)) or \
                    (item == 'Pit' and (x, y) == (1, 2)) or \
                    (item == 'Pit' and (x, y) == (2, 1)) or \
                    (item == 'Wumpus' and (x, y) == (1, 1)) or \
                    (item == 'Pit' and (x, y) == (1, 1)) or \
                    (item == 'Glitter(Au)' and (x, y) == (1, 1)) or \
                    ((x, y) == (1, 2) and (x - 1, y) == (2, 1)) or \
                    ((x, y) == (2, 1) and (x - 1, y) == (1, 2)):
                x = random.randint(1, grid_size)
                y = random.randint(1, grid_size)
            ENVIRONMENT.append((x, y, item))

    #Ensure no overlapping of wumpus, pit, and gold
    for i in range(len(ENVIRONMENT)):
        for j in range(i + 1, len(ENVIRONMENT)):
            if ENVIRONMENT[i][2] != ENVIRONMENT[j][2] and ENVIRONMENT[i][:2] == ENVIRONMENT[j][:2]:
                # Remove one of the conflicting positions
                ENVIRONMENT.pop(j)
                break

    #Generate breeze and stench based on pit and wumpus positions
    pit_positions = [pos for pos in ENVIRONMENT if pos[2] == 'Pit']
    wumpus_positions = [pos for pos in ENVIRONMENT if pos[2] == 'Wumpus']

    for pit_pos in pit_positions:
        #Generate breeze around each pit
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x = pit_pos[0] + dx
            y = pit_pos[1] + dy
            if 1 <= x <= grid_size and 1 <= y <= grid_size and (x, y, 'Breeze') not in ENVIRONMENT:
                ENVIRONMENT.append((x, y, 'Breeze'))

    for wumpus_pos in wumpus_positions:
        #Generate stench around each wumpus
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x = wumpus_pos[0] + dx
            y = wumpus_pos[1] + dy
            if 1 <= x <= grid_size and 1 <= y <= grid_size and (x, y, 'Stench') not in ENVIRONMENT:
                ENVIRONMENT.append((x, y, 'Stench'))

def reset():
    global ENVIRONMENT, SOLVING_PHASE, GOLD_FOUND, POINTS, ARROW, AGENT_KNOWLEDGE_BASE, AGENT_OUTSIDE_CAVE, AGENT_POS, WUMPUS_POS, PIT_POS, GOLD_POS, START_POS

    ENVIRONMENT = []
    SOLVING_PHASE = False
    POINTS = 0
    GOLD_FOUND = False
    ARROW = 1
    AGENT_OUTSIDE_CAVE = False
    AGENT_KNOWLEDGE_BASE = {} #NAKA USUAL POS 

    AGENT_POS = (1,1) #NAKA CUSTOM POS 
    WUMPUS_POS = ()
    PIT_POS = []
    GOLD_POS = ()
    START_POS = (1,1)

def display_entry():
    global entryBTN, entryBTN_rects
   
    statement = f5.render("'Board was successfully generated.'", True, c4)
    statementRect = statement.get_rect(center=(width / 2, 545))
    window.blit(statement, statementRect)

    button_width = 200
    button_height = 45
    spacing = 40

    entryBTN = ["Show Board", "Proceed"]

    button_surfaces = [f4.render(text, True, c1) for text in entryBTN]

    total_width = len(entryBTN) * button_width + (len(entryBTN) - 1) * spacing
    start_x = (width - total_width) // 2

    #Create rectangles with proper spacing
    entryBTN_rects = [pg.Rect(start_x + (button_width + spacing) * i, 580, button_width, button_height) for i in range(len(entryBTN))]


    #check for mouse hover over buttons
    mouse_pos = pg.mouse.get_pos()
    for n, rect in enumerate(entryBTN_rects):
        if rect.collidepoint(mouse_pos):
            pg.draw.rect(window, c3, rect)  #Change color to green if hovered
        else:
            pg.draw.rect(window, c2, rect)  #Otherwise, use default blue color

        text_surface = button_surfaces[n]
        text_rect = text_surface.get_rect()
        text_rect.center = rect.center #center texts in rect

        window.blit(text_surface, text_rect)
    
    pg.display.flip()

def wumpus_world():
    global SOLVING_PHASE

    bgColor = bg_gradient()
    window.blit(bgColor, (0, 0))

    generate_positions()
    print("Board was successfully generated.")
    show_board = False

    running = True
    while running and not SOLVING_PHASE:
        draw_grid(show_board)
        display_entry()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()

                for n, rect in enumerate(entryBTN_rects):
                        if rect.collidepoint(mouse_pos):
                            if entryBTN[n] == "Show Board":
                                print("Showing board...")
                                print("Developer Mode")
                                show_board = True
                                window.blit(bgColor, (0, 0))
                                draw_grid(show_board)
                                draw_positions()
                            elif entryBTN[n] == "Proceed":
                                print("Proceeding to Agent...")
                                SOLVING_PHASE = True

    solve_wumpus_world() 
    reset()

def menu():
    global button_texts, button_rects

    bgColor = bg_gradient()
    window.blit(bgColor, (0, 0))

    header = f1.render("WUMPUS", True, c1)
    headerRect = header.get_rect(center=(width / 2, 100))
    window.blit(header, headerRect)
    header1 = f1.render("WORLD", True, c1)
    header1Rect = header1.get_rect(center=(width / 2, 200))
    window.blit(header1, header1Rect)
    header2 = f1.render("AGENT", True, c1)
    header2Rect = header2.get_rect(center=(width / 2, 300))
    window.blit(header2, header2Rect)


    button_width = 250
    button_height = 60

    #Define button texts
    button_texts = ["Start", "Quit"]

    #render the texts and get their rectangles
    button_surfaces = [f2.render(text, True, c1) for text in button_texts]
    button_rects = [pg.Rect((width - button_width) // 2, 420 + i * 70, button_width, button_height) for i in range(len(button_texts))]


    #check for mouse hover over buttons
    mouse_pos = pg.mouse.get_pos()
    for n, rect in enumerate(button_rects):
        if rect.collidepoint(mouse_pos):
            pg.draw.rect(window, c3, rect)  #Change color to green if hovered
        else:
            pg.draw.rect(window, c2, rect)  #Otherwise, use default blue color
        

        text_surface = button_surfaces[n]
        text_rect = text_surface.get_rect()
        text_rect.center = rect.center #center texts in rect

        window.blit(text_surface, text_rect)

    pg.display.flip()

def main():
    running = True
    while running:
        bgColor = bg_gradient()
        window.blit(bgColor, (0, 0))
        menu()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()

                for n, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        if button_texts[n] == "Start":
                            print("Starting the game...")
                            wumpus_world()
                        elif button_texts[n] == "Quit":
                            print("Quitting the game...")
                            pg.quit()
                            sys.exit()

if __name__ == "__main__":
    main()