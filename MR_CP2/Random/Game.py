import pygame, sys, random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Polished Platformer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# ---------------- COLORS ---------------- #
WHITE, BLACK, BLUE, GREEN, RED, PURPLE, YELLOW = (255,255,255),(0,0,0),(50,150,255),(50,200,50),(200,50,50),(200,50,200),(255,220,50)

# ---------------- CAMERA ---------------- #
class Camera:
    def __init__(self):
        self.x, self.y = 0,0
        self.shake_timer = 0
        self.shake_magnitude = 0
        self.zoom = 1

    def follow(self, target):
        target_x = target.rect.centerx - WIDTH // 2
        target_y = target.rect.centery - HEIGHT // 2
        self.x += (target_x - self.x) * 0.1
        self.y += (target_y - self.y) * 0.1

        if self.shake_timer > 0:
            self.shake_timer -= 1
            self.x += random.randint(-self.shake_magnitude, self.shake_magnitude)
            self.y += random.randint(-self.shake_magnitude, self.shake_magnitude)

    def apply(self, rect):
        return rect.move(-self.x, -self.y)

camera = Camera()

# ---------------- PARTICLES ---------------- #
class Particle:
    def __init__(self, x, y):
        self.pos = [x,y]
        self.vel = [random.uniform(-3,3), random.uniform(-3,3)]
        self.lifetime = random.randint(10,20)
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.lifetime -= 1
    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.pos[0]-camera.x), int(self.pos[1]-camera.y)), 3)

# ---------------- PLAYER ---------------- #
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x,y,40,60)
        self.vel_y = 0
        self.speed = 5
        self.gravity = 0.5
        self.jump_strength = -10
        self.jump_count = 0
        self.max_jumps = 2
        self.health = 5
        self.invincible = 0
        self.facing = 1
        self.weapon = "pistol"
    
    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing = -1
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing = 1

    def jump(self):
        if self.jump_count < self.max_jumps:
            self.vel_y = self.jump_strength
            self.jump_count += 1

    def update(self, platforms):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0 and self.rect.bottom <= p.rect.top + 15:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.jump_count = 0
                elif self.vel_y < 0 and self.rect.top >= p.rect.bottom - 15:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0
        
        if self.invincible > 0:
            self.invincible -= 1

    def draw(self):
        color = BLUE if self.invincible % 10 < 5 else (0,100,255)
        pygame.draw.rect(screen,color,camera.apply(self.rect))

# ---------------- PLATFORM ---------------- #
class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x,y,w,h)
    def draw(self):
        pygame.draw.rect(screen,GREEN,camera.apply(self.rect))

# ---------------- BULLET ---------------- #
class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x,y,10,5)
        self.direction = direction
        self.speed = 10
    def update(self):
        self.rect.x += int(self.speed*self.direction)
    def draw(self):
        pygame.draw.rect(screen,BLACK,camera.apply(self.rect))

# ---------------- ENEMY ---------------- #
class Enemy:
    def __init__(self, x, y, platform):
        self.rect = pygame.Rect(x,y-40,40,40)
        self.platform = platform
        self.speed = random.choice([-2,2])
        self.alive = True
    
    def update(self, player):
        if not self.alive: return
        if abs(player.rect.x - self.rect.x) < 200:
            self.speed = -2 if player.rect.x < self.rect.x else 2
        self.rect.x += self.speed
        if self.rect.left <= self.platform.rect.left or self.rect.right >= self.platform.rect.right:
            self.speed *= -1

    def draw(self):
        if self.alive:
            pygame.draw.rect(screen,PURPLE,camera.apply(self.rect))

# ---------------- BOSS ---------------- #
class Boss:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,120,80)
        self.health = 20
        self.timer = 0
        self.attack_phase = 0
        self.projectiles = []
    
    def update(self):
        self.timer +=1
        if self.timer%120==0:
            self.attack_phase=(self.attack_phase+1)%2
        if self.attack_phase==0 and self.timer%20==0:
            self.projectiles.append(pygame.Rect(self.rect.centerx,self.rect.bottom,10,20))
        if self.attack_phase==1 and self.timer%40==0:
            for i in range(-2,3):
                self.projectiles.append(pygame.Rect(self.rect.centerx,self.rect.centery+i*10,15,5))
        for p in self.projectiles:
            if self.attack_phase==0: p.y+=5
            else: p.x-=6
    
    def draw(self):
        pygame.draw.rect(screen,RED,camera.apply(self.rect))
        for p in self.projectiles:
            pygame.draw.rect(screen,(255,100,0),camera.apply(p))

# ---------------- LEVEL SETUP ---------------- #
platforms = [
    Platform(0,550,2000,50),
    Platform(300,450,200,20),
    Platform(600,350,200,20),
    Platform(900,300,200,20),
    Platform(1200,250,200,20),
    Platform(1500,200,200,20)
]

player = Player(100,400)
enemies = [Enemy(350,450,platforms[1]), Enemy(650,350,platforms[2])]
boss = Boss(1600,150)
goal = pygame.Rect(1800,150,40,40)
bullets = []
particles = []
score = 0

# ---------------- GAME LOOP ---------------- #
while True:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_SPACE: player.jump()
            if event.key==pygame.K_f:
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, player.facing))
            if event.key==pygame.K_1: player.weapon="pistol"
            if event.key==pygame.K_2: player.weapon="shotgun"
            if event.key==pygame.K_3: player.weapon="laser"

    # Update
    player.handle_input(keys)
    player.update(platforms)
    for enemy in enemies: enemy.update(player)
    boss.update()
    for b in bullets: b.update()
    for p in particles: p.update()
    
    # Collision & Gameplay
    for enemy in enemies:
        if enemy.alive and player.rect.colliderect(enemy.rect):
            if player.vel_y>0:
                enemy.alive=False
                player.vel_y=-8
                camera.shake_timer=10
                camera.shake_magnitude=5
                for _ in range(15): particles.append(Particle(enemy.rect.centerx,enemy.rect.centery))
                score+=100
            elif player.invincible<=0:
                player.health-=1
                player.invincible=60

    for b in bullets[:]:
        for enemy in enemies:
            if enemy.alive and b.rect.colliderect(enemy.rect):
                enemy.alive=False
                bullets.remove(b)
                for _ in range(15): particles.append(Particle(enemy.rect.centerx,enemy.rect.centery))
                score+=100
        if b.rect.colliderect(boss.rect):
            boss.health-=1
            bullets.remove(b)
            for _ in range(20): particles.append(Particle(boss.rect.centerx,boss.rect.centery))

    # Boss projectiles
    for p in boss.projectiles:
        if player.rect.colliderect(p) and player.invincible<=0:
            player.health-=1
            player.invincible=60

    # Camera follow
    camera.follow(player)

    # Draw
    for plat in platforms: plat.draw()
    for enemy in enemies: enemy.draw()
    for b in bullets: b.draw()
    for p in particles: p.draw()
    boss.draw()
    player.draw()
    pygame.draw.rect(screen,RED,camera.apply(goal))

    # UI
    screen.blit(font.render(f"Health: {player.health}",True,BLACK),(10,10))
    screen.blit(font.render(f"Score: {score}",True,BLACK),(10,40))
    screen.blit(font.render(f"Weapon: {player.weapon}",True,BLACK),(10,70))
    screen.blit(font.render(f"Boss HP: {boss.health}",True,BLACK),(WIDTH-150,10))

    # Win/Lose
    if player.rect.colliderect(goal):
        score+=500
        player.rect.x,player.rect.y=100,400
        enemies = [Enemy(350,450,platforms[1]), Enemy(650,350,platforms[2])]
        boss = Boss(1600,150)
    if player.health<=0:
        player.health=5
        score=0
        player.rect.x,player.rect.y=100,400
        enemies = [Enemy(350,450,platforms[1]), Enemy(650,350,platforms[2])]
        boss = Boss(1600,150)
    
    pygame.display.flip()
    clock.tick(60)