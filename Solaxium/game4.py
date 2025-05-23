import pygame
import sys
import random
from pygame import mixer
import pygame
import sys
import random
import math               # <-- ADD THIS
from pygame import mixer

#... [rest of your imports and setup] ...

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vector):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=(x, y))
        # Normalize direction and multiply by speed
        direction_vector = pygame.math.Vector2(direction_vector)
        if direction_vector.length() != 0:
            direction_vector = direction_vector.normalize()
        else:
            direction_vector = pygame.math.Vector2(1, 0)
        self.velocity = direction_vector * BULLET_SPEED

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        if (
            self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT
        ):
            self.kill()

class Gun(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.original_image = pygame.Surface((40, 10), pygame.SRCALPHA)
        pygame.draw.rect(self.original_image, BLACK, (0, 0, 40, 10))
        pygame.draw.circle(self.original_image, ORANGE, (35, 5), 5)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=self.player.rect.center)
        self.angle = 0

    def update(self):
        mx, my = pygame.mouse.get_pos()
        gun_center = self.player.rect.center
        dx = mx - gun_center[0]
        dy = my - gun_center[1]
        self.angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=gun_center)

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
        self.jumps_left = 1
        self.max_jumps = 1
        self.invincible = False
        self.invincible_timer = 0
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0
        self.facing_right = True

        self.gun = Gun(self)  # <-- ADD GUN

    def update(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.image.fill(RED)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True
            self.velocity_y = 0
            self.jumps_left = self.max_jumps

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.facing_right = True
        elif keys[pygame.K_a]:
            self.facing_right = False

        self.gun.update()  # <-- UPDATE GUN

    # ... rest of your Player methods ...

    def shoot(self, all_sprites):
        if self.shoot_cooldown == 0:
            # Shoot towards the mouse position
            mx, my = pygame.mouse.get_pos()
            bullet_start = self.gun.rect.center
            direction = (mx - bullet_start[0], my - bullet_start[1])
            bullet = Bullet(bullet_start[0], bullet_start[1], direction)
            self.bullets.add(bullet)
            all_sprites.add(bullet)
            self.shoot_cooldown = BULLET_COOLDOWN
            shoot_sound.play()

# ... rest of your code ...

def create_level(level_num):
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)
    all_sprites.add(player.gun)   

    return player, all_sprites, platforms, coins, enemies, powerups


pygame.init()
mixer.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5
MAX_LEVEL = 5
BULLET_SPEED = 10
BULLET_COOLDOWN = 15

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
    (135, 206, 235),
    (100, 149, 237),
    (70, 130, 180),
    (65, 105, 225),
    (25, 25, 112)
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solaxium Platformer")
clock = pygame.time.Clock()

font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)

try:
    jump_sound = mixer.Sound('jump.wav')
    coin_sound = mixer.Sound('coin.wav')
    hurt_sound = mixer.Sound('hurt.wav')
    powerup_sound = mixer.Sound('powerup.wav')
    shoot_sound = mixer.Sound('shoot.wav')
except:
    class DummySound:
        def play(self): pass
    jump_sound = coin_sound = hurt_sound = powerup_sound = shoot_sound = DummySound()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = BULLET_SPEED
        
    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

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
        self.jumps_left = 1
        self.max_jumps = 1
        self.invincible = False
        self.invincible_timer = 0
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0
        self.facing_right = True
        
    def update(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.image.fill(RED)
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True
            self.velocity_y = 0
            self.jumps_left = self.max_jumps
            
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.facing_right = True
        elif keys[pygame.K_a]:
            self.facing_right = False
            
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
            self.invincible_timer = 60
            self.image.fill(PURPLE)
            hurt_sound.play()
            return True
        return False
        
    def unlock_double_jump(self):
        self.max_jumps = 2
        powerup_sound.play()
        
    def shoot(self):
        if self.shoot_cooldown == 0:
            direction = 1 if self.facing_right else -1
            bullet_x = self.rect.right if self.facing_right else self.rect.left
            bullet = Bullet(bullet_x, self.rect.centery, direction)
            self.bullets.add(bullet)
            all_sprites.add(bullet)
            self.shoot_cooldown = BULLET_COOLDOWN
            shoot_sound.play()

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
            if self.rect.right > WIDTH or self.rect.left < 0:
                self.move_direction *= -1
        elif self.enemy_type == "flying":
            self.rect.x += self.move_speed
            self.rect.y += 2 * pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() / 200).y
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
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    player = Player()
    all_sprites.add(player)
    
    ground = Platform(0, HEIGHT - 40, WIDTH, 40)
    platforms.add(ground)
    all_sprites.add(ground)
    
    level_designs = {
        1: [
            (100, 400, 200, 20, False),
            (400, 300, 200, 20, False),
            (200, 200, 200, 20, False),
            (500, 500, 200, 20, False)
        ],
        2: [
            (50, 450, 150, 20, False),
            (250, 350, 150, 20, True),
            (450, 250, 150, 20, False),
            (300, 150, 150, 20, False),
            (600, 400, 150, 20, True)
        ],
        3: [
            (100, 500, 100, 20, False),
            (250, 400, 100, 20, True),
            (400, 300, 100, 20, True),
            (550, 200, 100, 20, False),
            (700, 100, 100, 20, False),
            (100, 200, 100, 20, True)
        ],
        4: [
            (50, 550, 100, 20, False),
            (200, 450, 100, 20, True),
            (350, 350, 100, 20, True),
            (500, 250, 100, 20, False),
            (650, 150, 100, 20, True),
            (150, 200, 100, 20, True)
        ],
        5: [
            (50, 550, 80, 20, True),
            (180, 450, 80, 20, True),
            (310, 350, 80, 20, True),
            (440, 250, 80, 20, True),
            (570, 150, 80, 20, True),
            (700, 300, 80, 20, True)
        ]
    }
    
    for x, y, w, h, moving in level_designs.get(level_num, level_designs[1]):
        platform = Platform(x, y, w, h, moving)
        platforms.add(platform)
        all_sprites.add(platform)
    
    coin_count = 5 + level_num * 2
    for i in range(coin_count):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 100)
        coin = Coin(x, y)
        coins.add(coin)
        all_sprites.add(coin)
    
    if level_num >= 3:
        enemy_count = min(level_num - 2, 3)
        for i in range(enemy_count):
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 150)
            enemy_type = "flying" if level_num >= 4 and random.random() > 0.7 else "ground"
            enemy = Enemy(x, y, enemy_type)
            enemies.add(enemy)
            all_sprites.add(enemy)
    
    if level_num >= 2 and random.random() > 0.5:
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
        
        buttons = []
        for i in range(1, MAX_LEVEL + 1):
            button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 3 + (i * 60), 200, 50)
            buttons.append((i, button))
            color = (
                GREEN if i == 1 else 
                BLUE if i == 2 else 
                YELLOW if i == 3 else 
                ORANGE if i == 4 else 
                RED
            )
            pygame.draw.rect(screen, color, button)
            draw_text(f"Level {i}", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 3 + (i * 60) + 25)
        
        back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 3 + (MAX_LEVEL + 1) * 60, 200, 50)
        pygame.draw.rect(screen, RED, back_button)
        draw_text("Back", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 3 + (MAX_LEVEL + 1) * 60 + 25)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for level, button in buttons:
                    if button.collidepoint((mx, my)):
                        game_loop(start_level=level)
                        running = False
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
        draw_text("SPACE to jump, F to shoot", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 60)
        
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
        player, all_sprites, platforms, coins, enemies, powerups = create_level(current_level)
        player.score = player_score
        
        if current_level >= 3:
            player.unlock_double_jump()
        
        level_running = True
        while level_running:
            clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_f:
                        player.shoot()
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                player.move_left()
            if keys[pygame.K_d]:
                player.move_right()
            
            all_sprites.update()
            
            if player.velocity_y > 0:
                hits = pygame.sprite.spritecollide(player, platforms, False)
                if hits:
                    player.on_ground = True
                    player.velocity_y = 0
                    player.rect.bottom = hits[0].rect.top
                    player.jumps_left = player.max_jumps
            
            coin_hits = pygame.sprite.spritecollide(player, coins, True)
            for coin in coin_hits:
                player.score += 10
                coin_sound.play()
            
            enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
            for enemy in enemy_hits:
                if player.velocity_y > 0 and player.rect.bottom < enemy.rect.centery:
                    enemy.kill()
                    player.velocity_y = JUMP_STRENGTH * 0.7
                else:
                    if player.take_damage():
                        player.velocity_y = JUMP_STRENGTH * 0.5
                        if player.rect.centerx < enemy.rect.centerx:
                            player.rect.x -= 30
                        else:
                            player.rect.x += 30
            
            for bullet in player.bullets:
                enemy_hits = pygame.sprite.spritecollide(bullet, enemies, True)
                for enemy in enemy_hits:
                    bullet.kill()
                    player.score += 20
            
            powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
            for powerup in powerup_hits:
                if powerup.power_type == "health":
                    player.health = min(3, player.health + 1)
                elif powerup.power_type == "double_jump":
                    player.unlock_double_jump()
                powerup_sound.play()
            
            screen.fill(BACKGROUND_COLORS[min(current_level-1, len(BACKGROUND_COLORS)-1)])
            all_sprites.draw(screen)
            
            draw_text(f"Score: {player.score}", small_font, WHITE, screen, WIDTH - 100, 20)
            draw_text(f"Level: {current_level}/{MAX_LEVEL}", small_font, WHITE, screen, WIDTH - 100, 50)
            draw_health_bar(screen, 20, 20, player.health)
            
            if player.max_jumps > 1:
                jump_text = f"Jumps: {player.jumps_left}/{player.max_jumps}"
                draw_text(jump_text, small_font, WHITE, screen, 100, 50)
            
            pygame.display.flip()
            
            if player.health <= 0:
                screen.fill(BACKGROUND_COLORS[min(current_level-1, len(BACKGROUND_COLORS)-1)])
                draw_text("Game Over!", font, RED, screen, WIDTH//2, HEIGHT//2 - 50)
                draw_text(f"Final Score: {player.score}", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 20)
                draw_text("Press any key to continue", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 80)
                pygame.display.flip()
                
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                            waiting = False
                return
            
            if len(coins) == 0:
                player_score = player.score
                current_level += 1
                level_running = False
                
                if current_level <= MAX_LEVEL:
                    screen.fill(BACKGROUND_COLORS[min(current_level-2, len(BACKGROUND_COLORS)-1)])
                    draw_text(f"Level {current_level-1} Complete!", font, GREEN, screen, WIDTH//2, HEIGHT//2 - 50)
                    draw_text(f"Score: {player_score}", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 20)
                    draw_text("Preparing next level...", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 80)
                    pygame.display.flip()
                    pygame.time.wait(2000)
        
    if current_level > MAX_LEVEL:
        screen.fill(BACKGROUND_COLORS[-1])
        draw_text("Congratulations!", font, GREEN, screen, WIDTH//2, HEIGHT//2 - 80)
        draw_text("You've Completed Solaxium!", font, YELLOW, screen, WIDTH//2, HEIGHT//2 - 30)
        draw_text(f"Final Score: {player_score}", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 30)
        draw_text("Press any key to continue", small_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 90)
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

if __name__ == "__main__":
    main_menu()