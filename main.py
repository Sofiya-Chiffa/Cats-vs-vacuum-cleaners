import os
import sys
import pygame
from itertools import product

DIS_SIZE = (1000, 600)
pygame.init()
screen = pygame.display.set_mode(DIS_SIZE)
pygame.display.set_caption('Коты против пылесосов')


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 90
        self.top = 90
        self.cs = 80

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cs = cell_size

    def render(self, surface):
        for x, y in product(range(self.width), range(self.height)):
            pygame.draw.rect(surface, 'white', (x * self.cs + self.left, y * self.cs + self.top,
                                                self.cs, self.cs), width=1)

    def get_click(self, mouse_pos):
        self.on_click(self.get_cell(mouse_pos))

    def on_click(self, cell_coords):
        pass

    def get_cell(self, mouse_pos):
        if self.left <= mouse_pos[0] <= self.left + self.cs * self.width and \
                self.top <= mouse_pos[1] <= self.top + self.cs * self.height:
            x = (mouse_pos[0] - self.left) // self.cs
            y = (mouse_pos[1] - self.top) // self.cs
            return x, y
        else:
            return None


class Cats(pygame.sprite.Sprite):

    def __init__(self, pos, health, power, name):
        # данные будут получаться из базы данных
        super().__init__(all_cats)
        sheet = pygame.transform.scale(load_image(name), (400, 160))
        self.frames = []
        self.cut_sheet(sheet, 5, 2)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect.x, self.rect.y = pos[0], pos[1]
        self.health = health
        self.power = power  # картинка атаки, сила атаки, скорость полета атаки
        self.dt_attack, self.vel_attack = 0, 1
        self.dt_fps = 0

    def update(self, dt):
        self.dt_fps += dt / 1000
        if self.rect.y in enemies_list.keys() and enemies_list[self.rect.y] != 0:
            if self.dt_fps >= 0.15:
                self.dt_fps = 0
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
            self.dt_attack += dt / 1000
            if self.dt_attack >= self.vel_attack and\
                self.power[0] is not None:
                self.dt_attack = 0
                Cat_Attack(self.power, (self.rect.x, self.rect.y))
        elif self.power[1] == 0:
            self.dt_attack += dt / 1000
            if self.dt_fps >= 0.15:
                self.dt_fps = 0
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                if self.dt_attack >= self.vel_attack and \
                        self.power[0] is not None:
                    self.dt_attack = 0
                    Cat_Attack(self.power, (self.rect.x, self.rect.y))
        elif self.power[1] != 0:
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]

    def taking_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.death()

    def death(self):
        self.kill()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


class Cat_Attack(pygame.sprite.Sprite):

    def __init__(self, power, pos):
        super().__init__(all_cat_attack)
        self.im, self.pow, self.vel = power
        self.image = load_image(self.im)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0] + 30, pos[1]
        self.x = pos[0] + 30
        if self.pow == 0:
            self.dt = 0

    def update(self, dt):
        if self.pow != 0:
            self.x += self.vel * dt / 1000
            self.rect.x = self.x
            if pygame.sprite.spritecollideany(self, all_enemies):
                pygame.sprite.spritecollideany(self, all_enemies).taking_damage(self.pow)
                self.kill()
            elif self.x > DIS_SIZE[0]:
                self.kill()
        else:
            self.dt += dt / 1000
            if self.dt >= 0.5:
                self.kill()


class Enemies(pygame.sprite.Sprite):

    def __init__(self, pos, vel, health, power, name):
        # данные будут получаться из базы данных
        super().__init__(all_enemies)
        sheet = pygame.transform.scale(load_image(name), (400, 160))
        self.frames = []
        self.cut_sheet(sheet, 5, 2)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        enemies_list.setdefault(pos[1], 0)
        enemies_list[pos[1]] += 1
        self.rect.x, self.rect.y = pos[0] + 30, pos[1]
        self.x = pos[0] + 30
        self.vel = vel
        self.health, self.power = health, power
        self.vel_attack = 1
        self.run = True
        self.dt_fps = 0

    def update(self, dt):
        self.dt_fps += dt / 1000
        if self.dt_fps >= 0.15:
            self.dt_fps = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        if self.run:
            self.x -= self.vel * dt / 1000
            self.rect.x = self.x
            if pygame.sprite.spritecollideany(self, all_cats):
                self.x -= 5
                self.dt_attack = 0
                self.run = False
        else:
            self.dt_attack += dt / 1000
            if self.dt_attack >= self.vel_attack:
                self.dt_attack = 0
                self.attack(pygame.sprite.spritecollideany(self, all_cats))
                if not pygame.sprite.spritecollideany(self, all_cats):
                    self.run = True
        if self.rect.x == -40:
            self.kill()
            # - здоровье игрока

    def attack(self, cat):
        cat.taking_damage(self.power)

    def taking_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.death()

    def death(self):
        enemies_list[self.rect.y] -= 1
        self.kill()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


class Shop:
    pass


enemies_list = dict()
all_cat_attack = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()
all_cats = pygame.sprite.Group()
board = Board(9, 6)
running = True
#
Cats((90, 90), 500, ('денежный кот атака.png', 0, 0), 'денежный кот.png')
Cats((90, 170), 500, ('вжух атака.png', 150, 80), 'вжух.png')
Cats((90, 250), 500, ('поп атака.png', 100, 100), 'поп.png')
Cats((90, 330), 500, ('просто кот атака.png', 200, 125), 'просто кот.png')
Cats((90, 410), 500, (None, 0, 0), 'танк.png')
#
Enemies((DIS_SIZE[0], 170), 100, 2000, 50, 'роб пылесос.png')
Enemies((DIS_SIZE[0], 250), 100, 1500, 150, 'пион пылесос.png')
Enemies((DIS_SIZE[0], 330), 100, 1750, 100, 'верт пылесос.png')
#

clock = pygame.time.Clock()
while running:
    screen.fill('black')
    board.render(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            board.get_click(event.pos)
    dt = clock.tick()
    all_enemies.draw(screen)
    all_cats.draw(screen)
    all_cat_attack.draw(screen)
    all_enemies.update(dt)
    all_cats.update(dt)
    all_cat_attack.update(dt)
    pygame.display.flip()
pygame.quit()
