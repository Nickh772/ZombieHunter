import pygame
import random
import math
import time

# Blood Splatter Particle System
class BloodSplatter:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = random.uniform(1.5, 3)
        self.lifetime = 4
        self.timer = 0
        self.size = random.randint(3, 5)

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.timer += 0.05
        if self.timer >= self.lifetime:
            return True
        return False

    def draw(self, camera_x, camera_y):
        pygame.draw.rect(screen, RED, (int(self.x - camera_x), int(self.y - camera_y), self.size, self.size))

class Grenade:
    def __init__(self, x, y, timer=2):
        self.x = x
        self.y = y
        self.timer = timer
        self.image = pygame.image.load("grenade.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.exploded = False
        self.blast_radius = 100

    def update(self, zombies):
        if not self.exploded:
            self.timer -= 1 / 60
            if self.timer <= 0:
                self.explode(zombies)

    def explode(self, zombies):
        self.exploded = True
        for zombie in zombies[:]:
            if math.hypot(zombie.x - self.x, zombie.y - self.y) < self.blast_radius:
                zombies.remove(zombie)
                global score
                score += 10
                for _ in range(10):
                    angle = random.uniform(0, 2 * math.pi)
                    blood_splatter_particles.append(BloodSplatter(zombie.x, zombie.y, angle))

    def draw(self, camera_x, camera_y):
        screen.blit(self.image, (self.x - camera_x - self.rect.width // 2, self.y - camera_y - self.rect.height // 2))
        if not self.exploded:
            font = pygame.font.Font("pixelfont.ttf", 30)
            timer_text = font.render(f"{int(self.timer)}", True, (255, 0, 0))
            screen.blit(timer_text, (self.x - camera_x - timer_text.get_width() // 2, self.y - camera_y - self.rect.height // 2 - 20))

blood_splatter_particles = []

pygame.init()

# Screen and game constants
width, height = 800, 600
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Zombie Hunter")

# Colors and fonts
BLACK, GREEN, RED, WHITE, BLUE, DARK_GRAY = (0, 0, 0), (0, 255, 0), (255, 0, 0), (255, 255, 255), (0, 0, 255), (50, 50, 50)
font = pygame.font.Font("pixelfont.ttf", 24)

# Clock and game variables
clock = pygame.time.Clock()

# Power-up timers (dictionary to manage multiple power-ups)
active_powerup_timers = {
    "insta_kill": 0,
    "double_points": 0,
    "freeze": 0,
    "infinite_ammo": 0,
}

player_speed, player_x, player_y = 1.9, 400, 300
health, shield, score, round_num = 100, 0, 1000, 1
stamina, max_stamina = 100, 100
zombies, bullets, active_powerups = [], [], []
gun_type = "pistol"
ammo = {"pistol": 6, "assault_rifle": 30, "shotgun": 8}
current_ammo, reload_time, reloading, reload_start_time = 6, 1.5, False, 0
map_width, map_height = 3000, 1500
weapon_damage = {"pistol": 1, "assault_rifle": 2, "shotgun": 5}
fire_rate = {"pistol": 0.5, "assault_rifle": 0.1, "shotgun": 1}
last_shot_time = 0

# Power-up timers
insta_kill_active, double_points_active, freeze_active, infinite_ammo_active = False, False, False, False
insta_kill_end_time, double_points_end_time, freeze_end_time, infinite_ammo_end_time = 0, 0, 0, 0

# Images (scaled down)
background_image = pygame.image.load("ground.png")
background_image = pygame.transform.scale(background_image, (map_width * 2.3, map_height * 2.3))
player_stand_image = pygame.image.load("hitman1_gun.png")
player_reload_image = pygame.image.load("hitman1_reload.png")
player_ak_hold_image = pygame.image.load("hitman1_ak_hold.png")
player_ak_reload_image = pygame.image.load("hitman1_ak_reload.png")
player_shotgun_hold_image = pygame.image.load("hitman1_shotgun_hold.png")
player_shotgun_reload_image = pygame.image.load("hitman1_shotgun_reload.png")
player_image = player_stand_image
zombie_image = pygame.image.load("zombie.png")
zombie_image = pygame.transform.scale(zombie_image, (30, 30))
powerup_images = {
    "insta_kill": pygame.transform.scale(pygame.image.load("instant_kill.png"), (60, 45)),
    "double_points": pygame.transform.scale(pygame.image.load("2x.png"), (60, 45)),
    "freeze": pygame.transform.scale(pygame.image.load("freeze.png"), (60, 45)),
    "infinite_ammo": pygame.transform.scale(pygame.image.load("infinite_ammo.png"), (60, 45))
}
shield_image = pygame.image.load("shield.png")
shield_image = pygame.transform.scale(shield_image, (80, 80))
grenade_image = pygame.image.load("grenade.png")
grenade_image = pygame.transform.scale(grenade_image, (80, 80))

# Load sound effects for the pistol
gun_sounds = {
    "pistol": pygame.mixer.Sound("sounds/pistol.mp3"),
    "assault_rifle": pygame.mixer.Sound("sounds/assault_rifle.mp3"),
    "shotgun": pygame.mixer.Sound("sounds/shotgun.mp3"),
}

# Buy Menu
def draw_buy_menu():
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    items = [
        ("Shield", shield_image, 125),
        ("Grenade", grenade_image, 50),
        ("Insta Kill", powerup_images["insta_kill"], 200),
        ("Double Points", powerup_images["double_points"], 150),
        ("Freeze", powerup_images["freeze"], 100),
        ("Infinite Ammo", powerup_images["infinite_ammo"], 250),
        ("Assault Rifle", pygame.image.load("assault_rifle.png"), 500),
        ("Shotgun", pygame.image.load("shotgun.png"), 300),
        ("Pistol", pygame.image.load("revolver.png"), 0),
    ]

    mouse_x, mouse_y = pygame.mouse.get_pos()
    for idx, (name, image, price) in enumerate(items):
        x, y = 100 + (idx % 4) * 150, 100 + (idx // 4) * 150
        rect = pygame.Rect(x, y, 100, 100)
        if rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, WHITE, rect, 3)
            price_text = font.render(f"{name} ${price}", True, RED)
            screen.blit(price_text, (x + 10, y + 110))
        else:
            pygame.draw.rect(screen, BLACK, rect, border_radius=5)
        screen.blit(image, (x + 10, y + 10))

    if insufficient_funds:
        insufficient_funds_text = font.render("Insufficient Funds", True, RED if int(time.time() * 5) % 2 == 0 else WHITE)
        screen.blit(insufficient_funds_text, (width // 2 - insufficient_funds_text.get_width() // 2, height - 50))

def handle_buy_click(pos):
    global score, shield, grenade_ammo, gun_type, insufficient_funds, player_image, current_ammo
    items = [
        ("Shield", 125),
        ("Grenade", 50),
        ("Insta Kill", 200),
        ("Double Points", 150),
        ("Freeze", 100),
        ("Infinite Ammo", 250),
        ("Assault Rifle", 500),
        ("Shotgun", 300),
        ("Pistol", 0),
    ]

    for idx, (name, price) in enumerate(items):
        x, y = 100 + (idx % 4) * 150, 100 + (idx // 4) * 150
        if x < pos[0] < x + 100 and y < pos[1] < y + 100:
            if score >= price:
                if name == "Shield":
                    shield = min(100, shield + 50)
                elif name == "Grenade":
                    grenade_ammo += 1
                elif name == "Insta Kill":
                    active_powerup_timers["insta_kill"] = time.time() + 24
                elif name == "Double Points":
                    active_powerup_timers["double_points"] = time.time() + 24
                elif name == "Freeze":
                    active_powerup_timers["freeze"] = time.time() + 24
                elif name == "Infinite Ammo":
                    active_powerup_timers["infinite_ammo"] = time.time() + 24
                elif name == "Assault Rifle":
                    gun_type = "assault_rifle"
                    current_ammo = ammo[gun_type]
                    player_image = player_ak_hold_image
                elif name == "Shotgun":
                    gun_type = "shotgun"
                    current_ammo = ammo[gun_type]
                    player_image = player_shotgun_hold_image
                elif name == "Pistol":
                    gun_type = "pistol"
                    current_ammo = ammo[gun_type]
                    player_image = player_stand_image
                score -= price
                insufficient_funds = False
            else:
                insufficient_funds = True
            if price == 0:
                if name == "Pistol":
                    gun_type = "pistol"
                    current_ammo = ammo[gun_type]
                    player_image = player_stand_image
                insufficient_funds = False

insufficient_funds = False

class Zombie:
    def __init__(self, x, y, speed, health):
        self.x, self.y, self.speed, self.health, self.max_health = x, y, speed, health, health

    def move_towards_player(self, player_x, player_y):
        if freeze_active:
            return 0
        angle = math.atan2(player_y - self.y, player_x - self.x)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        return angle

    def draw(self, camera_x, camera_y, angle):
        scaled_x, scaled_y = self.x - camera_x, self.y - camera_y
        rotated_zombie = pygame.transform.rotate(zombie_image, -math.degrees(angle))
        zombie_rect = rotated_zombie.get_rect(center=(scaled_x, scaled_y))
        screen.blit(rotated_zombie, zombie_rect.topleft)
        self.draw_health_bar(camera_x, camera_y)
        if freeze_active:
            blue_overlay = pygame.Surface(rotated_zombie.get_size(), pygame.SRCALPHA)
            blue_overlay.fill((0, 0, 255, 100))
            screen.blit(blue_overlay, zombie_rect.topleft)

    def draw_health_bar(self, camera_x, camera_y):
        bar_width = 30
        bar_height = 5
        border_thickness = 2
        health_percentage = self.health / self.max_health
        health_bar_x = self.x - camera_x - bar_width // 2
        health_bar_y = self.y - camera_y - 20
        health_bar_width = int(bar_width * health_percentage)
        pygame.draw.rect(screen, (255, 255, 255), (health_bar_x - border_thickness, health_bar_y - border_thickness, bar_width + 2 * border_thickness, bar_height + 2 * border_thickness))
        pygame.draw.rect(screen, (50, 50, 50), (health_bar_x, health_bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, health_bar_width, bar_height))

class Bullet:
    def __init__(self, x, y, angle, explosive=False):
        self.x, self.y, self.angle, self.speed = x, y, angle, 10
        self.explosive = explosive
        self.exploded = False
        self.travel_distance = 0
        self.max_distance = 500

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.travel_distance += self.speed

    def draw(self, camera_x, camera_y):
        scaled_x, scaled_y = self.x - camera_x, self.y - camera_y
        pygame.draw.circle(screen, GREEN, (int(scaled_x), int(scaled_y)), 5)

    def explode(self, zombies):
        self.exploded = True
        explosion_radius = 50
        for zombie in zombies[:]:
            if math.hypot(zombie.x - self.x, zombie.y - self.y) < explosion_radius:
                zombie.health -= weapon_damage["rocket_launcher"]
                if zombie.health <= 0:
                    zombies.remove(zombie)
                    global score
                    score += 10

class PowerUp:
    def __init__(self, x, y, type):
        self.x, self.y, self.type = x, y, type

    def draw(self, camera_x, camera_y):
        scaled_x, scaled_y = self.x - camera_x, self.y - camera_y
        screen.blit(powerup_images[self.type], (scaled_x, scaled_y))

def spawn_powerup_at_zombie(zombie_x, zombie_y):
    if random.random() < 0.02:
        powerup_type = random.choice(["insta_kill", "double_points", "freeze", "infinite_ammo"])
        active_powerups.append(PowerUp(zombie_x, zombie_y, powerup_type))

def shoot_bullet(player_x, player_y, mouse_x, mouse_y):
    global current_ammo, reloading, last_shot_time
    current_time = time.time()
    if not reloading and (current_ammo > 0 or infinite_ammo_active) and current_time - last_shot_time >= fire_rate[gun_type]:
        angle = math.atan2(mouse_y - height // 2, mouse_x - width // 2)
        last_shot_time = current_time
        gun_sounds[gun_type].play()
        if gun_type == "shotgun":
            for spread in [-0.1, 0, 0.1]:
                bullets.append(Bullet(player_x, player_y, angle + spread))
        elif gun_type == "assault_rifle":
            bullets.append(Bullet(player_x, player_y, angle))
        else:
            bullets.append(Bullet(player_x, player_y, angle))
        if not infinite_ammo_active:
            current_ammo -= 1

def draw_flashlight(camera_x, camera_y):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 240))
    flashlight_radius = 200
    flashlight_x, flashlight_y = player_x - camera_x, player_y - camera_y
    pygame.draw.circle(overlay, (0, 0, 0, 0), (int(flashlight_x), int(flashlight_y)), flashlight_radius)
    screen.blit(overlay, (0, 0))

def spawn_zombies(round_num):
    base_zombies = 5 + min(round_num - 1, 5)
    additional_zombies = max(0, round_num - 5) * 3
    zombie_count = base_zombies + additional_zombies
    zombie_health = 3 + round_num // 2
    zombie_speed = 1 + round_num * 0.1
    return [
        Zombie(
            random.choice([random.randint(0, 100), random.randint(map_width - 100, map_width)]),
            random.choice([random.randint(0, 100), random.randint(map_height - 100, map_height)]),
            zombie_speed,
            zombie_health,
        )
        for _ in range(zombie_count)
    ]

def apply_powerups():
    global weapon_damage, double_points_active, freeze_active, infinite_ammo_active
    current_time = time.time()
    if active_powerup_timers["insta_kill"] > current_time:
        weapon_damage = {key: 999 for key in weapon_damage}
    else:
        weapon_damage = {"pistol": 1, "assault_rifle": 2, "shotgun": 5}
    double_points_active = active_powerup_timers["double_points"] > current_time
    freeze_active = active_powerup_timers["freeze"] > current_time
    infinite_ammo_active = active_powerup_timers["infinite_ammo"] > current_time

def draw_hud():
    health_bar_width = 200
    health_bar_height = 20
    border_thickness = 3
    health_ratio = health / 100
    pygame.draw.rect(screen, WHITE, (10 - border_thickness, 10 - border_thickness, health_bar_width + 2 * border_thickness, health_bar_height + 2 * border_thickness))
    pygame.draw.rect(screen, RED, (10, 10, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, GREEN, (10, 10, health_bar_width * health_ratio, health_bar_height))
    shield_bar_width = 200
    shield_bar_height = 20
    shield_ratio = shield / 100
    pygame.draw.rect(screen, WHITE, (10 - border_thickness, 40 - border_thickness, shield_bar_width + 2 * border_thickness, shield_bar_height + 2 * border_thickness))
    pygame.draw.rect(screen, (50, 50, 50), (10, 40, shield_bar_width, shield_bar_height))
    pygame.draw.rect(screen, BLUE, (10, 40, shield_bar_width * shield_ratio, shield_bar_height))
    stamina_bar_width = 200
    stamina_bar_height = 20
    stamina_ratio = stamina / max_stamina
    pygame.draw.rect(screen, WHITE, (10 - border_thickness, 70 - border_thickness, stamina_bar_width + 2 * border_thickness, stamina_bar_height + 2 * border_thickness))
    pygame.draw.rect(screen, (50, 50, 50), (10, 70, stamina_bar_width, stamina_bar_height))
    pygame.draw.rect(screen, GREEN, (10, 70, stamina_bar_width * stamina_ratio, stamina_bar_height))
    round_text = font.render(f"Wave: {round_num}", True, WHITE)
    screen.blit(round_text, (10, height - 40))
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (width - 150, height - 40))
    if insufficient_funds:
        insufficient_funds_text = font.render("Insufficient Funds", True, RED if int(time.time() * 5) % 2 == 0 else WHITE)
        screen.blit(insufficient_funds_text, (width // 2 - insufficient_funds_text.get_width() // 2, 10))
    gun_text = font.render(f"Gun: {gun_type.capitalize()}", True, WHITE)
    screen.blit(gun_text, (10, 100))
    ammo_text = font.render(f"Ammo: {'∞' if infinite_ammo_active else f'{current_ammo}/{ammo[gun_type]}'}", True, WHITE)
    screen.blit(ammo_text, (10, 130))
    if reloading:
        reload_text = font.render("Reloading...", True, RED)
        screen.blit(reload_text, (10, 190))
    current_time = time.time()
    powerup_icon_width = 80
    powerup_icon_height = 64
    powerup_y_pos = height - 100
    total_icons = len([p for p, t in active_powerup_timers.items() if t > current_time])
    total_width = total_icons * (powerup_icon_width + 10) - 10
    start_x = (width // 2) - (total_width // 2)
    for index, (powerup, end_time) in enumerate(active_powerup_timers.items()):
        if end_time > current_time:
            powerup_image = pygame.transform.scale(powerup_images[powerup], (powerup_icon_width, powerup_icon_height))
            x_pos = start_x + index * (powerup_icon_width + 10)
            screen.blit(powerup_image, (x_pos, powerup_y_pos))
            timer_text = font.render(f"{int(end_time - current_time)}s", True, WHITE)
            screen.blit(timer_text, (x_pos + (powerup_icon_width // 2) - (timer_text.get_width() // 2), powerup_y_pos + powerup_icon_height + 5))
    grenade_count_text = font.render(f"Grenades: {grenade_ammo}", True, WHITE)
    screen.blit(grenade_count_text, (10, 160))

def startup_screen():
    screen.fill(BLACK)
    title_font = pygame.font.Font("pixelfont.ttf", 50)
    button_font = pygame.font.Font("pixelfont.ttf", 30)
    title_text = title_font.render("Zombie Hunter", True, WHITE)
    start_button = button_font.render("Start Game", True, WHITE)
    settings_button = button_font.render("Settings", True, WHITE)
    quit_button = button_font.render("Quit Game", True, WHITE)
    screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 2 - 100))
    screen.blit(start_button, (width // 2 - start_button.get_width() // 2, height // 2))
    screen.blit(settings_button, (width // 2 - settings_button.get_width() // 2, height // 2 + 50))
    screen.blit(quit_button, (width // 2 - quit_button.get_width() // 2, height // 2 + 100))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
    freeze_active = active_powerup_timers["freeze"] > current_time

    # Infinite ammo logic
    infinite_ammo_active = active_powerup_timers["infinite_ammo"] > current_time


def draw_hud():
    # Health bar dimensions and position
    health_bar_width = 200
    health_bar_height = 20
    border_thickness = 3
    health_ratio = health / 100

    # Draw health bar
    pygame.draw.rect(screen, WHITE, (
        10 - border_thickness, 10 - border_thickness, health_bar_width + 2 * border_thickness,
        health_bar_height + 2 * border_thickness))
    pygame.draw.rect(screen, RED, (10, 10, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, GREEN, (10, 10, health_bar_width * health_ratio, health_bar_height))

    # Draw shield bar
    shield_bar_width = 200
    shield_bar_height = 20
    shield_ratio = shield / 100

    # Draw shield bar
    pygame.draw.rect(screen, WHITE, (
        10 - border_thickness, 40 - border_thickness, shield_bar_width + 2 * border_thickness,
        shield_bar_height + 2 * border_thickness))
    pygame.draw.rect(screen, (50, 50, 50),
                     (10, 40, shield_bar_width, shield_bar_height))  # Grey background for shield bar
    pygame.draw.rect(screen, BLUE, (10, 40, shield_bar_width * shield_ratio, shield_bar_height))

    # Draw stamina bar
    stamina_bar_width = 200
    stamina_bar_height = 20
    stamina_ratio = stamina / max_stamina

    # Draw stamina bar
    pygame.draw.rect(screen, WHITE, (
        10 - border_thickness, 70 - border_thickness, stamina_bar_width + 2 * border_thickness,
        stamina_bar_height + 2 * border_thickness))
    pygame.draw.rect(screen, (50, 50, 50),
                     (10, 70, stamina_bar_width, stamina_bar_height))  # Grey background for stamina bar
    pygame.draw.rect(screen, GREEN, (10, 70, stamina_bar_width * stamina_ratio, stamina_bar_height))

    # Draw round number
    round_text = font.render(f"Wave: {round_num}", True, WHITE)
    screen.blit(round_text, (10, height - 40))

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (width - 150, height - 40))

    # Display "Insufficient Funds" message if applicable
    if insufficient_funds:
        insufficient_funds_text = font.render("Insufficient Funds", True, RED if int(time.time() * 5) % 2 == 0 else WHITE)
        screen.blit(insufficient_funds_text, (width // 2 - insufficient_funds_text.get_width() // 2, 10))

    # Draw gun type and ammo
    gun_text = font.render(f"Gun: {gun_type.capitalize()}", True, WHITE)
    screen.blit(gun_text, (10, 100))  # Position above the ammo count
    ammo_text = font.render(f"Ammo: {'∞' if infinite_ammo_active else f'{current_ammo}/{ammo[gun_type]}'}", True, WHITE)
    screen.blit(ammo_text, (10, 130))
    if reloading:
        reload_text = font.render("Reloading...", True, RED)
        screen.blit(reload_text, (10, 190))

    # Display active power-ups
    current_time = time.time()
    powerup_icon_width = 80
    powerup_icon_height = 64
    powerup_y_pos = height - 100
    total_icons = len([p for p, t in active_powerup_timers.items() if t > current_time])
    total_width = total_icons * (powerup_icon_width + 10) - 10
    start_x = (width // 2) - (total_width // 2)

    for index, (powerup, end_time) in enumerate(active_powerup_timers.items()):
        if end_time > current_time:
            powerup_image = pygame.transform.scale(powerup_images[powerup], (powerup_icon_width, powerup_icon_height))
            x_pos = start_x + index * (powerup_icon_width + 10)
            screen.blit(powerup_image, (x_pos, powerup_y_pos))

            # Draw the remaining timer below the image
            timer_text = font.render(f"{int(end_time - current_time)}s", True, WHITE)
            screen.blit(timer_text, (
                x_pos + (powerup_icon_width // 2) - (timer_text.get_width() // 2),
                powerup_y_pos + powerup_icon_height + 5))

    # Display grenades count in HUD
    grenade_count_text = font.render(f"Grenades: {grenade_ammo}", True, WHITE)
    screen.blit(grenade_count_text, (10, 160))  # Adjust position below the pistol ammo


# Startup Screen
def startup_screen():
    screen.fill(BLACK)
    title_font = pygame.font.Font("pixelfont.ttf", 50)
    button_font = pygame.font.Font("pixelfont.ttf", 30)
    title_text = title_font.render("Zombie Hunter", True, WHITE)
    start_button = button_font.render("Start Game", True, WHITE)
    settings_button = button_font.render("Settings", True, WHITE)
    quit_button = button_font.render("Quit Game", True, WHITE)

    screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 2 - 100))
    screen.blit(start_button, (width // 2 - start_button.get_width() // 2, height // 2))
    screen.blit(settings_button, (width // 2 - settings_button.get_width() // 2, height // 2 + 50))
    screen.blit(quit_button, (width // 2 - quit_button.get_width() // 2, height // 2 + 100))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if width // 2 - start_button.get_width() // 2 <= mouse_x <= width // 2 + start_button.get_width() // 2 and height // 2 <= mouse_y <= height // 2 + start_button.get_height():
                    return
                elif width // 2 - quit_button.get_width() // 2 <= mouse_x <= width // 2 + quit_button.get_width() // 2 and height // 2 + 100 <= mouse_y <= height // 2 + 100 + quit_button.get_height():
                    pygame.quit()
                    exit()
                elif width // 2 - settings_button.get_width() // 2 <= mouse_x <= width // 2 + settings_button.get_width() // 2 and height // 2 + 50 <= mouse_y <= height // 2 + 50 + settings_button.get_height():
                    settings_menu()

        # Change button color on hover
        mouse_x, mouse_y = pygame.mouse.get_pos()
        start_button_color = RED if width // 2 - start_button.get_width() // 2 <= mouse_x <= width // 2 + start_button.get_width() // 2 and height // 2 <= mouse_y <= height // 2 + start_button.get_height() else WHITE
        settings_button_color = RED if width // 2 - settings_button.get_width() // 2 <= mouse_x <= width // 2 + settings_button.get_width() // 2 and height // 2 + 50 <= mouse_y <= height // 2 + 50 + settings_button.get_height() else WHITE
        quit_button_color = RED if width // 2 - quit_button.get_width() // 2 <= mouse_x <= width // 2 + quit_button.get_width() // 2 and height // 2 + 100 <= mouse_y <= height // 2 + 100 + quit_button.get_height() else WHITE

        start_button = button_font.render("Start Game", True, start_button_color)
        settings_button = button_font.render("Settings", True, settings_button_color)
        quit_button = button_font.render("Quit Game", True, quit_button_color)

        screen.blit(start_button, (width // 2 - start_button.get_width() // 2, height // 2))
        screen.blit(settings_button, (width // 2 - settings_button.get_width() // 2, height // 2 + 50))
        screen.blit(quit_button, (width // 2 - quit_button.get_width() // 2, height // 2 + 100))

        pygame.display.flip()


def settings_menu():
    global width, height  # Declare width and height as global variables
    screen.fill(BLACK)
    button_font = pygame.font.Font("pixelfont.ttf", 30)
    fullscreen_button = button_font.render("Toggle Fullscreen", True, WHITE)
    back_button = button_font.render("Back", True, WHITE)

    screen.blit(fullscreen_button, (width // 2 - fullscreen_button.get_width() // 2, height // 2))
    screen.blit(back_button, (width // 2 - back_button.get_width() // 2, height // 2 + 50))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if width // 2 - fullscreen_button.get_width() // 2 <= mouse_x <= width // 2 + fullscreen_button.get_width() // 2 and height // 2 <= mouse_y <= height // 2 + fullscreen_button.get_height():
                    pygame.display.toggle_fullscreen()
                    width, height = screen.get_size()  # Update width and height after toggling fullscreen
                    reset_hud()
                elif width // 2 - back_button.get_width() // 2 <= mouse_x <= width // 2 + back_button.get_width() // 2 and height // 2 + 50 <= mouse_y <= height // 2 + 50 + back_button.get_height():
                    return

        # Change button color on hover
        mouse_x, mouse_y = pygame.mouse.get_pos()
        fullscreen_button_color = RED if width // 2 - fullscreen_button.get_width() // 2 <= mouse_x <= width // 2 + fullscreen_button.get_width() // 2 and height // 2 <= mouse_y <= height // 2 + fullscreen_button.get_height() else WHITE
        back_button_color = RED if width // 2 - back_button.get_width() // 2 <= mouse_x <= width // 2 + back_button.get_width() // 2 and height // 2 + 50 <= mouse_y <= height // 2 + 50 + back_button.get_height() else WHITE

        fullscreen_button = button_font.render("Toggle Fullscreen", True, fullscreen_button_color)
        back_button = button_font.render("Back", True, back_button_color)

        screen.blit(fullscreen_button, (width // 2 - fullscreen_button.get_width() // 2, height // 2))
        screen.blit(back_button, (width // 2 - back_button.get_width() // 2, height // 2 + 50))

        pygame.display.flip()

def reset_hud():
    global font
    font = pygame.font.Font("pixelfont.ttf", 24 * (width / 800))

def reset_game():
    global player_x, player_y, health, shield, score, round_num, stamina, zombies, bullets, active_powerups, gun_type, current_ammo, running, player_image, grenade_ammo, grenades
    player_x, player_y = 400, 300
    health, shield, score, round_num = 100, 0, 0, 1
    stamina = max_stamina  # Reset stamina
    zombies, bullets, active_powerups = [], [], []
    gun_type = "pistol"
    current_ammo = ammo[gun_type]
    zombies = spawn_zombies(round_num)
    running = True
    player_image = player_stand_image  # Reset player image
    grenade_ammo = 3  # Reset grenade ammo
    grenades = []  # Reset grenades

def ensure_player_within_boundaries():
    global player_x, player_y
    player_x = max(0, min(player_x, map_width))
    player_y = max(0, min(player_y, map_height))


# Game Loop
running = True
paused = False
buy_menu_open = False
camera_x, camera_y = 0, 0
zombies = spawn_zombies(round_num)
grenades = []  # List to store grenades
grenade_ammo = 3  # Starting ammo for grenades

# Show startup screen
startup_screen()

while running:
    screen.fill(BLACK)
    camera_x, camera_y = player_x - width // 2, player_y - height // 2
    screen.blit(background_image, (-camera_x, -camera_y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if buy_menu_open:
                handle_buy_click(event.pos)
            else:
                shoot_bullet(player_x, player_y, *pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reloading, reload_start_time = True, time.time()
            elif event.key == pygame.K_g:  # Press 'G' to drop a grenade
                if grenade_ammo > 0:  # Ensure the player has grenades
                    grenades.append(Grenade(player_x, player_y))  # Drop a grenade at the player's position
                    grenade_ammo -= 1  # Decrease the grenade count
            elif event.key == pygame.K_ESCAPE:  # Press 'ESC' to pause/unpause the game
                paused = not paused
            elif event.key == pygame.K_f:  # Press 'F' to toggle fullscreen
                pygame.display.toggle_fullscreen()
            elif event.key == pygame.K_TAB:  # Press 'TAB' to open/close buy menu
                buy_menu_open = not buy_menu_open
                paused = buy_menu_open

    # Continuous shooting for assault rifle
    if pygame.mouse.get_pressed()[0] and gun_type == "assault_rifle" and not buy_menu_open:
        shoot_bullet(player_x, player_y, *pygame.mouse.get_pos())

    if paused:
        if buy_menu_open:
            draw_buy_menu()
        else:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Semi-transparent overlay
            screen.blit(overlay, (0, 0))
            pause_text = font.render("Paused", True, WHITE)
            screen.blit(pause_text, (width // 2 - pause_text.get_width() // 2, height // 2))
            exit_text = font.render("Press ESC to Exit", True, WHITE)
            screen.blit(exit_text, (width // 2 - exit_text.get_width() // 2, height // 2 + 50))
            settings_button = font.render("Settings", True, WHITE)
            screen.blit(settings_button, (width // 2 - settings_button.get_width() // 2, height // 2 + 100))
            pygame.display.flip()

            while paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        paused = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        paused = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if width // 2 - settings_button.get_width() // 2 <= mouse_x <= width // 2 + settings_button.get_width() // 2 and height // 2 + 100 <= mouse_y <= height // 2 + 100 + settings_button.get_height():
                            settings_menu()
                            paused = False
                if not running:
                    break
            continue

    # Reloading logic inside the game loop
    if reloading:
        if gun_type == "assault_rifle":
            player_image = player_ak_reload_image  # Show AK reload image while reloading
        elif gun_type == "shotgun":
            player_image = player_shotgun_reload_image  # Show shotgun reload image while reloading
        else:
            player_image = player_reload_image  # Show reload image while reloading
        if time.time() - reload_start_time >= reload_time:
            reloading = False  # Reset reloading state
            current_ammo = ammo[gun_type]  # Reload ammo to full
            # Update player image based on gun type after reloading
            if gun_type == "assault_rifle":
                player_image = player_ak_hold_image
            elif gun_type == "shotgun":
                player_image = player_shotgun_hold_image
            else:
                player_image = pygame.image.load("hitman1_gun.png")

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LSHIFT] and stamina > 0:  # Running logic
        player_speed = 3.8
        stamina -= 0.3  # Stamina drain
    else:
        player_speed = 1.9
        stamina += 0.2  # Regain stamina when not running
    stamina = max(0, min(stamina, max_stamina))  # Clamp stamina between 0 and max_stamina

    player_x += (keys[pygame.K_d] - keys[pygame.K_a]) * player_speed
    player_y += (keys[pygame.K_s] - keys[pygame.K_w]) * player_speed

    # Ensure player stays within map boundaries
    ensure_player_within_boundaries()

    # Rotate player image to face the mouse
    mouse_x, mouse_y = pygame.mouse.get_pos()
    angle = math.atan2(mouse_y - height // 2, mouse_x - width // 2)
    rotated_player = pygame.transform.rotate(player_image, -math.degrees(angle))

    # Draw the rotated player image at the player's position
    player_rect = rotated_player.get_rect(center=(player_x - camera_x, player_y - camera_y))
    screen.blit(rotated_player, player_rect.topleft)

    # Update and draw grenades
    for grenade in grenades[:]:
        grenade.update(zombies)
        if grenade.exploded:
            grenades.remove(grenade)  # Remove grenade after explosion
        grenade.draw(camera_x, camera_y)

    # Handle bullets, zombies, blood splatter, power-ups (existing logic)
    for bullet in bullets[:]:
        bullet.move()
        bullet.draw(camera_x, camera_y)
        if bullet.explosive and not bullet.exploded:
            bullet.explode(zombies)
            draw_explosion(bullet.x, bullet.y, camera_x, camera_y)  # Draw explosion effect
            bullets.remove(bullet)
        for zombie in zombies[:]:
            if math.hypot(zombie.x - bullet.x, zombie.y - bullet.y) < 30:
                damage = 999 if insta_kill_active else weapon_damage[gun_type]
                zombie.health -= damage
                if zombie.health <= 0:
                    spawn_powerup_at_zombie(zombie.x, zombie.y)
                    for _ in range(10):  # Generate 10 blood splatter particles
                        angle = random.uniform(0, 2 * math.pi)  # Random direction for each particle
                        blood_splatter_particles.append(BloodSplatter(zombie.x, zombie.y, angle))
                    zombies.remove(zombie)
                    score += 10  # Add points for killing a zombie
                bullets.remove(bullet)
                break
        if bullet.travel_distance >= bullet.max_distance or not (0 <= bullet.x <= map_width and 0 <= bullet.y <= map_height):
            bullets.remove(bullet)

    # Update and draw blood splatter particles
    for particle in blood_splatter_particles[:]:
        if particle.update():
            blood_splatter_particles.remove(particle)
        else:
            particle.draw(camera_x, camera_y)

    for zombie in zombies:
        angle = zombie.move_towards_player(player_x, player_y)
        zombie.draw(camera_x, camera_y, angle)
        if math.hypot(zombie.x - player_x, player_y - player_y) < 30:
            if shield > 0:
                shield -= 1  # Reduce shield first
            else:
                health -= 1  # Only reduce player health if shield is depleted

    # Handle power-ups and HUD (existing logic)
    for powerup in active_powerups[:]:
        powerup.draw(camera_x, camera_y)
        if math.hypot(powerup.x - player_x, powerup.y - player_y) < 20:
            active_powerup_timers[powerup.type] = time.time() + 24  # Set power-up timer for 24 seconds
            active_powerups.remove(powerup)

    apply_powerups()

    # Handle Game Over
    if health <= 0:
        running = False
        # Display "Game Over" message
        screen.fill(BLACK)
        game_over_text = font.render("Game Over", True, RED)
        restart_text = font.render('Press "R" To Restart', True, WHITE)
        screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - 50))
        screen.blit(restart_text, (width // 2 - restart_text.get_width() // 2, height // 2 + 10))
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    reset_game()
                    break
            if running:
                break

    # Draw HUD
    draw_hud()

    # If no zombies remain, start next round
    if not zombies:
        round_num += 1
        zombies = spawn_zombies(round_num)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

def draw_explosion(x, y, camera_x, camera_y):
    explosion_image = pygame.image.load("explosion.png").convert_alpha()
    explosion_image = pygame.transform.scale(explosion_image, (100, 100))
    screen.blit(explosion_image, (x - camera_x - 50, y - camera_y - 50))