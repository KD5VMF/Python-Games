
import pygame
import random
import time
import os
import math

# Seed the random generator using system time
random.seed(time.time())

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Breakout-Randomized")

# Paddle settings
PADDLE_WIDTH = SCREEN_WIDTH // 9
PADDLE_HEIGHT = 10
PADDLE_Y_POSITION = SCREEN_HEIGHT - 40
PADDLE_SPEED = 24

# Ball settings
BALL_SIZE = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 25
BALL_INITIAL_SPEED_X = 6
BALL_INITIAL_SPEED_Y = -6
BALL_SPEED_MULTIPLIER = 1.0
BALL_SPEED_INCREMENT = 0.05
BALL_SPEED_MAX = 4.0
MIN_BALL_SPEED = 2.0

# Brick settings
BRICK_ROWS = 6
BRICK_COLUMNS = 12
BRICK_WIDTH = (SCREEN_WIDTH - SCREEN_WIDTH // 5 - SCREEN_WIDTH // 15 * 2 - 40) // BRICK_COLUMNS
BRICK_HEIGHT = SCREEN_HEIGHT // 22
BRICK_SPACING = BRICK_WIDTH // 6
BRICK_MARGIN = SCREEN_WIDTH // 15

# Player settings
PLAYER_INITIAL_SCORE = 0
PLAYER_MISS_PENALTY = 125
PLAYER_POINTS_PER_HIT = 5
PLAYER_POINTS_PER_ROW_CLEARED = 123
PLAYER_MULTI_HIT_BONUS = 10

# Save file
SAVE_FILE = "max_level.txt"

# Colors
paddle_color = (255, 255, 255)
ball_color = (255, 255, 0)
background_color = (0, 0, 0)
bright_colors = [(57, 255, 20), (255, 0, 255), (0, 255, 255), (255, 255, 0),
                 (255, 105, 180), (255, 69, 0), (138, 43, 226), (124, 252, 0),
                 (0, 191, 255), (255, 20, 147), (127, 255, 0), (173, 255, 47)]

# Loop detector vars
last_positions = []
LOOP_DETECT_FRAMES = 100
LOOP_DETECT_THRESHOLD_X_MOVEMENT = 20
LOOP_DETECT_THRESHOLD_Y_DIRECTION = 0.9

# Load saved max level
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as file:
        max_level_reached = int(file.read().strip())
else:
    max_level_reached = 1

score = PLAYER_INITIAL_SCORE
misses = 0
level = 1
multi_hit_count = 0
ball_speed_multiplier = BALL_SPEED_MULTIPLIER
ball_dx = BALL_INITIAL_SPEED_X if random.choice([True, False]) else -BALL_INITIAL_SPEED_X
ball_dy = BALL_INITIAL_SPEED_Y

MIN_ANGLE = 0.2
NUDGE_FACTOR = 0.1


def adjust_game_elements():
    global SCOREBOARD_WIDTH, paddle_x, ball_x, ball_y, brick_strength, brick_color_indices
    SCOREBOARD_WIDTH = SCREEN_WIDTH // 5
    paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
    ball_x = SCREEN_WIDTH // 2
    ball_y = PADDLE_Y_POSITION - BALL_SIZE - 3
    brick_strength = [[random.randint(1, 2) for _ in range(BRICK_COLUMNS)] for _ in range(BRICK_ROWS)]
    brick_color_indices = [[random.randint(0, len(bright_colors) - 1) for _ in range(BRICK_COLUMNS)] for _ in range(BRICK_ROWS)]


def prevent_stuck():
    global ball_dx, ball_dy
    angle = math.atan2(ball_dy, ball_dx)
    if abs(math.cos(angle)) < MIN_ANGLE:
        ball_dx += NUDGE_FACTOR if ball_dx > 0 else -NUDGE_FACTOR
    if abs(math.sin(angle)) < MIN_ANGLE:
        ball_dy += NUDGE_FACTOR if ball_dy > 0 else -NUDGE_FACTOR


def ensure_minimum_ball_motion():
    global ball_dx, ball_dy
    if abs(ball_dx) < MIN_BALL_SPEED:
        ball_dx = MIN_BALL_SPEED if ball_dx >= 0 else -MIN_BALL_SPEED
    if abs(ball_dy) < MIN_BALL_SPEED:
        ball_dy = MIN_BALL_SPEED if ball_dy >= 0 else -MIN_BALL_SPEED


def detect_and_prevent_loop():
    global ball_dx, ball_dy, last_positions
    last_positions.append((ball_x, ball_y))
    if len(last_positions) > LOOP_DETECT_FRAMES:
        last_positions.pop(0)
        x_positions = [pos[0] for pos in last_positions]
        min_x, max_x = min(x_positions), max(x_positions)
        if max_x - min_x < LOOP_DETECT_THRESHOLD_X_MOVEMENT:
            if abs(ball_dy) / (abs(ball_dx) + 0.1) > LOOP_DETECT_THRESHOLD_Y_DIRECTION:
                ball_dx += random.choice([-1, 1]) * random.uniform(3.0, 5.0)
                ball_dy = -abs(ball_dy) if ball_dy > 0 else abs(ball_dy)
                ensure_minimum_ball_motion()
                last_positions.clear()


def move_ball():
    global ball_x, ball_y, ball_dx, ball_dy, ball_speed_multiplier, misses, score, multi_hit_count
    ball_x += ball_dx * ball_speed_multiplier
    ball_y += ball_dy * ball_speed_multiplier

    bounced = False

    if ball_x <= SCOREBOARD_WIDTH + BALL_SIZE // 2 or ball_x >= SCREEN_WIDTH - BALL_SIZE // 2:
        ball_dx = -ball_dx
        bounced = True
    if ball_y <= BALL_SIZE // 2:
        ball_dy = -ball_dy
        bounced = True
    if ball_y >= SCREEN_HEIGHT:
        misses += 1
        score = max(score - PLAYER_MISS_PENALTY, 0)
        reset_paddle_and_ball()
        multi_hit_count = 0
        last_positions.clear()
        return
    if ball_y + BALL_SIZE // 2 >= PADDLE_Y_POSITION and paddle_x <= ball_x <= paddle_x + PADDLE_WIDTH:
        hit_pos = ((ball_x - paddle_x) - PADDLE_WIDTH / 2) / (PADDLE_WIDTH / 2)
        ball_dx = BALL_INITIAL_SPEED_X * hit_pos
        ball_dy = -abs(ball_dy)
        increase_ball_speed()
        prevent_stuck()
        ensure_minimum_ball_motion()
        multi_hit_count = 0
        bounced = True

    if bounced:
        prevent_stuck()
        ensure_minimum_ball_motion()

    detect_and_prevent_loop()


def check_collisions():
    global ball_dx, ball_dy, score, multi_hit_count, brick_strength, level, max_level_reached
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLUMNS):
            if brick_strength[row][col] > 0:
                x = SCOREBOARD_WIDTH + BRICK_MARGIN + col * (BRICK_WIDTH + BRICK_SPACING)
                y = row * (BRICK_HEIGHT + BRICK_SPACING) + 50
                if (ball_x + BALL_SIZE / 2 > x and ball_x - BALL_SIZE / 2 < x + BRICK_WIDTH and
                        ball_y + BALL_SIZE / 2 > y and ball_y - BALL_SIZE / 2 < y + BRICK_HEIGHT):
                    ball_dx = -ball_dx if abs(ball_x - (x + BRICK_WIDTH / 2)) > abs(ball_y - (y + BRICK_HEIGHT / 2)) else ball_dx
                    ball_dy = -ball_dy if abs(ball_y - (y + BRICK_HEIGHT / 2)) > abs(ball_x - (x + BRICK_WIDTH / 2)) else ball_dy
                    prevent_stuck()
                    ensure_minimum_ball_motion()
                    brick_strength[row][col] -= 1
                    score += PLAYER_POINTS_PER_HIT
                    multi_hit_count += 1
                    score += multi_hit_count * PLAYER_MULTI_HIT_BONUS
                    brick_color_indices[row][col] = random.randint(0, len(bright_colors) - 1)
                    if all(brick_strength[r][c] <= 0 for r in range(BRICK_ROWS) for c in range(BRICK_COLUMNS)):
                        next_level()


def reset_paddle_and_ball():
    global paddle_x, ball_x, ball_y, ball_dx, ball_dy, ball_speed_multiplier
    paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
    ball_x = SCREEN_WIDTH // 2
    ball_y = PADDLE_Y_POSITION - BALL_SIZE - 3
    ball_dx = BALL_INITIAL_SPEED_X if random.choice([True, False]) else -BALL_INITIAL_SPEED_X
    ball_dy = BALL_INITIAL_SPEED_Y
    ball_speed_multiplier = BALL_SPEED_MULTIPLIER


def increase_ball_speed():
    global ball_speed_multiplier
    ball_speed_multiplier = min(ball_speed_multiplier + BALL_SPEED_INCREMENT, BALL_SPEED_MAX)


def next_level():
    global level, max_level_reached
    level += 1
    if level > max_level_reached:
        max_level_reached = level
        with open(SAVE_FILE, "w") as file:
            file.write(str(max_level_reached))
    adjust_game_elements()
    reset_paddle_and_ball()


def move_paddle_ai():
    global paddle_x
    target_x = ball_x - PADDLE_WIDTH / 2
    paddle_x += min(PADDLE_SPEED, abs(paddle_x - target_x)) * (1 if target_x > paddle_x else -1)
    paddle_x = max(SCOREBOARD_WIDTH, min(paddle_x, SCREEN_WIDTH - PADDLE_WIDTH))


def draw_scoreboard():
    pygame.draw.rect(screen, (0, 0, 128), (0, 0, SCOREBOARD_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont(None, SCREEN_HEIGHT // 20)
    info = [("Score", score), ("Misses", misses), ("Level", level), ("Max Level", max_level_reached)]
    colors = [(255, 215, 0), (255, 0, 0), (0, 255, 0), (255, 215, 0)]
    for i, (label, value) in enumerate(info):
        screen.blit(font.render(label, True, colors[i]), (10, 60 * i + 20))
        screen.blit(font.render(str(value), True, colors[i]), (10, 60 * i + 50))
    exit_msg = pygame.font.SysFont(None, SCREEN_HEIGHT // 25).render("Press F8 to Exit", True, (255, 255, 0))
    screen.blit(exit_msg, (10, SCREEN_HEIGHT - 40))


def draw_bricks():
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLUMNS):
            if brick_strength[row][col] > 0:
                x = SCOREBOARD_WIDTH + BRICK_MARGIN + col * (BRICK_WIDTH + BRICK_SPACING)
                y = row * (BRICK_HEIGHT + BRICK_SPACING) + 50
                color = bright_colors[brick_color_indices[row][col]]
                pygame.draw.rect(screen, color, (x, y, BRICK_WIDTH, BRICK_HEIGHT), border_radius=10)


def draw_paddle():
    pygame.draw.rect(screen, paddle_color, (paddle_x, PADDLE_Y_POSITION, PADDLE_WIDTH, PADDLE_HEIGHT))


def draw_ball():
    pygame.draw.circle(screen, ball_color, (int(ball_x), int(ball_y)), BALL_SIZE // 2)


# Main game loop
adjust_game_elements()
running = True
while running:
    screen.fill(background_color)
    draw_scoreboard()
    draw_bricks()
    draw_paddle()
    draw_ball()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_F8):
            running = False

    move_ball()
    check_collisions()
    move_paddle_ai()
    pygame.display.flip()
    pygame.time.delay(10)

pygame.quit()
