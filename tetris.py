import json
import pygame
import random
import os

pygame.init()

block_size = 30
play_width = 10 * block_size
play_height = 20 * block_size
screen_width = play_width + 250
screen_height = play_height

black = (0, 0, 0)
white = (255, 255, 255)
rgb_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

color_sets_file = "color_sets.json"
high_score_file = "high_score.json"

with open(color_sets_file) as file:
    color_sets = json.load(file)

default_colors = color_sets["1"]

if os.path.exists(high_score_file):
    with open(high_score_file) as file:
        high_score_data = json.load(file)
else:
    high_score_data = {"high_score": 0}
    with open(high_score_file, "w") as file:
        json.dump(high_score_data, file)

high_score = high_score_data["high_score"]

tetriminos = [
    [[1, 1, 1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tetris')

grid_width = 10
grid_height = 20

grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]

current_color_set = default_colors

def new_tetrimino():
    return random.choice(tetriminos), random.choice(current_color_set)

def draw_grid():
    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y][x] == 0:
                pygame.draw.rect(screen, black, pygame.Rect(x * block_size, y * block_size, block_size, block_size), 1)
            else:
                pygame.draw.rect(screen, grid[y][x], pygame.Rect(x * block_size, y * block_size, block_size, block_size))
                pygame.draw.rect(screen, white, pygame.Rect(x * block_size, y * block_size, block_size, block_size), 1)

def draw_tetrimino(tetrimino, offset):
    shape, color = tetrimino
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color, pygame.Rect((off_x + x) * block_size, (off_y + y) * block_size, block_size, block_size))
                pygame.draw.rect(screen, white, pygame.Rect((off_x + x) * block_size, (off_y + y) * block_size, block_size, block_size), 1)

def valid_position(tetrimino, offset):
    shape, _ = tetrimino
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if x + off_x < 0 or x + off_x >= grid_width or y + off_y >= grid_height:
                    return False
                if grid[y + off_y][x + off_x]:
                    return False
    return True

def merge(tetrimino, offset):
    shape, color = tetrimino
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid[y + off_y][x + off_x] = color

def clear_lines():
    global grid, score, lines_cleared, level
    lines_cleared_this_turn = 0
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    lines_cleared_this_turn = grid_height - len(new_grid)
    lines_cleared += lines_cleared_this_turn
    new_grid = [[0 for _ in range(grid_width)] for _ in range(grid_height - len(new_grid))] + new_grid
    grid = new_grid
    
    base_score = [0, 40, 100, 300, 1200]
    if level in range(2, 4):
        multiplier = 2
    elif level >= 10:
        multiplier = 10
    else:
        multiplier = 1

    if lines_cleared_this_turn <= 4:
        score += base_score[lines_cleared_this_turn] * multiplier

    return lines_cleared_this_turn

def draw_hud(held_tetrimino, score, level, lines_cleared, next_tetrimino, high_score):
    pygame.draw.line(screen, white, (play_width, 0), (play_width, screen_height), 3)
    font = pygame.font.Font(None, 36)
    text_top = font.render(f'Top: {high_score}', True, white)
    text_score = font.render(f'Score: {score}', True, white)
    text_level = font.render(f'Level: {level}', True, white)
    text_lines = font.render(f'Lines: {lines_cleared}', True, white)
    text_how = font.render(f'How to play', True, white)
    text_controls = font.render(f'WASD or arrow keys', True, white)
    text_hold = font.render(f'Shift to hold', True, white)
    text_exit = font.render(f'ESP to exit', True, white)
    screen.blit(text_top, (play_width + 20, 0))
    screen.blit(text_score, (play_width + 20, 40))
    screen.blit(text_level, (play_width + 20, 80))
    screen.blit(text_lines, (play_width + 20, 120))
    screen.blit(text_how, (play_width + 5, 425))
    screen.blit(text_controls, (play_width + 5, 455))
    screen.blit(text_hold, (play_width + 5, 485))
    screen.blit(text_exit, (play_width + 5, 515))

    next_shape, next_color = next_tetrimino
    for y, row in enumerate(next_shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, next_color, pygame.Rect(play_width + 20 + x * block_size, 180 + y * block_size, block_size, block_size))
                pygame.draw.rect(screen, white, pygame.Rect(play_width + 20 + x * block_size, 180 + y * block_size, block_size, block_size), 1)

    if held_tetrimino:
        shape, color = held_tetrimino
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, color, pygame.Rect(play_width + 20 + x * block_size, 300 + y * block_size, block_size, block_size))
                    pygame.draw.rect(screen, white, pygame.Rect(play_width + 20 + x * block_size, 300 + y * block_size, block_size, block_size), 1)
    
    pygame.draw.rect(screen, white, pygame.Rect(play_width + 10, 290, 130, 130), 2)
    pygame.draw.rect(screen, white, pygame.Rect(play_width + 10, 170, 130, 100), 2)

def change_grid_colors(new_color_set):
    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y][x] != 0:
                current_color = grid[y][x]
                try:
                    new_color = new_color_set[current_color_set.index(current_color)]
                    grid[y][x] = new_color
                except ValueError:
                    print(f"Color {current_color} not found in the current color set.")
                    grid[y][x] = random.choice(new_color_set)

def save_high_score(new_high_score):
    with open(high_score_file, "w") as file:
        json.dump({"high_score": new_high_score}, file)

def flash_tetris():
    font = pygame.font.Font(None, 74)
    for _ in range(2):
        for color in rgb_colors:
            text_tetris = font.render("TETRIS", True, color)
            screen.blit(text_tetris, (play_width // 2 - 100, play_height // 2 - 50))
            pygame.display.flip()
            pygame.time.delay(50)
            screen.fill(black)
            pygame.display.flip()
            pygame.time.delay(50)

def main():
    global grid, score, lines_cleared, current_color_set, fps, level
    clock = pygame.time.Clock()
    tetrimino = new_tetrimino()
    next_tetrimino = new_tetrimino()
    offset = [grid_width // 2 - len(tetrimino[0][0]) // 2, 0]
    drop_time = 0
    game_over = False
    held_tetrimino = None
    held_used = False
    score = 0
    lines_cleared = 0
    level = 1
    current_color_set = default_colors
    fps = 20
    fall_speed = fps // 2

    move_left = move_right = False
    move_delay = 0
    initial_delay = 200
    repeat_delay = 50

    while not game_over:
        screen.fill(black)
        draw_grid()
        draw_tetrimino(tetrimino, offset)
        draw_hud(held_tetrimino, score, level, lines_cleared, next_tetrimino, high_score)
        pygame.display.flip()

        drop_time += 1
        if drop_time >= fall_speed:
            drop_time = 0
            offset[1] += 1
            if not valid_position(tetrimino, offset):
                offset[1] -= 1
                merge(tetrimino, offset)
                lines_cleared_this_turn = clear_lines()
                if lines_cleared_this_turn == 4:
                    flash_tetris()
                tetrimino = next_tetrimino
                next_tetrimino = new_tetrimino()
                offset = [grid_width // 2 - len(tetrimino[0][0]) // 2, 0]
                held_used = False
                if not valid_position(tetrimino, offset):
                    game_over = True
                if lines_cleared >= level * 10:
                    level += 1
                    if level <= 15:
                        fall_speed = max(int(fps // (1.4 ** level)), 1)
                    new_color_set = random.choice([color_sets[str(i)] for i in range(2, 21)])
                    change_grid_colors(new_color_set)
                    current_color_set = new_color_set

        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            offset[1] += 1
            if not valid_position(tetrimino, offset):
                offset[1] -= 1

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if not move_left or current_time - move_delay > repeat_delay:
                offset[0] -= 1
                if not valid_position(tetrimino, offset):
                    offset[0] += 1
                move_left = True
                move_delay = current_time
        else:
            move_left = False

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if not move_right or current_time - move_delay > repeat_delay:
                offset[0] += 1
                if not valid_position(tetrimino, offset):
                    offset[0] -= 1
                move_right = True
                move_delay = current_time
        else:
            move_right = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_over = True
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    tetrimino = (list(zip(*tetrimino[0][::-1])), tetrimino[1])
                    if not valid_position(tetrimino, offset):
                        tetrimino = (list(zip(*tetrimino[0]))[::-1], tetrimino[1])
                elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                    if not held_used:
                        if held_tetrimino:
                            tetrimino, held_tetrimino = held_tetrimino, tetrimino
                        else:
                            held_tetrimino = tetrimino
                            tetrimino = next_tetrimino
                            next_tetrimino = new_tetrimino()
                        offset = [grid_width // 2 - len(tetrimino[0][0]) // 2, 0]
                        held_used = True

        clock.tick(fps)

    if score > high_score:
        save_high_score(score)

if __name__ == "__main__":
    main()
    pygame.quit()
