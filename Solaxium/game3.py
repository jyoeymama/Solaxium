import pygame
import sys
import random
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5
MAX_LEVEL = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
PLATFORM_COLOR = (100, 100, 100)
ORANGE = (255, 165, 0)
BACKGROUND_COLORS = [
    (135, 206, 235),  # Level 1 - Sky blue
    (100, 149, 237),  # Level 2 - Cornflower blue
    (70, 130, 180),   # Level 3 - Steel blue
    (65, 105, 225),   # Level 4 - Royal blue
    (25, 25, 112)     # Level 5 - Midnight blue
]

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solaxium Platformer")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)

# Sound effects
try:
    jump_sound = mixer.Sound('jump.wav')
    coin_sound = mixer.Sound('coin.wav')
    hurt_sound = mixer.Sound('hurt.wav')
    powerup_sound = mixer.Sound('powerup.wav')
except:
    # Dummy sound objects if files don't exist
    class DummySound:
        def play(self): pass
    jump_sound = coin_sound = hurt_sound = powerup_sound = DummySound()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 4, HEIGHT // 2)
        self.velocity_y = 0
        self.on_ground = False
        self.score = 0
        self.health = 3
        self.jumps_left = 1  # Single jump by default
        self.max_jumps = 1
        self.invincible = False
        self.invincible_timer = 0
        
    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        
        # Update invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.image.fill(RED)
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True
            self.velocity_y = 0
            self.jumps_left = self.max_jumps
            
    def jump(self):
        if self.jumps_left > 0:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False
            self.jumps_left -= 1
            jump_sound.play()
            
    def move_left(self):
        self.rect.x -= PLAYER_SPEED
        
    def move_right(self):
        self.rect.x += PLAYER_SPEED
        
    def take_damage(self):
        if not self.invincible:
            self.health -= 1
            self.invincible = True
            self.invincible_timer = 60  # 1 second invincibility
            self.image.fill(PURPLE)  # Flash purple when hit
            hurt_sound.play()
            return True
        return False
        
    def unlock_double_jump(self):
        self.max_jumps = 2
        powerup_sound.play()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, is_moving=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_moving = is_moving
        self.move_direction = 1
        self.move_speed = 2 if is_moving else 0
        self.original_x = x
        
    def update(self):
        if self.is_moving:
            self.rect.x += self.move_speed * self.move_direction
            # Reverse direction if platform hits boundaries
            if self.rect.right > WIDTH or self.rect.left < 0:
                self.move_direction *= -1

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="ground"):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(GREEN if enemy_type == "ground" else BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.enemy_type = enemy_type
        self.move_direction = 1
        self.move_speed = 2
        
    def update(self):
        if self.enemy_type == "ground":
            self.rect.x += self.move_speed * self.move_direction
            # Reverse direction if enemy hits boundaries
            if self.rect.right > WIDTH or self.rect.left < 0:
                self.move_direction *= -1
        elif self.enemy_type == "flying":
            # Sine wave movement pattern
            self.rect.x += self.move_speed
            self.rect.y += 2 * pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() / 200).y
            # Wrap around screen
            if self.rect.left > WIDTH:
                self.rect.right = 0

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type="health"):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(PURPLE if power_type == "health" else YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.power_type = power_type

def create_level(level_num):
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    # Create player - position changes based on level
    player = Player()
    all_sprites.add(player)
    
    # Create ground platform (common to all levels)
    ground = Platform(0, HEIGHT - 40, WIDTH, 40)
    platforms.add(ground)
    all_sprites.add(ground)
    
    # Define different platforms for each level
    level_designs = {
        1: [  # Level 1 (beginner level)
            (100, 400, 200, 20, False),
            (400, 300, 200, 20, False),
            (200, 200, 200, 20, False),
            (500, 500, 200, 20, False)
        ],
        2: [  # Level 2 (introduce moving platforms)
            (50, 450, 150, 20, False),
            (250, 350, 150, 20, True),  # Moving platform
            (450, 250, 150, 20, False),
            (300, 150, 150, 20, False),
            (600, 400, 150, 20, True)   # Moving platform
        ],
        3: [  # Level 3 (more challenging)
            (100, 500, 100, 20, False),
            (250, 400, 100, 20, True),
            (400, 300, 100, 20, True),
            (550, 200, 100, 20, False),
            (700, 100, 100, 20, False),
            (100, 200, 100, 20, True)
        ],
        4: [  # Level 4 (difficult with enemies)
            (50, 550, 100, 20, False),
            (200, 450, 100, 20, True),
            (350, 350, 100, 20, True),
            (500, 250, 100, 20, False),
            (650, 150, 100, 20, True),
            (150, 200, 100, 20, True)
        ],
        5: [  # Level 5 (expert level)
            (50, 550, 80, 20, True),
            (180, 450, 80, 20, True),
            (310, 350, 80, 20, True),
            (440, 250, 80, 20, True),
            (570, 150, 80, 20, True),
            (700, 300, 80, 20, True)
        ]
    }
    
    # Add platforms for the current level
    for x, y, w, h, moving in level_designs.get(level_num, level_designs[1]):
        platform = Platform(x, y, w, h, moving)
        platforms.add(platform)
        all_sprites.add(platform)
    
    # Add coins - number increases with level
    coin_count = 5 + level_num * 2  # More coins in higher levels
    for i in range(coin_count):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 100)
        coin = Coin(x, y)
        coins.add(coin)
        all_sprites.add(coin)
    
    # Add enemies starting from level 3
    if level_num >= 3:
        enemy_count = min(level_num - 2, 3)  # 1-3 enemies based on level
        for i in range(enemy_count):
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 150)
            enemy_type = "flying" if level_num >= 4 and random.random() > 0.7 else "ground"
            enemy = Enemy(x, y, enemy_type)
            enemies.add(enemy)
            all_sprites.add(enemy)
    
    # Add powerups starting from level 2
    if level_num >= 2 and random.random() > 0.5:  # 50% chance for powerup
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 150)
        power_type = "health" if random.random() > 0.5 else "double_jump"
        powerup = PowerUp(x, y, power_type)
        powerups.add(powerup)
        all_sprites.add(powerup)
    
    return player, all_sprites, platforms, coins, enemies, powerups

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

def draw_health_bar(surface, x, y, health):
    bar_width = 100
    bar_height = 20
    fill = (health / 3) * bar_width
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

def main_menu():
    while True:
        screen.fill(BACKGROUND_COLORS[0])
        draw_text("Solaxium", font, BLACK, screen, WIDTH // 2, HEIGHT // 4)
        
        mx, my = pygame.mouse.get_pos()
        
        button_1 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
        button_2 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
        button_3 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50)
        button_4 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 210, 200, 50)
        
        pygame.draw.rect(screen, GREEN, button_1)
        pygame.draw.rect(screen, BLUE, button_2)
        pygame.draw.rect(screen, YELLOW, button_3)
        pygame.draw.rect(screen, RED, button_4)
        
        draw_text("Start Game", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 25)
        draw_text("Level Select", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 95)
        draw_text("About", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 165)
        draw_text("Exit", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 235)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_1.collidepoint((mx, my)):
                    game_loop(start_level=1)
                if button_2.collidepoint((mx, my)):
                    level_select()
                if button_3.collidepoint((mx, my)):
                    about_screen()
                if button_4.collidepoint((mx, my)):
                    pygame.quit()
                    sys.exit()
        
        pygame.display.update()
        clock.tick(FPS)

def level_select():
    running = True
    while running:
        screen.fill(BACKGROUND_COLORS[0])
        draw_text("Select Level", font, BLACK, screen, WIDTH // 2, HEIGHT // 4)
        
        mx, my = pygame.mouse.get_pos()
        
        # Create buttons for each level
        buttons = []
        for i in range(1, MAX_LEVEL + 1):
            button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 3 + (i * 60), 200, 50)
            buttons.append((i, button))
            # Different colors for different levels
            color = (
                GREEN if i == 1 else 
                BLUE if i == 2 else 
                YELLOW if i == 3 else 
                ORANGE if i == 4 else 
                RED
            )
            pygame.draw.rect(screen, color, button)
            draw_text(f"Level {i}", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 3 + (i * 60) + 25)
        
        # Back button
        back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 3 + (MAX_LEVEL + 1) * 60, 200, 50)
        pygame.draw.rect(screen, RED, back_button)
        draw_text("Back", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 3 + (MAX_LEVEL + 1) * 60 + 25)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check level buttons
                for level, button in buttons:
                    if button.collidepoint((mx, my)):
                        game_loop(start_level=level)
                        running = False
                # Check back button
                if back_button.collidepoint((mx, my)):
                    running = False
        
        pygame.display.update()
        clock.tick(FPS)

def about_screen():
    running = True
    while running:
        screen.fill(BACKGROUND_COLORS[0])
        draw_text("About Solaxium", font, BLACK, screen, WIDTH // 2, HEIGHT // 4)
        
        draw_text("An Epic Platformer Adventure", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 - 60)
        draw_text("Created by: Jyomama28", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 - 20)
        draw_text("Controls: WASD to move", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 20)
        draw_text("SPACE to jump (double jump unlocked at level 3)", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 60)
        
        mx, my = pygame.mouse.get_pos()
        back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)
        pygame.draw.rect(screen, BLUE, back_button)
        draw_text("Back", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 145)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint((mx, my)):
                    running = False
        
        pygame.display.update()
        clock.tick(FPS)

def game_loop(start_level=1):
    current_level = start_level
    player_score = 0
    
    while current_level <= MAX_LEVEL:
        # Create the current level
        player, all_sprites, platforms, coins, enemies, powerups = create_level(current_level)
        player.score = player_score  # Carry over score
        
        # Unlock double jump at level 3
        if current_level >= 3:
            player.unlock_double_jump()
        
        level_running = True
        while level_running:
            clock.tick(FPS)
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                    if event.key == pygame.K_ESCAPE:
                        return  # Return to main menu
            
            # Movement controls
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                player.move_left()
            if keys[pygame.K_d]:
                player.move_right()
            
            # Update all sprites
            all_sprites.update()
            
            # Platform collisions
            if player.velocity_y > 0:
                hits = pygame.sprite.spritecollide(player, platforms, False)
                if hits:
                    player.on_ground = True
                    player.velocity_y = 0
                    player.rect.bottom = hits[0].rect.top
                    player.jumps_left = player.max_jumps
            
            # Coin collisions
            coin_hits = pygame.sprite.spritecollide(player, coins, True)
            for coin in coin_hits:
                player.score += 10
                coin_sound.play()
            
            # Enemy collisions
            enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
            for enemy in enemy_hits:
                # Only get hurt if landing on top of enemy
                if player.velocity_y > 0 and player.rect.bottom < enemy.rect.centery:
                    enemy.kill()  # Jump on enemy to defeat it
                    player.velocity_y = JUMP_STRENGTH * 0.7  # Bounce
                else:
                    if player.take_damage():
                        # Knockback when hit
                        player.velocity_y = JUMP_STRENGTH * 0.5
                        if player.rect.centerx < enemy.rect.centerx:
                            player.rect.x -= 30  # Knock left
                        else:
                            player.rect.x += 30  # Knock right
            
            # Powerup collisions
            powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
            for powerup in powerup_hits:
                if powerup.power_type == "health":
                    player.health = min(3, player.health + 1)
                elif powerup.power_type == "double_jump":
                    player.unlock_double_jump()
                powerup_sound.play()
            
            # Drawing
            screen.fill(BACKGROUND_COLORS[min(current_level-1, len(BACKGROUND_COLORS)-1)])
            all_sprites.draw(screen)
            
            # Draw UI
            draw_text(f"Score: {player.score}", small_font, WHITE, screen, WIDTH - 100, 20)
            draw_text(f"Level: {current_level}/{MAX_LEVEL}", small_font, WHITE, screen, WIDTH - 100, 50)
            draw_health_bar(screen, 20, 20, player.health)
            
            # Draw jump indicator
            if player.max_jumps > 1:
                jump_text = f"Jumps: {player.jumps_left}/{player.max_jumps}"
                draw_text(jump_text, small_font, WHITE, screen, 100, 50)
            
            pygame.display.flip()
            
            # Check for death
            if player.health <= 0:
                screen.fill(BACKGROUND_COLORS[min(current_level-1, len(BACKGROUND_COLORS)-1)])
                draw_text("Game Over!", font, RED, screen, WIDTH//2, HEIGHT//2 - 50)
                draw_text(f"Final Score: {player.score}", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 20)
                draw_text("Press any key to continue", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 80)
                pygame.display.flip()
                
                # Wait for key press
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                            waiting = False
                return
            
            # Check level completion (all coins collected)
            if len(coins) == 0:
                player_score = player.score  # Save score for next level
                current_level += 1
                level_running = False
                
                # Show level complete message (except after last level)
                if current_level <= MAX_LEVEL:
                    screen.fill(BACKGROUND_COLORS[min(current_level-2, len(BACKGROUND_COLORS)-1)])
                    draw_text(f"Level {current_level-1} Complete!", font, GREEN, screen, WIDTH//2, HEIGHT//2 - 50)
                    draw_text(f"Score: {player_score}", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 20)
                    draw_text("Preparing next level...", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 80)
                    pygame.display.flip()
                    pygame.time.wait(2000)
        
    # Game completed
    if current_level > MAX_LEVEL:
        screen.fill(BACKGROUND_COLORS[-1])
        draw_text("Congratulations!", font, GREEN, screen, WIDTH//2, HEIGHT//2 - 80)
        draw_text("You've Completed Solaxium!", font, YELLOW, screen, WIDTH//2, HEIGHT//2 - 30)
        draw_text(f"Final Score: {player_score}", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 30)
        draw_text("Press any key to continue", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 90)
        pygame.display.flip()
        
        # Wait for key press
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

# Start the game
if __name__ == "__main__":
    main_menu()