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


class Enemies(pygame.sprite.Sprite):

    def __init__(self, name):
        pass

    def update(self, dt):
        pass

    def attack(self, cat):
        pass

    def taking_damage(self, damage):
        pass

    def death(self):
        pass


class Shop:
    pass


board = Board(9, 6)
running = True
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
    pygame.display.flip()
pygame.quit()
