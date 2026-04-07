import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = 15
MAX_FALL_SPEED = 15
PLAYER_SPEED = 5
DASH_BOOST = 18
DASH_DURATION = 12   # frames (~0.2s)
DASH_COOLDOWN = 90   # frames (~1.5s)

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GRAY = (100, 100, 100)
RED = (180, 20, 20)

# Particle for dash VFX
class Particle:
    def __init__(self, x, y):
        self.x = x + random.uniform(-8, 8)
        self.y = y + random.uniform(-15, 15)
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-3, 2)
        self.life = random.randint(12, 28)
        self.color = (255, random.randint(180, 255), 0)  # bright orange/yellow trail

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15  # slight "float up" then fall
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            size = max(2, int(self.life / 6))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.start_x = 120
        self.start_y = HEIGHT - 120
        self.rect.center = (self.start_x, self.start_y)
        self.velocity_y = 0
        self.on_ground = False
        self.jumps_remaining = 2
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_velocity = 0

    def reset_position(self):
        self.rect.center = (self.start_x, self.start_y)
        self.velocity_y = 0
        self.on_ground = False
        self.jumps_remaining = 2
        self.dash_timer = 0
        self.dash_velocity = 0

    def update(self, dx, platforms, enemies):
        # Cooldown & dash timer
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
            # Spawn dash particles (trail behind)
            if random.random() < 0.75:
                dash_dir = 1 if self.dash_velocity > 0 else -1
                px = self.rect.centerx - (dash_dir * 25)
                py = self.rect.centery
                particles.append(Particle(px, py))

        # Horizontal movement (input + dash boost)
        effective_dx = dx
        if self.dash_timer > 0:
            effective_dx += self.dash_velocity

        self.rect.x += effective_dx

        # Horizontal collisions
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for hit in hits:
            if effective_dx > 0:
                self.rect.right = hit.rect.left
            elif effective_dx < 0:
                self.rect.left = hit.rect.right

        # Vertical movement
        self.velocity_y += GRAVITY
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED
        self.rect.y += self.velocity_y

        # Reset on_ground
        self.on_ground = False

        # Vertical collisions
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for hit in hits:
            if self.velocity_y >= 0:  # Falling / landing
                if hit.hazard:
                    self.reset_position()
                    return
                self.rect.bottom = hit.rect.top
                self.velocity_y = 0
                self.on_ground = True
                self.jumps_remaining = 2

                # Trigger disappearing platforms
                if hit.disappearing and hit.disappear_timer is None:
                    hit.disappear_timer = 50  # ~0.83s grace period
            elif self.velocity_y < 0:  # Ceiling hit
                self.rect.top = hit.rect.bottom
                self.velocity_y = 0

        # Fallback floor
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity_y = 0
            self.on_ground = True
            self.jumps_remaining = 2

        # Enemy collisions (after movement)
        enemy_hits = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_hits:
            if self.velocity_y > 2 and self.rect.bottom - self.velocity_y <= enemy.rect.top + 12:
                # Stomp!
                enemy.kill()
                self.velocity_y = -JUMP_STRENGTH * 0.8
            else:
                # Hit from side/bottom
                self.reset_position()
                break

    def jump(self):
        if self.jumps_remaining > 0:
            self.velocity_y = -JUMP_STRENGTH
            self.jumps_remaining -= 1
            self.on_ground = False

    def dash(self):
        if self.dash_cooldown <= 0:
            self.dash_timer = DASH_DURATION
            self.dash_cooldown = DASH_COOLDOWN
            # Determine direction from current input or default right
            keys = pygame.key.get_pressed()
            dir_x = 1
            if keys[pygame.K_LEFT]:
                dir_x = -1
            elif keys[pygame.K_RIGHT]:
                dir_x = 1
            self.dash_velocity = dir_x * DASH_BOOST


# Platform class (now supports moving, disappearing, hazard/spikes)
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, moving=False, vel_x=0, disappearing=False, hazard=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        if hazard:
            self.image.fill(RED)
        elif moving:
            self.image.fill((70, 70, 180))
        else:
            self.image.fill(GRAY)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.moving = moving
        self.vel_x = vel_x
        self.disappearing = disappearing
        self.hazard = hazard
        self.disappear_timer = None

    def update(self):
        if self.moving and self.vel_x != 0:
            self.rect.x += self.vel_x
            if self.rect.left < 0:
                self.rect.left = 0
                self.vel_x = abs(self.vel_x)
            elif self.rect.right > WIDTH:
                self.rect.right = WIDTH
                self.vel_x = -abs(self.vel_x)

        if self.disappearing and self.disappear_timer is not None:
            self.disappear_timer -= 1
            if self.disappear_timer <= 0:
                self.kill()


# Enemy class (simple horizontal patrol)
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((200, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = random.choice([-3, 3])

    def update(self):
        self.rect.x += self.vel_x
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.vel_x *= -1


# Exit / Goal
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill((0, 220, 0))
        pygame.draw.rect(self.image, (255, 255, 100), (10, 15, 20, 30))  # simple door highlight
        self.rect = self.image.get_rect(topleft=(x, y))


# === LEVEL GENERATION ===
def regenerate_level():
    # Clear old dynamic objects (keep player)
    for sprite in list(all_sprites):
        if sprite != player:
            all_sprites.remove(sprite)
    platforms.empty()
    enemies.empty()
    exit_group.empty()
    particles.clear()

    # Ground
    ground = Platform(0, HEIGHT - 40, WIDTH, 40, moving=False, vel_x=0, disappearing=False, hazard=False)
    platforms.add(ground)
    all_sprites.add(ground)

    # Layered random platforms for playable vertical progression
    y = HEIGHT - 120
    for i in range(8):
        x = random.randint(40, WIDTH - 160)
        w = random.randint(90, 230)
        moving = random.random() < 0.35
        disappearing = random.random() < 0.25
        hazard = random.random() < 0.28
        vel_x = random.choice([-2.8, 2.8]) if moving else 0

        plat = Platform(x, y, w, 20, moving, vel_x, disappearing, hazard)
        platforms.add(plat)
        all_sprites.add(plat)

        # Occasionally add an extra off-layer platform for variety
        if random.random() < 0.4:
            extra_x = random.randint(40, WIDTH - 160)
            extra_y = y + random.randint(-50, 40)
            extra_plat = Platform(extra_x, extra_y, random.randint(80, 180), 20,
                                  random.random() < 0.3, random.choice([-2.5, 2.5]) if random.random() < 0.3 else 0,
                                  random.random() < 0.2, random.random() < 0.25)
            platforms.add(extra_plat)
            all_sprites.add(extra_plat)

        y -= random.randint(70, 130)
        if y < 80:
            break

    # Enemies (placed on random platforms)
    for _ in range(4):
        if platforms.sprites():
            plat = random.choice(platforms.sprites())
            ex = plat.rect.x + random.randint(10, max(10, plat.rect.width - 50))
            ey = plat.rect.top - 55
            enemy = Enemy(ex, ey)
            enemies.add(enemy)
            all_sprites.add(enemy)

    # Exit placed on a higher platform
    high_plats = [p for p in platforms if p.rect.y < HEIGHT // 3]
    chosen = random.choice(high_plats) if high_plats else random.choice(platforms.sprites())
    exit_x = chosen.rect.x + random.randint(10, max(10, chosen.rect.width - 50))
    exit_y = chosen.rect.top - 75
    exit_obj = Exit(exit_x, exit_y)
    exit_group.add(exit_obj)
    all_sprites.add(exit_obj)

    # Reset player to starting position
    player.reset_position()


# Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Procedural Platformer - Double Jump + Dash + Enemies + Exit")
clock = pygame.time.Clock()

player = Player()

# Groups
all_sprites = pygame.sprite.Group(player)
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
particles = []

# Generate the first level
regenerate_level()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_x:
                player.dash()

    # Input
    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_LEFT]:
        dx -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        dx += PLAYER_SPEED

    # Updates
    platforms.update()          # moving + disappearing logic
    player.update(dx, platforms, enemies)
    enemies.update()

    # Particle cleanup
    for p in particles[:]:
        p.update()
        if p.life <= 0:
            particles.remove(p)

    # Check win condition
    if pygame.sprite.spritecollideany(player, exit_group):
        print("★★★ LEVEL COMPLETE! Generating new random level... ★★★")
        regenerate_level()

    # Draw
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Draw particles on top (VFX)
    for p in particles:
        p.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)