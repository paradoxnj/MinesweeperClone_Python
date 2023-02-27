import pygame
import random
from queue import Queue

pygame.init()

board_size = int(input("Board Size (8 to 32): "))
if board_size > 32:
    print("Board size cannot be greater than 32!!  Setting to 32...")
    board_size = 32
elif board_size < 8:
    print("Board size cannot be less than 8!!  Setting to 8...")
    board_size = 8

SIZE = 16
ROWS, COLS = board_size, board_size
MINES = (ROWS * COLS) // (ROWS + 4)

WIDTH, HEIGHT = SIZE * COLS, SIZE * ROWS + 96
if WIDTH < 512:
    WIDTH = 512
if HEIGHT < 512:
    HEIGHT = 512

BG_COLOR = "white"

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

NUM_FONT = pygame.font.SysFont("comicsans", 16)
NUM_COLORS = {1: "black", 2: "green", 3: "red", 4: "orange", 5: "yellow", 6: "purple", 7: "blue", 8: "pink"}

MSG_FONT = pygame.font.SysFont("comicsans", 50)
HUD_FONT = pygame.font.SysFont("comicsans", 20)

RECT_COLOR = (200, 200, 200)
CLICKED_RECT_COLOR = (140, 140, 140)
BOMB_RECT_COLOR = "red"
#SIZE = WIDTH / ROWS

GAME_OVER = False
FLAG_MINE = -1

clicks = 0

def get_neighbors(row, col, rows, cols):
    neighbors = []

#    print("Row: " + str(row))
#    print("Col: " + str(col))
#    print("")
    
    if (row > 0 and row < rows - 1) and (col > 0 and col < cols - 1): # UP
        neighbors.append((row - 1, col))
#        print("UP")
    if (row >= 0 and row < rows - 1) and (col >= 0 and col < cols):  # DOWN
        neighbors.append((row + 1, col))
#        print("DOWN")
    if (row >= 0 and row < rows) and (col > 0 and col < cols - 1): # LEFT
        neighbors.append((row, col - 1))
#        print("LEFT")
    if row >= 0 and col < cols - 1:  # RIGHT
        neighbors.append((row, col + 1))
#        print("RIGHT")
    
    if row > 0 and col > 0:
        neighbors.append((row - 1, col - 1))
#        print("TOP LEFT")
    if row < rows - 1 and col < cols - 1:
        neighbors.append((row + 1, col + 1))
#        print("TOP RIGHT")
    if row < rows - 1 and col > 0 and col < cols:
        neighbors.append((row + 1, col - 1))
#        print("BOTTOM LEFT")
    if row > 0 and col < cols - 1:
        neighbors.append((row - 1, col + 1))
#        print("BOTTOM RIGHT")

    return neighbors

def create_mine_field(rows, cols, mines):
    field = [[0 for _ in range(cols)] for _ in range(rows)]
    mine_positions = set()

    print("Creating field with " + str(mines) + " mines...")
    while len(mine_positions) < mines:
        row = random.randrange(0, rows-1)
        col = random.randrange(0, cols-1)
        pos = row, col

        if pos in mine_positions:
            continue

        mine_positions.add(pos)
        field[row][col] = FLAG_MINE

    for mine in mine_positions:
        neighbors = get_neighbors(*mine, rows, cols)
        for r, c in neighbors:
            if field[r][c] != -1:
                field[r][c] += 1

    return field

def get_grid_pos(mouse_pos):
    mx, my = mouse_pos
    row = int(my // SIZE)
    col = int(mx // SIZE)
    
    return row, col

def draw(win, field, mask, flags):
    win.fill(BG_COLOR)
    
    t = HUD_FONT.render("Flags: " + str(flags), 1, "black")
    win.blit(t, (0, HEIGHT - 96 + t.get_height() / 2))

    for i, row in enumerate(field):
        y = SIZE * i
        for j, value in enumerate(row):
            x = SIZE * j

            is_covered = mask[i][j] == 0
            is_bomb = field[i][j] == -1
            is_flag = mask[i][j] == -2

            if is_flag:
                pygame.draw.rect(win, "green", (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue

            if is_covered:
                pygame.draw.rect(win, RECT_COLOR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue
            else:
                pygame.draw.rect(win, CLICKED_RECT_COLOR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                
                if is_bomb:
                    pygame.draw.rect(win, BOMB_RECT_COLOR, (x, y, SIZE, SIZE))
                    
                
            if value > 0:
                text = NUM_FONT.render(str(value), 1, NUM_COLORS[value])
                win.blit(text, (x + (SIZE/2 - text.get_width()/2), y + (SIZE/2 - text.get_height()/2)))


    pygame.display.update()

def uncover_from_pos(row, col, mask, field):
    q = Queue()
    q.put((row, col))
    visited = set()

    v = field[row][col]
    mask[row][col] = 1

    while not q.empty():
        current = q.get()

        neighbors = get_neighbors(*current, ROWS, COLS)
        for r, c in neighbors:
            if (r, c) in visited:
                continue

            value = field[r][c]
            mask[r][c] = 1
            if value == 0 and mask[r][c] != -2:
                q.put((r, c))
            
            visited.add((r, c))

def draw_lost(win, text):
    t = MSG_FONT.render(text, 1, "purple")
    win.blit(t, (WIDTH / 2 - t.get_width() / 2, HEIGHT / 2 - t.get_height() / 2))
    pygame.display.update()

def draw_win(win, text):
    t = MSG_FONT.render(text, 1, "blue")
    win.blit(t, (WIDTH / 2 - t.get_width() / 2, HEIGHT / 2 - t.get_height() / 2))
    pygame.display.update()

def check_won(win, field, mask, flags):
    # If there are still boxes unclicked then we have not won
    for i, row in enumerate(mask):
        for j, value in enumerate(row):
            if value == 0:
                return False

    for i, row in enumerate(mask):
        for j, value in enumerate(row):
            if value <= 0:
                mask[i][j] = 1

    return True

def main():
    global GAME_OVER
    global clicks
    
    flags = MINES
    run = True
    field = create_mine_field(ROWS, COLS, MINES)
    mask_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    while run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
                break

            if e.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_grid_pos(pygame.mouse.get_pos())
                if row >= ROWS or col >= COLS:
                    continue

                mouse_pressed = pygame.mouse.get_pressed()
                if mouse_pressed[0] and mask_field[row][col] != -2:
                    mask_field[row][col] = 1
                    if field[row][col] == -1:
                        GAME_OVER = True

                    if field[row][col] == 0:
                        uncover_from_pos(row, col, mask_field, field)
                        
                elif mouse_pressed[2]:
                    if mask_field[row][col] == -2:
                        mask_field[row][col] = 0
                        flags += 1
                    else:
                        if flags > 0:
                            flags -= 1
                            mask_field[row][col] = -2

        if check_won(win, field, mask_field, flags):
            draw(win, field, mask_field, flags)
            draw_win(win, "YOU WIN!!!")
            pygame.time.delay(5000)
            field = create_mine_field(ROWS, COLS, MINES)
            mask_field = [[0 for _ in range(0, COLS)] for _ in range(ROWS)]
            flags = MINES
            clicks = 0
            GAME_OVER = False
        
        if GAME_OVER:
            draw(win, field, mask_field, flags)
            draw_lost(win, "You lost!! Try again...")
            pygame.time.delay(5000)

            field = create_mine_field(ROWS, COLS, MINES)
            mask_field = [[0 for _ in range(0, COLS)] for _ in range(ROWS)]
            flags = MINES
            clicks = 0
            GAME_OVER = False

        draw(win, field, mask_field, flags)
        
    pygame.quit()


if __name__ == "__main__":
    main()
