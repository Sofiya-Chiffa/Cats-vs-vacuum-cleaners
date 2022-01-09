import os
import sys
import pygame
from itertools import product

DIS_SIZE = (1000, 600)
pygame.init()
screen = pygame.display.set_mode(DIS_SIZE)
pygame.display.set_caption('Коты против пылесосов')
clock = pygame.time.Clock()
FPS = 50


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
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        screen.fill('green')
        pygame.display.flip()
        clock.tick(FPS)


def load_level(text):
    if text[0] == '':
        return
    for i in range(6):
        if text[i][0] == 'в':
            Enemies((DIS_SIZE, 120 + (i * 80)), 'Вертикальный пылесос')
        elif text[i][0] == 'п':
            Enemies((DIS_SIZE, 120 + (i * 80)), 'Пылесос пионер')
        elif text[i][0] == 'р':
            Enemies((DIS_SIZE, 120 + (i * 80)), 'Робот пылесос')
        text[i] = text[i][1:]



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
        self.on_click(self.get_cell(mouse_pos))

    def on_click(self, cell_coords):
        print(cell_coords)

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

    def __init__(self, name):
        pass

    def update(self, dt):
        pass

    def attack(self, enemie):
        pass

    def taking_damage(self, damage):
        pass

    def death(self):
        pass


# Класс врагов
class Enemies(pygame.sprite.Sprite):

    def __init__(self, pos, name):
        pass

    def update(self, dt):
        pass

    def attack(self, cat):
        pass

    def taking_damage(self, damage):
        pass

    def death(self):
        pass


start_screen()

info_bar = InfoBar(3, 1)

board = Board(9, 6)
cell_size = 80
board.set_view(DIS_SIZE[0] - cell_size * 9, DIS_SIZE[1] - cell_size * 6, cell_size)

shop = Shop(1, 5)
shop.set_view(0, 30, DIS_SIZE[1] // 5 - 6)

num_level, dt_level = 1, 0
text_level = ''.split('\n')

running = True
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


    dt_level += dt / 1000
    if dt_level >= 1:
        dt_level = 0
        load_level(text_level)

    pygame.display.flip()

pygame.quit()
