import random
import pygame
import sys
import math
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 800

# Setup screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# Load and scale spaceship image
if getattr(sys, 'frozen', False):
    # Running from a PyInstaller bundle (e.g., .exe)
    base_path = sys._MEIPASS  # Temporary folder where PyInstaller extracts files
else:
    # Running in source code (development mode)
    base_path = os.path.abspath(".")

# Construct the path to the image
spaceship_image_path = os.path.join(base_path, 'assets', 'Spaceship.png')

# Load the spaceship image
spaceship_image = pygame.image.load(spaceship_image_path)
spaceship_image = pygame.transform.scale(spaceship_image, (50, 50))

# Enemy Image
if getattr(sys, 'frozen', False):
    # Running from a PyInstaller bundle (e.g., .exe)
    base_path = sys._MEIPASS  # Temporary folder where PyInstaller extracts files
else:
    # Running in source code (development mode)
    base_path = os.path.abspath(".")

# Construct the path to the image
enemy_image_path = os.path.join(base_path, 'assets', 'Enemy.png')

# Load the spaceship image
enemy_image = pygame.image.load(enemy_image_path)
enemy_image = pygame.transform.scale(enemy_image, (50, 50))

# Sounds
if getattr(sys, 'frozen', False):
    # Running from a PyInstaller bundle (e.g., .exe)
    base_path = sys._MEIPASS  # Temporary folder where PyInstaller extracts files
else:
    # Running in source code (development mode)
    base_path = os.path.abspath(".")

# Construct the path to the image
enemy_hit_path = os.path.join(base_path, 'assets', 'Enemy_hit_sound.wav')
enemy_hit = pygame.mixer.Sound(enemy_hit_path)


# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Font for text
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Player properties
player_x = screen_width // 2
player_y = screen_height // 2
player_speed = 0.2
max_speed = 5
deceleration = 0.05
player_health = 1

# Initial velocity and rotation
velocity_x = 0
velocity_y = 0
current_angle = 0

# Bullets
bullets = []
bullet_speed = 10

# Enemies
enemies = []
enemy_speed = 2
enemy_spawn_rate = 60  # Frames per enemy spawn

# Score
score = 0

# Game state flags
MAIN_MENU = True
GAME_RUNNING = False
GAME_OVER = False


# Reset the game state
def reset_game():
    global player_x, player_y, player_health, velocity_x, velocity_y, score
    global enemies, bullets, current_angle, enemy_spawn_rate, enemy_speed
    global MAIN_MENU, GAME_RUNNING, GAME_OVER

    # Reset player and game variables
    player_x = screen_width // 2
    player_y = screen_height // 2
    player_health = 1
    velocity_x = 0
    velocity_y = 0
    score = 0
    enemies = []
    bullets = []
    current_angle = 0

    # Reset difficulty scaling
    enemy_spawn_rate = 60
    enemy_speed = 2

    # Set game state flags
    MAIN_MENU = True
    GAME_RUNNING = False
    GAME_OVER = False


# Function to display the main menu
def show_main_menu():
    screen.fill(BLACK)
    title_text = large_font.render("Space Shooter", True, WHITE)
    start_text = font.render("Press S to Start", True, WHITE)
    quit_text = font.render("Press Q to Quit", True, WHITE)

    # Center the text
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 3))
    screen.blit(start_text, (screen_width // 2 - start_text.get_width() // 2, screen_height // 2))
    screen.blit(quit_text, (screen_width // 2 - quit_text.get_width() // 2, screen_height // 2 + 40))

    pygame.display.flip()


# Function to display game over screen
def show_game_over():
    screen.fill(BLACK)
    game_over_text = large_font.render("Game Over", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    menu_text = font.render("Press M for Main Menu", True, WHITE)

    # Center the text
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 3))
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2))
    screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2 + 40))
    screen.blit(menu_text, (screen_width // 2 - menu_text.get_width() // 2, screen_height // 2 + 80))

    pygame.display.flip()


# Main game loop
reset_game()  # Ensure initial reset
frame_count = 0

while True:
    # Main Menu Loop
    while MAIN_MENU:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:  # Start game
            MAIN_MENU = False
            GAME_RUNNING = True
        elif keys[pygame.K_q]:  # Quit game
            pygame.quit()
            sys.exit()

        show_main_menu()


    # Game loop
    while GAME_RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        # Game over logic
        if player_health <= 0:
            GAME_RUNNING = False
            GAME_OVER = True
            break

        # Movement logic
        velocity_x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
        velocity_y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * player_speed

        # Deceleration
        if velocity_x > 0:
            velocity_x -= deceleration
        elif velocity_x < 0:
            velocity_x += deceleration
        if velocity_y > 0:
            velocity_y -= deceleration
        elif velocity_y < 0:
            velocity_y += deceleration

        # Prevent jitter near zero velocity
        if abs(velocity_x) < deceleration:
            velocity_x = 0
        if abs(velocity_y) < deceleration:
            velocity_y = 0

        # Update player position and enforce boundaries
        player_x = max(25, min(screen_width - 25, player_x + velocity_x))
        player_y = max(25, min(screen_height - 25, player_y + velocity_y))

        # Calculate rotation angle
        if velocity_x != 0 or velocity_y != 0:  # Only update angle if moving
            current_angle = math.degrees(math.atan2(-velocity_y, velocity_x)) - 90

        # Fire bullets
        if keys[pygame.K_SPACE]:
            bullet_x = player_x
            bullet_y = player_y
            angle_radians = math.radians(current_angle - 90)
            bullet_dx = math.cos(angle_radians) * bullet_speed
            bullet_dy = math.sin(angle_radians) * bullet_speed

            if -90 <= current_angle <= 270:
                bullet_dx = -bullet_dx

            bullets.append({"x": bullet_x, "y": bullet_y, "dx": bullet_dx, "dy": bullet_dy})


        # Update bullets
        for bullet in bullets[:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]
            if bullet["x"] < 0 or bullet["x"] > screen_width or bullet["y"] < 0 or bullet["y"] > screen_height:
                bullets.remove(bullet)

            # Bullet collision with enemies
            for enemy in enemies[:]:
                # Calculate the distance between the bullet and the enemy
                distance = math.sqrt((bullet["x"] - enemy["x"]) ** 2 + (bullet["y"] - enemy["y"]) ** 2)

                # Check if the distance is smaller than a set threshold (25 pixels)
                if distance < 25:
                    bullets.remove(bullet)  # Remove bullet
                    enemies.remove(enemy)  # Remove enemy
                    score += 1  # Increment score
                    break  # Exit the loop once a collision is detected

        # Spawn enemies
        frame_count += 1
        if frame_count % enemy_spawn_rate == 0:
            enemies.append({"x": random.randint(50, screen_width - 50), "y": 50})

        # Move enemies towards player
        for enemy in enemies:
            dx = player_x - enemy["x"]
            dy = player_y - enemy["y"]
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance != 0:
                enemy["x"] += dx / distance * enemy_speed
                enemy["y"] += dy / distance * enemy_speed

        # Check for collisions (player and enemies)
        for enemy in enemies[:]:
            distance = math.sqrt((player_x - enemy["x"]) ** 2 + (player_y - enemy["y"]) ** 2)
            if distance < 25:
                player_health = 0

        # Draw everything
        screen.fill(BLACK)

        # Rotate and draw the spaceship
        rotated_image = pygame.transform.rotate(spaceship_image, current_angle)
        image_rect = rotated_image.get_rect(center=(player_x, player_y))
        screen.blit(rotated_image, image_rect.topleft)

        # Draw enemies
        for enemy in enemies:
            screen.blit(enemy_image, (enemy["x"], enemy["y"]))

        # Draw bullets
        for bullet in bullets:
            pygame.draw.circle(screen, (255, 255, 0), (int(bullet["x"]), int(bullet["y"])), 5)

        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Refresh screen
        pygame.display.flip()
        clock.tick(60)

    # Game Over Loop
    while GAME_OVER:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_game()
        elif keys[pygame.K_m]:
            reset_game()

        show_game_over()

