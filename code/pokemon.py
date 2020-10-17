import pygame
import os
import time
import random

pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokemon Shooter")


# Load all the images ok pokemons from assets folder
BULBASAUR = pygame.image.load(os.path.join("assets", "bulbasaur.png"))
CHARMANDER = pygame.image.load(os.path.join("assets", "charmander.png"))
PIKACHU = pygame.image.load(os.path.join("assets", "pikachu.png"))
SQUIRTLE = pygame.image.load(os.path.join("assets", "squirtle.png"))

# Player - Ash Ketchum :P
TRAINER = pygame.image.load(os.path.join("assets", "ash.png"))

#Game Window Icon
ICON = pygame.image.load(os.path.join("assets", "game_icon.png"))

# Weapons  (Super powers)
BULBASAUR_LEAF = pygame.image.load(os.path.join("assets", "leaf.png"))
CHARMANDER_FLAME = pygame.image.load(os.path.join("assets", "flame.png"))
PIKACHU_THUNDER = pygame.image.load(os.path.join("assets", "thunder.png"))
SQUIRTLE_WATER = pygame.image.load(os.path.join("assets", "water-drop.png"))
POKEBALL = pygame.image.load(os.path.join("assets", "pokeball.png"))

# Playground image
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")), (WIDTH, HEIGHT))

pygame.display.set_icon(ICON)

class Weapon:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)




class Avatar:

    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.avatar_img = None
        self.weapon_img = None
        self.weapons = []
        self.cool_down_counter = 0

    def draw(self, window):
        #pygame.draw.rect(window, (255,0,0), (self.x, self.y, 50, 50))
        window.blit(self.avatar_img, (self.x, self.y))
        for weapon in self.weapons:
            weapon.draw(window)

    def move_weapons(self, vel, obj):
        self.cooldown()
        for weapon in self.weapons:
            weapon.move(vel)
            if weapon.off_screen(HEIGHT):
                self.weapons.remove(weapon)
            elif weapon.collision(obj):
                obj.health -= 10
                self.weapons.remove(weapon)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            weapon = Weapon(self.x+25, self.y, self.weapon_img)
            self.weapons.append(weapon)
            self.cool_down_counter = 1

    def get_width(self):
        return self.avatar_img.get_width()

    def get_height(self):
        return self.avatar_img.get_height()


class Player(Avatar):
    def __init__(self, x, y, health=100):
        super().__init__(x,y, health)
        self.avatar_img = TRAINER
        self.weapon_img = POKEBALL
        self.mask = pygame.mask.from_surface(self.avatar_img)
        self.max_health = health

    def move_weapons(self, vel, objs):
        self.cooldown()
        for weapon in self.weapons:
            weapon.move(vel)
            if weapon.off_screen(HEIGHT):
                self.weapons.remove(weapon)
            else:
                for obj in objs:
                    if weapon.collision(obj):
                        objs.remove(obj)
                        if weapon in self.weapons:
                            self.weapons.remove(weapon)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y+self.avatar_img.get_height()+10, self.avatar_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y+self.avatar_img.get_height()+10, self.avatar_img.get_width()*(self.health/self.max_health), 10))

class Pokemon(Avatar):

    POKEMON_TYPE = {
        "leaf": (BULBASAUR, BULBASAUR_LEAF),
        "fire": (CHARMANDER, CHARMANDER_FLAME),
        "water": (SQUIRTLE, SQUIRTLE_WATER),
        "thunder": (PIKACHU, PIKACHU_THUNDER)
    }

    def __init__(self, x, y, poke_type, health = 100):
        super().__init__(x,y, health)
        self.avatar_img, self.weapon_img = self.POKEMON_TYPE[poke_type]
        self.mask = pygame.mask.from_surface(self.avatar_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            weapon = Weapon(self.x+10, self.y, self.weapon_img)
            self.weapons.append(weapon)
            self.cool_down_counter = 1



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x  # if this value is negative then the objects are not colliding (i.e) no pixel overlapping
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    pokes = []
    wave_length = 5
    pokemon_vel = 1
    weapon_vel = 4

    player_vel = 5
    player = Player(300, 630)
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0)) # 0,0 is top left in pygame
        # draw text
        lives_label = main_font.render(f"Lives: {lives}",1, (255,255,255))
        level_label = main_font.render(f"Level: {level}",1, (255,255,255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for pokemon in pokes:
            pokemon.draw(WIN)

        player.draw(WIN)    

        if lost:
            lost_label = lost_font.render("You Lost Trainer...", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 5: # Total number of seconds to display the lost message
                run = False
            else:
                continue

        if len(pokes) == 0:
            level += 1
            wave_length += 5

            for i in range(wave_length):
                poke = Pokemon(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["leaf", "water", "fire", "thunder"]))
                pokes.append(poke)
        
        for event in pygame.event.get():
            if event.type == pygame.constants.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: #move left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel+player.get_width() < WIDTH: #move right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #move up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel+player.get_height() + 15 < HEIGHT: #move down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        for poke in pokes[:]:
            poke.move(pokemon_vel)
            poke.move_weapons(weapon_vel, player)

            if random.randrange(0, 2*60) == 1:
                poke.shoot()

            if collide(poke, player):
                player.health -= 10
                pokes.remove(poke)
            elif poke.y + poke.get_height() > HEIGHT:
                lives -= 1
                pokes.remove(poke)

        player.move_weapons(-weapon_vel, pokes) # to move the pokeball upwards we need to give -ve velocity

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.constants.QUIT:
                run = False
            if event.type == pygame.constants.MOUSEBUTTONDOWN:
                main()

    pygame.quit()
        
main_menu()
