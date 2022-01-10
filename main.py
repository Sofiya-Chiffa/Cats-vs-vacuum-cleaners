import os
import sys
import pygame
import sqlite3
from itertools import product


DIS_SIZE = (1000, 600)
pygame.init()
screen = pygame.display.set_mode(DIS_SIZE)
pygame.display.set_caption('Коты против пылесосов')
clock = pygame.time.Clock()
FPS = 50
conn = sqlite3.connect("game_base.sqlite3")
all_levels = pygame.sprite.Group()


# Выход из игры
def terminate():
    pygame.quit()
    sys.exit()


# Загрузка изображений
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


# Рисование текста для заставки игры
def draw_text(text, color, type):
    font = pygame.font.SysFont('comicsansms', 35)
    text_coord = 50
    if type == 3:
        text_coord += 64
    for line in text:
        string_rendered = font.render(line, True, color)
        intro_rect = string_rendered.get_rect()
        text_coord += 15
        intro_rect.top = text_coord
        intro_rect.x = 30
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


# Экран начала игры
def start_screen():
    intro_text = ["НАЧАТЬ ИГРУ", "ВЫЙТИ ИЗ ИГРЫ"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (DIS_SIZE[0], DIS_SIZE[1]))
    screen.blit(fon, (0, 0))
    # Все "магические числа" вычислены опытным путём
    pygame.draw.rect(screen, 'grey', (28, 48, 320, 70))
    pygame.draw.rect(screen, 'gray', (28, 120, 320, 65))

    draw_text(intro_text, 'black', 1)

    # Цикл заставки игры
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                # Для перехода на карту уровней
                if 28 <= event.pos[0] <= 348 and 48 <= event.pos[1] <= 118:
                    level_map()
                    return
                # Для выхода из игры
                elif 28 <= event.pos[0] <= 348 and 120 <= event.pos[1] <= 185:
                    terminate()
            # Смена цвета текста кнопки "Начать игру"
            if event.type == pygame.MOUSEMOTION and \
                    (28 <= event.pos[0] <= 348 and 48 <= event.pos[1] <= 118):
                draw_text([intro_text[0]], 'white', 2)
            else:
                draw_text([intro_text[0]], 'black', 2)
            # Смена цвета текста кнопки Выйти из игры
            if event.type == pygame.MOUSEMOTION and \
                    (28 <= event.pos[0] <= 348 and 120 <= event.pos[1] <= 185):
                draw_text([intro_text[1]], 'white', 3)
            else:
                draw_text([intro_text[1]], 'black', 3)

        pygame.display.flip()
        clock.tick(FPS)


# Здесь рисуется карта уровней, и при нажатии на уровень будет запускаться соответствующий
def level_map():
    font = pygame.font.SysFont('comicsansms', 35)
    text_coord = 30
    string_rendered = font.render('ВЫБЕРИТЕ УРОВЕНЬ', True, 'black')
    intro_rect = string_rendered.get_rect()
    intro_rect.top = text_coord
    intro_rect.x = 350

    spr_x = 40
    spr_y = 100
    for i in range(1, 8):
        sprite = pygame.sprite.Sprite()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.status as st FROM levels l
            WHERE l.id = ?""", (i,))
        # Если уровень не пройден рисуется красная картинка, иначе - зеленая
        sprite.image = load_image('red_lvl.png').convert_alpha()
        for row in cursor:
            if row[0] == 1:
                sprite.image = load_image('green_lvl.png').convert_alpha()
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x += 20
        all_levels.add(sprite)
        sprite.rect.x += spr_x
        sprite.rect.y = spr_y
        spr_x += 20 + 205
        if spr_x >= 775:
            sprite.x = 0
            spr_x = 40
            spr_y = 325
    check_board = Board(4, 2)
    check_board.set_view(60, 100, 225)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for lvl in all_levels:
                    if lvl.rect.collidepoint(event.pos):
                        num_level = check_board.get_click(event.pos)[0] + 1
                        if check_board.get_click(event.pos)[1] > 0:
                            num_level += 4
                        print(num_level)
                        return
        screen.fill('white')
        all_levels.draw(screen)
        screen.blit(string_rendered, intro_rect)

        font1 = pygame.font.SysFont('comicsansms', 70)
        top_coord = 170
        intr_x = 140
        for i in range(7):
            string_rendered1 = font1.render(f'{i + 1}', True, 'black')
            intro_rect1 = string_rendered.get_rect()
            intro_rect1.top = top_coord
            intro_rect1.x = intr_x
            screen.blit(string_rendered1, intro_rect1)
            intr_x += 225
            if intr_x > 1000:
                intr_x = 140
                top_coord = 400
        check_board.render(screen)
        pygame.display.flip()
        clock.tick(FPS)


# Общий класс для рисования клетчатого поля
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
        return self.on_click(self.get_cell(mouse_pos))

    def on_click(self, cell_coords):
        print(cell_coords)
        return cell_coords

    def get_cell(self, mouse_pos):
        if self.left <= mouse_pos[0] <= self.left + self.cs * self.width and \
                self.top <= mouse_pos[1] <= self.top + self.cs * self.height:
            x = (mouse_pos[0] - self.left) // self.cs
            y = (mouse_pos[1] - self.top) // self.cs
            return x, y
        else:
            return None


# Класс для рисования магазина
class Shop(Board):

    def __init__(self, width, height):
        super().__init__(width, height)

    def move_cat_to_board(self):
        pass


# Класс для рисования информационной панели сверху уровня
class InfoBar(Board):

    def __init__(self, width, height):
        super().__init__(width, height)
        # Ширина и высота в пикселях
        self.width_px = DIS_SIZE[0] // width
        self.height_px = 30

    # Отрисовка прямоугольников
    def render(self, surface):
        for x, y in product(range(self.width), range(self.height)):
            pygame.draw.rect(surface, 'white', (0, 0, (x + 1) * self.width_px,
                                                self.height_px), width=1)

    # Получение координат клетки
    def get_cell(self, mouse_pos):
        if mouse_pos[0] <= self.width_px * self.width and \
                mouse_pos[1] <= self.height_px * self.height:
            x = mouse_pos[0] // self.width_px
            y = mouse_pos[1] // self.height_px
            return x, y
        else:
            return None

    # Возвращение на карту уровней при нажатии на ячейку
    def back_to_menu(self):
        pass

    # Рисование текста монет (Их количество будет меняться в процессе игры)
    def show_coins(self):
        pass

    # Отображение названия текущего уровня
    def show_lvl(self):
        pass


# Класс котиков
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
            if self.dt_attack >= self.vel_attack and \
                    self.power[0] is not None:
                self.dt_attack = 0
                CatAttack(self.power, (self.rect.x, self.rect.y))
        elif self.power[1] == 0:
            self.dt_attack += dt / 1000
            if self.dt_fps >= 0.15:
                self.dt_fps = 0
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                if self.dt_attack >= self.vel_attack and \
                        self.power[0] is not None:
                    self.dt_attack = 0
                    CatAttack(self.power, (self.rect.x, self.rect.y))
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


class CatAttack(pygame.sprite.Sprite):

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


# Класс врагов
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


start_screen()

info_bar = InfoBar(3, 1)

enemies_list = dict()
all_cat_attack = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()
all_cats = pygame.sprite.Group()
board = Board(9, 6)
cell_size = 80
board.set_view(DIS_SIZE[0] - cell_size * 9, DIS_SIZE[1] - cell_size * 6, cell_size)

shop = Shop(1, 5)
shop.set_view(0, 30, DIS_SIZE[1] // 5 - 6)

running = True


Cats((90, 90), 500, ('денежный кот атака.png', 0, 0), 'денежный кот.png')
Cats((90, 170), 500, ('вжух атака.png', 150, 80), 'вжух.png')
Cats((90, 250), 500, ('поп атака.png', 100, 100), 'поп.png')
Cats((90, 330), 500, ('просто кот атака.png', 200, 125), 'просто кот.png')
Cats((90, 410), 500, (None, 0, 0), 'танк.png')

Enemies((DIS_SIZE[0], 170), 100, 2000, 50, 'роб пылесос.png')
Enemies((DIS_SIZE[0], 250), 100, 1500, 150, 'пион пылесос.png')
Enemies((DIS_SIZE[0], 330), 100, 1750, 100, 'верт пылесос.png')


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            board.get_click(event.pos)
            shop.get_click(event.pos)
            info_bar.get_click(event.pos)
    dt = clock.tick()

    screen.fill('black')
    info_bar.render(screen)
    board.render(screen)
    shop.render(screen)
    
    all_enemies.draw(screen)
    all_cats.draw(screen)
    all_cat_attack.draw(screen)
    all_enemies.update(dt)
    all_cats.update(dt)
    all_cat_attack.update(dt)
    pygame.display.flip()

pygame.quit()
