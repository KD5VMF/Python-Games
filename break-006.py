import pygame
import random
import time
import os

# Initialize Pygame
pygame.init()

# Game Settings

# Screen settings
SCREEN_WIDTH = pygame.display.Info().current_w  # Screen width (default: full screen width)
SCREEN_HEIGHT = pygame.display.Info().current_h  # Screen height (default: full screen height)

# Define display mode (fullscreen)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Breakout-011")

# Paddle settings
PADDLE_WIDTH = SCREEN_WIDTH // 9  # Paddle width (default: 1/7th of the screen width)
PADDLE_HEIGHT = 10  # Paddle height in pixels (default: 10)
PADDLE_Y_POSITION = SCREEN_HEIGHT - 40  # Paddle Y position from the top (default: screen height - 40)
PADDLE_SPEED = 24  # Paddle speed (default: 24)

# Ball settings
BALL_SIZE = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 25  # Ball size in pixels (default: 1/25th of the smaller screen dimension)
BALL_INITIAL_SPEED_X = 6  # Ball initial speed in the X direction (default: 6)
BALL_INITIAL_SPEED_Y = -6  # Ball initial speed in the Y direction (default: -6)
BALL_SPEED_MULTIPLIER = 1.0  # Initial ball speed multiplier (default: 1.0)
BALL_SPEED_INCREMENT = 0.05  # Amount to increase ball speed on paddle hit (default: 0.05)
BALL_SPEED_MAX = 4.0  # Maximum ball speed multiplier (default: 4.0)

# Brick settings
BRICK_ROWS = 6  # Number of brick rows (default: 6)
BRICK_COLUMNS = 12  # Number of brick columns (default: 12)
BRICK_WIDTH = (SCREEN_WIDTH - SCREEN_WIDTH // 5 - SCREEN_WIDTH // 15 * 2 - 40) // BRICK_COLUMNS  # Brick width (default: adjusted to fit screen)
BRICK_HEIGHT = SCREEN_HEIGHT // 22  # Brick height in pixels (default: screen height // 22)
BRICK_SPACING = BRICK_WIDTH // 6  # Spacing between bricks (default: 1/6th of brick width)
BRICK_MARGIN = SCREEN_WIDTH // 15  # Margin on both sides for ball travel (default: 1/15th of screen width)

# Player settings
PLAYER_INITIAL_SCORE = 0  # Initial player score (default: 0)
PLAYER_MISS_PENALTY = 125  # Points deducted when a ball is missed (default: 125)
PLAYER_POINTS_PER_HIT = 5  # Points awarded for each brick hit (default: 5)
PLAYER_POINTS_PER_ROW_CLEARED = 123  # Points awarded for clearing a row of bricks (default: 123)
PLAYER_MULTI_HIT_BONUS = 10  # Bonus points for consecutive hits (default: 10)

# Other game settings
MAX_LEVEL_REACHED = 1  # Maximum level reached (default: 1)
SAVE_FILE = "max_level.txt"  # File to save the max level (default: 'max_level.txt')

# Colors (no default values as they are initialized later)
paddle_color = (255, 255, 255)
ball_color = (255, 255, 0)
background_color = (0, 0, 0)
bright_green = (57, 255, 20)
scoreboard_bg_color = (0, 0, 128)
score_color = (255, 215, 0)
miss_color = (255, 0, 0)
level_color = (0, 255, 0)

# Load the max level achieved from the save file
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as file:
        max_level_reached = int(file.read().strip())
else:
    max_level_reached = MAX_LEVEL_REACHED

# Initialize game variables
score = PLAYER_INITIAL_SCORE
misses = 0
level = 1
multi_hit_count = 0
ball_speed_multiplier = BALL_SPEED_MULTIPLIER

# Initialize ball and paddle positions
ball_dx = BALL_INITIAL_SPEED_X
ball_dy = BALL_INITIAL_SPEED_Y

# A wide range of bright colors for the bricks
bright_colors = [
    (57, 255, 20), (255, 0, 255), (0, 255, 255), (255, 255, 0),
    (255, 105, 180), (255, 69, 0), (138, 43, 226), (124, 252, 0),
    (0, 191, 255), (255, 20, 147), (127, 255, 0), (173, 255, 47),
    (34, 255, 150), (255, 140, 0), (255, 165, 0), (199, 21, 133),
    (255, 0, 127), (255, 110, 180), (0, 250, 154), (102, 255, 178),
    (240, 50, 230), (0, 255, 127), (255, 99, 71), (255, 66, 244),
    (255, 240, 31), (255, 182, 193), (173, 255, 47), (0, 255, 102),
    (255, 20, 240), (0, 128, 255)
]

def adjust_game_elements():
    global SCOREBOARD_WIDTH, paddle_x, ball_x, ball_y, brick_strength, brick_colors, brick_color_indices
    
    SCOREBOARD_WIDTH = SCREEN_WIDTH // 5  # Width of the scoreboard
    
    # Update positions
    paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
    ball_x = SCREEN_WIDTH // 2
    ball_y = PADDLE_Y_POSITION - BALL_SIZE - 3

    # Initialize brick grid
    brick_strength = [[1 for _ in range(BRICK_COLUMNS)] for _ in range(BRICK_ROWS)]
    brick_colors = [[random.choice(bright_colors) for _ in range(BRICK_COLUMNS)] for _ in range(BRICK_ROWS)]
    brick_color_indices = [[random.randint(0, len(bright_colors) - 1) for _ in range(BRICK_COLUMNS)] for _ in range(BRICK_ROWS)]

# Function to draw the scoreboard
def draw_scoreboard():
    pygame.draw.rect(screen, scoreboard_bg_color, (0, 0, SCOREBOARD_WIDTH, SCREEN_HEIGHT))
    
    # Dynamic font size based on screen height
    font_size = SCREEN_HEIGHT // 20
    font = pygame.font.SysFont(None, font_size)
    
    # Calculate vertical spacing
    label_spacing = SCREEN_HEIGHT // 6
    value_spacing = label_spacing + (font_size // 1.5)  # Adjusted to bring values closer to labels
    
    # Display the labels and values
    labels = ["Score", "Misses", "Level", "Max Level"]
    values = [score, misses, level, max_level_reached]
    colors = [score_color, miss_color, level_color, score_color]

    for i in range(4):
        label_text = font.render(labels[i], True, colors[i])
        value_text = font.render(str(values[i]), True, colors[i])
        screen.blit(label_text, (10, label_spacing * i + 20))
        screen.blit(value_text, (10, label_spacing * i + 60))  # Adjusted position for values

    # Display exit instruction at the bottom of the scoreboard
    exit_font_size = SCREEN_HEIGHT // 25
    exit_font = pygame.font.SysFont(None, exit_font_size)
    exit_text = exit_font.render("Press F8 to Exit", True, score_color)
    screen.blit(exit_text, (10, SCREEN_HEIGHT - exit_font_size - 20))


# Function to draw bricks with rounded corners
def draw_bricks():
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLUMNS):
            if brick_strength[row][col] > 0:
                x = SCOREBOARD_WIDTH + BRICK_MARGIN + col * (BRICK_WIDTH + BRICK_SPACING)
                y = row * (BRICK_HEIGHT + BRICK_SPACING) + 50
                color_index = brick_color_indices[row][col]
                pygame.draw.rect(screen, bright_colors[color_index], (x, y, BRICK_WIDTH, BRICK_HEIGHT), border_radius=10)

# Function to draw the paddle
def draw_paddle():
    pygame.draw.rect(screen, paddle_color, (paddle_x, PADDLE_Y_POSITION, PADDLE_WIDTH, PADDLE_HEIGHT))

# Function to draw the ball
def draw_ball():
    pygame.draw.circle(screen, ball_color, (int(ball_x), int(ball_y)), BALL_SIZE // 2)

# Function to reset paddle and ball position
def reset_paddle_and_ball():
    global paddle_x, ball_x, ball_y, ball_dx, ball_dy, ball_speed_multiplier
    paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
    ball_x = SCREEN_WIDTH // 2
    ball_y = PADDLE_Y_POSITION - BALL_SIZE - 3

    if random.choice([True, False]):
        ball_dx = BALL_INITIAL_SPEED_X
    else:
        ball_dx = -BALL_INITIAL_SPEED_X

    ball_dy = BALL_INITIAL_SPEED_Y
    ball_speed_multiplier = BALL_SPEED_MULTIPLIER

# Function to move the ball
def move_ball():
    global ball_x, ball_y, ball_dx, ball_dy, ball_speed_multiplier, misses, score, multi_hit_count

    ball_x += ball_dx * ball_speed_multiplier
    ball_y += ball_dy * ball_speed_multiplier

    # Ball collision with walls
    if ball_x <= SCOREBOARD_WIDTH + BALL_SIZE // 2 or ball_x >= SCREEN_WIDTH - BALL_SIZE // 2:
        ball_dx = -ball_dx
    if ball_y <= BALL_SIZE // 2:
        ball_dy = -ball_dy

    # Ball out of bounds
    if ball_y >= SCREEN_HEIGHT:
        misses += 1
        score -= PLAYER_MISS_PENALTY
        score = max(score, 0)
        reset_paddle_and_ball()
        multi_hit_count = 0

    # Ball collision with paddle
    if ball_y + BALL_SIZE // 2 >= PADDLE_Y_POSITION and paddle_x <= ball_x <= paddle_x + PADDLE_WIDTH:
        ball_dy = -ball_dy
        increase_ball_speed()
        multi_hit_count = 0

# Function to handle collisions with bricks
def check_collisions():
    global ball_dx, ball_dy, score, multi_hit_count, brick_strength, level, max_level_reached

    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLUMNS):
            if brick_strength[row][col] > 0:
                brick_x = SCOREBOARD_WIDTH + BRICK_MARGIN + col * (BRICK_WIDTH + BRICK_SPACING)
                brick_y = row * (BRICK_HEIGHT + BRICK_SPACING) + 50

                if (ball_x + BALL_SIZE / 2 > brick_x and ball_x - BALL_SIZE / 2 < brick_x + BRICK_WIDTH and
                    ball_y + BALL_SIZE / 2 > brick_y and ball_y - BALL_SIZE / 2 < brick_y + BRICK_HEIGHT):

                    ball_center_x = ball_x
                    ball_center_y = ball_y
                    brick_center_x = brick_x + BRICK_WIDTH / 2
                    brick_center_y = brick_y + BRICK_HEIGHT / 2

                    if abs(ball_center_x - brick_center_x) > abs(ball_center_y - brick_center_y):
                        ball_dx = -ball_dx
                    else:
                        ball_dy = -ball_dy

                    brick_strength[row][col] -= 1
                    if brick_strength[row][col] <= 0:
                        score += PLAYER_POINTS_PER_HIT
                        multi_hit_count += 1
                        score += multi_hit_count * PLAYER_MULTI_HIT_BONUS

                        # Rotate the brick's color upon hit
                        brick_color_indices[row][col] = (brick_color_indices[row][col] + 1) % len(bright_colors)

                        # Check if row cleared
                        if all(brick_strength[row][c] <= 0 for c in range(BRICK_COLUMNS)):
                            score += PLAYER_POINTS_PER_ROW_CLEARED

                        # Check for level progression
                        if all(brick_strength[r][c] <= 0 for r in range(BRICK_ROWS) for c in range(BRICK_COLUMNS)):
                            next_level()

# Function to increase ball speed
def increase_ball_speed():
    global ball_speed_multiplier
    ball_speed_multiplier = min(ball_speed_multiplier + BALL_SPEED_INCREMENT, BALL_SPEED_MAX)

# Function to progress to the next level
def next_level():
    global level, max_level_reached, ball_speed_multiplier, brick_strength, ball_dx, ball_dy

    level += 1

    if level > max_level_reached:
        max_level_reached = level
        with open(SAVE_FILE, "w") as file:
            file.write(str(max_level_reached))

    ball_speed_multiplier = BALL_SPEED_MULTIPLIER
    ball_dx = BALL_INITIAL_SPEED_X
    ball_dy = BALL_INITIAL_SPEED_Y

    brick_strength = [[1 for _ in range(BRICK_COLUMNS)] for _ in range(BRICK_ROWS)]
    draw_bricks()
    reset_paddle_and_ball()

# AI Function to move the paddle
def move_paddle_ai():
    global paddle_x
    target_x = ball_x - PADDLE_WIDTH / 2
    if target_x < paddle_x:
        paddle_x -= min(PADDLE_SPEED, paddle_x - target_x)
    elif target_x > paddle_x:
        paddle_x += min(PADDLE_SPEED, target_x - paddle_x)

    # Ensure the paddle stays within the screen bounds
    paddle_x = max(SCOREBOARD_WIDTH, min(paddle_x, SCREEN_WIDTH - PADDLE_WIDTH))

# Function to exit the game
def exit_game():
    pygame.quit()
    exit()

# Initial adjustment based on current screen size
adjust_game_elements()

# Game loop
running = True
while running:
    screen.fill(background_color)
    draw_scoreboard()
    draw_bricks()
    draw_paddle()
    draw_ball()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F8:
                exit_game()

    # Move the ball and check for collisions
    move_ball()
    check_collisions()

    # Move the paddle using AI
    move_paddle_ai()

    # Draw the updated frame
    pygame.display.flip()
    pygame.time.delay(10)

pygame.quit()
