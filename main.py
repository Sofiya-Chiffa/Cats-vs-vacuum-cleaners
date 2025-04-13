import os
import sys
import pygame
import sqlite3
import random
from itertools import product

t_s = 2
DIS_SIZE = (1920 / t_s, 1080 / t_s)
FPS = 50
pygame.init()
screen = pygame.display.set_mode(DIS_SIZE)
pygame.display.set_caption('Witch Next Door')
clock = pygame.time.Clock()


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


def give_text(place, num):
    return ["Хоши", "недавно мне пришо поручение от гильдии. говрят в одной квартире одинокий мужчина умер от сердечного приступа, но соседи продолжают слышать его шаги."]


# Рисование текста для заставки игры
def draw_text(text, color, place, size):
    lines = [""]
    i = 0
    for word in text.split():
        if len(word) + i > 70:
            i = 0
            lines.append("")
        i += len(word) + 1
        lines[-1] += word + " "
    for line in lines:
        font = pygame.font.SysFont('comicsansms', size)
        string_rendered = font.render(line, True, color)
        text_rect = string_rendered.get_rect()
        text_rect.top = place[1]
        place[1] += 20
        text_rect.x = place[0]
        screen.blit(string_rendered, text_rect)



def dialogue(text):
    pygame.draw.rect(screen, 'grey', (130, DIS_SIZE[1] - 150, DIS_SIZE[0] - 260, 100))
    draw_text(text[0], 'black', [130, DIS_SIZE[1] - 185], 30)
    draw_text(text[1], 'black', [145, DIS_SIZE[1] - 145], 20)


# Заставка игры и её начало
def intro(num):
    intro_text = give_text("intro", num)
    if 0 <= num <= 2:
        im = 'двор.png'
    elif 3 <= num <= 6:
        im = 'лестница.png'
    elif 7 <= num:
        im = 'лестница.png'
    fon = pygame.transform.scale(load_image(im), (DIS_SIZE[0], DIS_SIZE[1]))
    screen.blit(fon, (0, 0))
    if 7 <= num:
        neir = pygame.transform.scale(load_image('сосед.png'), (DIS_SIZE[0], DIS_SIZE[1]))
        screen.blit(neir, (0, 0))
    dialogue(intro_text)
    return


# Меню игры
def menu():
    print("this is menu")
    print("1 start")
    print("2 exit")
    a = int(input())
    if a == 1:
        return True
    else:
        return False

class Objects(pygame.sprite.Sprite):

    def __init__(self, name, active):
        super().__init__(all_obj)
        self.active = active
        if self.active == 0:
            self.image = pygame.transform.scale(load_image("шкаф" + ".png"), (495/t_s, 311/t_s))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = DIS_SIZE[0] - 490/t_s, DIS_SIZE[1] - (311/t_s + 40)
        elif self.active == 1:
            self.image = pygame.transform.scale(load_image("шкафоткрыт" + ".png"), (661 / t_s, 375 / t_s))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = DIS_SIZE[0] - 650/t_s, DIS_SIZE[1] - (375/t_s + 15)

    def get_click(self, mouse_pos):
        self.active = (self.active + 1) % 2


    def update(self, dt):
        if self.active == 0:
            self.image = pygame.transform.scale(load_image("шкаф" + ".png"), (495 / t_s, 311 / t_s))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = DIS_SIZE[0] - 490 / t_s, DIS_SIZE[1] - (311 / t_s + 40)
        elif self.active == 1:
            self.image = pygame.transform.scale(load_image("шкафоткрыт" + ".png"), (661 / t_s, 375 / t_s))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = DIS_SIZE[0] - 650 / t_s, DIS_SIZE[1] - (375 / t_s + 15)

    def delete(self):
        self.kill()


def apartment(state, time):
    if state == 0:
        im = 'гостиная.png'
    if state == 0 and time == 0:
        Objects("шкаф", 1)
    fon = pygame.transform.scale(load_image(im), (DIS_SIZE[0], DIS_SIZE[1]))
    screen.blit(fon, (5, 0))



run_game = True
state_room = 0
flag = 0
while run_game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            flag += 1
    if 0 <= flag <= 10:
        intro(flag)
    else:
        break
    pygame.display.flip()

run_game = True
all_obj = pygame.sprite.Group()
t_room = 0
while run_game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for obj in all_obj:
                if obj.rect.collidepoint(event.pos):
                    obj.get_click(event.pos)
            flag += 1
    dt = clock.tick()
    apartment(state_room, t_room)
    all_obj.draw(screen)
    all_obj.update(dt)
    pygame.display.flip()
    clock.tick(FPS)
    t_room += 1
pygame.quit()
