import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PLATFORM_COLOR = (100, 100, 100)
BACKGROUND_COLOR = (135, 206, 235)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Platformer")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)

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
        
    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True
            self.velocity_y = 0
            
    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False
            
    def move_left(self):
        self.rect.x -= PLAYER_SPEED
        
    def move_right(self):
        self.rect.x += PLAYER_SPEED

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

def create_game():
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    
    # Create player
    player = Player()
    all_sprites.add(player)
    
    # Create platforms
    ground = Platform(0, HEIGHT - 40, WIDTH, 40)
    platforms.add(ground)
    all_sprites.add(ground)
    
    # Add some floating platforms
    platform_positions = [
        (100, 400, 200, 20),
        (400, 300, 200, 20),
        (200, 200, 200, 20),
        (500, 500, 200, 20)
    ]
    
    for x, y, w, h in platform_positions:
        platform = Platform(x, y, w, h)
        platforms.add(platform)
        all_sprites.add(platform)
    
    # Add coins
    for i in range(10):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 100)
        coin = Coin(x, y)
        coins.add(coin)
        all_sprites.add(coin)
    
    return player, all_sprites, platforms, coins

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

def main_menu():
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Solaxium", font, BLACK, screen, WIDTH // 2, HEIGHT // 4)
        
        mx, my = pygame.mouse.get_pos()
        
        button_1 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
        button_2 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
        button_3 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50)
        
        pygame.draw.rect(screen, GREEN, button_1)
        pygame.draw.rect(screen, BLUE, button_2)
        pygame.draw.rect(screen, RED, button_3)
        
        draw_text("Start", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 25)
        draw_text("About", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 95)
        draw_text("Exit", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 165)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_1.collidepoint((mx, my)):
                    game_loop()
                if button_2.collidepoint((mx, my)):
                    about_screen()
                if button_3.collidepoint((mx, my)):
                    pygame.quit()
                    sys.exit()
        
        pygame.display.update()
        clock.tick(FPS)

def about_screen():
    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_text("About", font, BLACK, screen, WIDTH // 2, HEIGHT // 4)
        
        draw_text("Python Platformer Game", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 - 40)
        draw_text("Created by: Jyomama28", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2)
        draw_text("Controls: WASD to move, SPACE to jump", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 40)
        
        mx, my = pygame.mouse.get_pos()
        back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
        pygame.draw.rect(screen, BLUE, back_button)
        draw_text("Back", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 125)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint((mx, my)):
                    running = False
        
        pygame.display.update()
        clock.tick(FPS)

def game_loop():
    player, all_sprites, platforms, coins = create_game()
    running = True
    
    while running:
        # Keep loop running at the right speed
        clock.tick(FPS)
        
        # Process input (events)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Get pressed keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.move_left()
        if keys[pygame.K_d]:
            player.move_right()
        
        # Update
        all_sprites.update()
        
        # Check if player hits a platform when falling
        if player.velocity_y > 0:
            hits = pygame.sprite.spritecollide(player, platforms, False)
            if hits:
                player.on_ground = True
                player.velocity_y = 0
                player.rect.bottom = hits[0].rect.top
        
        # Check for coin collisions
        coin_hits = pygame.sprite.spritecollide(player, coins, True)
        for coin in coin_hits:
            player.score += 10
        
        # Render
        screen.fill(BACKGROUND_COLOR)
        all_sprites.draw(screen)
        
        # Draw score
        draw_text(f"Score: {player.score}", small_font, BLACK, screen, WIDTH - 100, 20)
        
        pygame.display.flip()
        
        # Check if all coins are collected
        if len(coins) == 0:
            draw_text("You Win!", font, GREEN, screen, WIDTH // 2, HEIGHT // 2)
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False

# Start the game
if __name__ == "__main__":
    main_menu()