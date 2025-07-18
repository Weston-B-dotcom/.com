import pygame
import sys

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
COYOTE_TIME_LIMIT = 0.1 # Time player can jump after leaving a platform in seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)

# Player properties
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 5
JUMP_STRENGTH = -15
GRAVITY = 0.8

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.change_x = 0
        self.change_y = 0
        self.death = False
        self.on_ground = False
        self.coyote_timer = 0.0 # New: Timer to track time since leaving ground

    def update(self, platforms):
        # Apply gravity
        self.change_y += GRAVITY
        if self.change_y > 10: # Cap falling speed
            self.change_y = 10

        # Move left/right
        self.rect.x += self.change_x

        # Check for horizontal collisions with platforms
        self.collide_horizontal(platforms)

        # Move up/down
        self.rect.y += self.change_y

        # Check for vertical collisions with platforms
        self.collide_vertical(platforms)

        # Coyote time logic:
        # If the player is currently on the ground, reset the coyote timer.
        if self.on_ground:
            self.coyote_timer = 0.0
        # If the player is in the air, increment the coyote timer.
        else:
            self.coyote_timer += (1.0 / FPS) # Increment by time per frame

        # Keep player within screen bounds horizontally
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def collide_horizontal(self, platforms):
        # Check for collisions after horizontal movement
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if platform.color == RED:
                    self.death = True
                if self.change_x > 0: # Moving right
                    self.rect.right = platform.rect.left
                elif self.change_x < 0: # Moving left
                    self.rect.left = platform.rect.right

    def collide_vertical(self, platforms):
        # Check for collisions after vertical movement
        # Temporarily set on_ground to False; it will be set to True if a collision occurs below.
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if platform.color == RED:
                    self.death = True
                elif self.change_y > 0: # Falling down, hit top of platform
                    self.rect.bottom = platform.rect.top
                    self.change_y = 0
                    self.on_ground = True # Player is now on ground
                    if platform.color == GOLD:
                        stage.stage_up()
                elif self.change_y < 0: # Jumping up, hit bottom of platform
                    self.rect.top = platform.rect.bottom
                    self.change_y = 0

        # If player falls off screen, reset position (simple death/reset)
        if self.rect.top > SCREEN_HEIGHT or self.death:
            self.rect.x = 100
            self.rect.y = 100
            self.change_y = 0
            self.on_ground = False # Player is no longer on ground after reset
            self.death = False # Player doesn't get stuck in a death loop
            self.coyote_timer = 0.0 # Reset coyote timer on death/reset

    def go_left(self):
        self.change_x = -PLAYER_SPEED

    def go_right(self):
        self.change_x = PLAYER_SPEED

    def stop(self):
        self.change_x = 0

    def jump(self):
        # Allow jumping if on the ground OR within the coyote time window
        if self.on_ground or (self.coyote_timer < COYOTE_TIME_LIMIT):
            self.change_y = JUMP_STRENGTH
            self.on_ground = False # Player is now in the air
            self.coyote_timer = COYOTE_TIME_LIMIT # Consume coyote time after jumping to prevent multiple jumps

# --- Platform Class ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, moving = False, speed = None):
        super().__init__()
        self.color = color
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

# --- Stage Class ---
class Stage:
    def __init__(self, platforms_group):
        super().__init__()
        self.platforms = platforms_group # Store the sprite group passed in
        self.number = 2

    def create_stage(self):
        # Clear existing platforms before creating a new stage
        self.platforms.empty()
        # Adds platforms to a list to be created based on stage
        if self.number == 1:
            self.platforms.add(Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH - 150, 20, GREEN))
            self.platforms.add(Platform(700, SCREEN_HEIGHT - 20, 150, 20, GOLD))
            self.platforms.add(Platform(150, SCREEN_HEIGHT - 100, 150, 20, GREEN))
            self.platforms.add(Platform(350, SCREEN_HEIGHT - 200, 100, 20, GREEN))
            self.platforms.add(Platform(550, SCREEN_HEIGHT - 100, 150, 20, RED))
            self.platforms.add(Platform(50, SCREEN_HEIGHT - 250, 80, 20, GREEN))
        elif self.number == 2:
            self.platforms.add(Platform(50, SCREEN_HEIGHT - 100, 150, 20, GREEN))
            self.platforms.add(Platform(200, SCREEN_HEIGHT - 200, 150, 20, GREEN))
            self.platforms.add(Platform(200, SCREEN_HEIGHT - 450, 20, 250, RED))
            self.platforms.add(Platform(300, SCREEN_HEIGHT - 100, 50, 20, GREEN))
            self.platforms.add(Platform(275, SCREEN_HEIGHT - 290, 50, 20, RED))
            self.platforms.add(Platform(275, SCREEN_HEIGHT - 320, 90, 20, GREEN))
            self.platforms.add(Platform(550, SCREEN_HEIGHT - 350, 100, 20, GREEN))
            self.platforms.add(Platform(350, SCREEN_HEIGHT - 320, 100, 20, RED))
            self.platforms.add(Platform(750, SCREEN_HEIGHT - 450, 100, 20, GOLD))

    def stage_up(self):
        self.number += 1
        self.create_stage() # Create the new stage when switching
        reset()

    def stage_down(self):
        if self.number != 0: # Stops player from going before the title screen
            self.number -= 1
        self.create_stage() # Create the new stage when switching
        reset()

# --- Game Setup ---
player = Player(100, SCREEN_HEIGHT - 100) # Starting position

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group() # Define the platforms sprite group

# Initialize the stage and create the initial platforms
stage = Stage(platforms)
stage.create_stage() # Create the first stage

def reset(): # Resets the screen based on stage switching
    all_sprites.empty()
    all_sprites.add(player)
    # Add all platforms from the platforms group to the all_sprites group for drawing
    for platform in platforms:
        all_sprites.add(platform)

reset()

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player.go_left()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.go_right()
            elif event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                player.jump()
            elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                stage.stage_down()
            elif event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a and player.change_x < 0:
                player.stop()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d and player.change_x > 0:
                player.stop()


    # Update game elements
    player.update(platforms) # Pass platforms to player for collision detection

    # Drawing
    screen.fill(BLACK) # Fill background

    all_sprites.draw(screen) # Draw all sprites

    # Update the display
    pygame.display.flip()

    # Control frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()