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
num_level, dt_level = None, 0


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
                    return level_map()
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
    global num_level
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
                        cur = conn.cursor()
                        text_tuple = cur.execute("""
                            SELECT lvl_map as st FROM levels
                            WHERE id = ?""", (num_level,)).fetchall()[0]
                        text = text_tuple[0].split('\\n')
                        return text
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


def load_level(text):
    if text[0] == '':
        return
    for i in range(6):
        if text[i][0] == 'в':
            Enemies((DIS_SIZE[0], 120 + (i * 80)), 'Вертикальный пылесос')
        elif text[i][0] == 'п':
            Enemies((DIS_SIZE[0], 120 + (i * 80)), 'Пылесос пионер')
        elif text[i][0] == 'р' or text[i][0] == 'p':
            Enemies((DIS_SIZE[0], 120 + (i * 80)), 'Робот пылесос')
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
        return self.on_click(self.get_cell(mouse_pos))

    def on_click(self, cell_coords):
        return cell_coords

    def get_cell(self, mouse_pos):
        if self.left <= mouse_pos[0] <= self.left + self.cs * self.width and \
                self.top <= mouse_pos[1] <= self.top + self.cs * self.height:
            x = (mouse_pos[0] - self.left) // self.cs
            y = (mouse_pos[1] - self.top) // self.cs
            return x, y
        else:
            return None

    def change_board(self, pos):
        self.board[board.get_click(pos)[1]][board.get_click(pos)[0]] = \
            (self.board[board.get_click(pos)[1]][board.get_click(pos)[0]] + 1) % 2

    def ret_status(self, pos):
        return self.board[board.get_click(pos)[1]][board.get_click(pos)[0]]


# Класс для рисования магазина
class Shop(Board):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.arts = {0: ['денежный кот0.png', 0, 'Денежный кот'], 1: ['поп0.png', 0, 'Кот-поп'],
                     2: ['просто кот0.png', 0, 'Просто кот'],
                     3: ['танк0.png', 0, 'Кот-танк'], 4: ['вжух0.png', 0, 'Кот-вжух']}
        # добавить стоимость и имена

    def render(self, surface):
        i = 0
        for x, y in product(range(self.width), range(self.height)):
            image = pygame.transform.scale(load_image(self.arts[i][0]), (114, 114))
            image_rect = image.get_rect()
            image_rect.x, image_rect.y = x * self.cs + self.left, y * self.cs + self.top
            screen.blit(image, image_rect)
            pygame.draw.rect(surface, 'white', (x * self.cs + self.left, y * self.cs + self.top,
                                                self.cs, self.cs), width=1)
            i += 1

    def check_cat(self, pos):
        if pos is None:
            return ''
        if self.arts[pos[1]][1] <= 0:  # деньги игрока
            return self.arts[pos[1]][2]
        else:
            return ''

    def move_cat_to_board(self, pos, name):
        if board.ret_status(pos) == 1:
            return
        board.change_board(pos)
        # Отнимаются деньги - sek
        Cats((board.get_click(pos)[0] * 80 + (DIS_SIZE[0] - cell_size * 9),
              board.get_click(pos)[1] * 80 + (DIS_SIZE[1] - cell_size * 6)), name)


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

    def update(self):
        # Надпись уровня
        global num_level
        cur = conn.cursor()
        lvl_name = f'lvl.{num_level}'
        font = pygame.font.SysFont('comicsansms', 20)
        text_coord = 1
        string_rendered = font.render(lvl_name, True, 'white')
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = DIS_SIZE[0] // 3 // 2 - 20
        screen.blit(string_rendered, intro_rect)
        # Монетка
        image = pygame.transform.scale(load_image('coin.png'), (30, 30))
        screen.blit(image, (DIS_SIZE[0] // 2 - 50, 0))
        # Кол-во денег
        coins = cur.execute("""SELECT coins_now FROM now_info""").fetchall()[0][0]
        font1 = pygame.font.SysFont('comicsansms', 20)
        text_coord1 = 0
        string_rendered1 = font1.render(str(coins), True, 'yellow')
        intro_rect1 = string_rendered1.get_rect()
        intro_rect1.top = text_coord1
        intro_rect1.x = DIS_SIZE[0] // 2
        screen.blit(string_rendered1, intro_rect1)
        # Текст на кнопке выхода в меню
        font2 = pygame.font.SysFont('comicsansms', 20)
        text_coord2 = 1
        string_rendered2 = font2.render('BACK TO MENU', True, 'white')
        intro_rect2 = string_rendered2.get_rect()
        intro_rect2.top = text_coord2
        intro_rect2.x = DIS_SIZE[0] - DIS_SIZE[0] // 3 // 2 - 75
        screen.blit(string_rendered2, intro_rect2)

    # Возвращение на карту уровней при нажатии на ячейку
    def back_to_menu(self):
        pass


# Класс котиков
class Cats(pygame.sprite.Sprite):

    def __init__(self, pos, name):
        super().__init__(all_cats)
        image = conn.cursor().execute("""
                            SELECT image FROM cats
                            WHERE name = ?""", (name,)).fetchall()[0]
        with open('data\cat.png', 'wb') as file:
            file.write(image[0])
        image = load_image('cat.png')
        sheet = pygame.transform.scale(image, (400, 160))
        self.frames = []
        self.cut_sheet(sheet, 5, 2)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect.x, self.rect.y = pos[0], pos[1]
        self.health = conn.cursor().execute("""
            SELECT hp FROM cats
            WHERE name = ?""", (name,)).fetchall()[0][0]
        self.power = conn.cursor().execute("""
            SELECT atack_img, dmg, fly_atack_speed FROM cats
            WHERE name = ?""", (name,)).fetchall()[0]  # картинка атаки, сила атаки, скорость полета атаки
        self.dt_attack, self.vel_attack = 0, conn.cursor().execute("""SELECT atack_speed 
            FROM cats WHERE name = ?""", (name,)).fetchall()[0][0]
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
            board.change_board((self.rect.x, self.rect.y))

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
        im, self.pow, self.vel = power
        with open('data\\at_im.png', 'wb') as file:
            file.write(im)
        self.image = load_image('at_im.png')
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
                self.attack(pygame.sprite.spritecollideany(self, all_enemies))
                self.kill()
            elif self.x > DIS_SIZE[0]:
                self.kill()
        else:
            self.dt += dt / 1000
            if self.dt >= 0.5:
                # кот делает деньги
                self.kill()

    def attack(self, en):
        if en is None:
            return
        en.taking_damage(self.pow)


# Класс врагов
class Enemies(pygame.sprite.Sprite):

    def __init__(self, pos, name):
        super().__init__(all_enemies)
        image = conn.cursor().execute("""
            SELECT en_image FROM enemies
            WHERE name = ?""", (name,)).fetchall()[0]
        with open('data\en.png', 'wb') as file:
            file.write(image[0])
        image = load_image('en.png')
        sheet = pygame.transform.scale(image, (400, 160))
        self.frames = []
        self.cut_sheet(sheet, 5, 2)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        enemies_list.setdefault(pos[1], 0)
        enemies_list[pos[1]] += 1
        self.rect.x, self.rect.y = pos[0] + 30, pos[1]
        self.x = pos[0] + 30
        self.vel = conn.cursor().execute("""
            SELECT speed FROM enemies
            WHERE name = ?""", (name,)).fetchall()[0][0]
        self.health, self.power = conn.cursor().execute("""
            SELECT hp FROM enemies
            WHERE name = ?""", (name,)).fetchall()[0][0], conn.cursor().execute("""
            SELECT dmg FROM enemies
            WHERE name = ?""", (name,)).fetchall()[0][0]
        self.vel_attack = conn.cursor().execute("""
            SELECT atack_speed FROM enemies
            WHERE name = ?""", (name,)).fetchall()[0][0]
        self.run = True
        self.dt_fps = 0

    def update(self, dt):
        global player_health
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
        if self.rect.x <= 180:
            player_health -= 1
            enemies_list[self.rect.y] -= 1
            self.kill()

    def attack(self, cat):
        if cat is None:
            return
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


def change_coins(num):
    cur = conn.cursor()
    cur.execute("""UPDATE now_info SET coins_now += ?""", (num,))


def text_for_win_window(text, pos):
    font = pygame.font.SysFont('comicsansms', 25)
    string_rendered = font.render(text, True, 'black')
    rect = string_rendered.get_rect()
    rect.x, rect.y = pos
    screen.blit(string_rendered, rect)


gamer = 0
run_game = True
while run_game:
    if gamer == 0:
        text_level = start_screen()
        gamer = False
    elif gamer == 1:
        text_level = level_map()
    else:
        cur = conn.cursor()
        text = cur.execute("""
            SELECT lvl_map as st FROM levels
            WHERE id = ?""", (num_level,)).fetchall()[0]
        text_level = text[0].split('\\n')
    player_health = 3
    play = True

    enemies_list = dict()
    all_cat_attack = pygame.sprite.Group()
    all_enemies = pygame.sprite.Group()
    all_cats = pygame.sprite.Group()
    info_bar = InfoBar(3, 1)
    board = Board(9, 6)
    cell_size = 80
    board.set_view(DIS_SIZE[0] - cell_size * 9, DIS_SIZE[1] - cell_size * 6, cell_size)

    shop = Shop(1, 5)
    shop.set_view(0, 30, DIS_SIZE[1] // 5 - 6)
    make_cat = ''

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                gamer = 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if make_cat != '':
                    if board.get_click(event.pos) is not None:
                        shop.move_cat_to_board(event.pos, make_cat)
                        make_cat = ''
                make_cat = shop.check_cat(shop.get_click(event.pos))
                if info_bar.get_click(event.pos) == (2, 0):
                    running = False
                    gamer = 1
        dt = clock.tick()
        screen.fill('black')
        info_bar.update()
        info_bar.render(screen)
        board.render(screen)
        shop.render(screen)

        dt_level += dt / 1000
        if dt_level >= 1:
            dt_level = 0
            load_level(text_level)
            if len(text_level[0]) == 0:
                for k in enemies_list.keys():
                    if len(all_enemies.sprites()) > 0 and enemies_list[k] > 0:
                        break
                else:
                    play = False
        if player_health <= 0:
            play = False

        if not play:
            # требуется доработка
            pygame.draw.rect(screen, (255, 248, 220), (150, 100, 700, 400), width=0)
            pygame.draw.rect(screen, (231, 198, 151), (150, 100, 700, 400), width=5)
            if player_health <= 0:
                win_text = 'Вы проиграли...'
            else:
                win_text = 'ПОБЕДА!'
                cur = conn.cursor()
                cur.execute("""UPDATE levels SET status = ? WHERE levels.id = ?""", (1, num_level))
            font = pygame.font.SysFont('comicsansms', 35)
            string_rendered = font.render(win_text, True, 'black')
            win_rect = string_rendered.get_rect()
            win_rect.x, win_rect.y = 300, 220
            screen.blit(string_rendered, win_rect)
            menu_butt = pygame.draw.rect(screen, (186, 175, 150), (270, 295, 100, 40))
            ret_butt = pygame.draw.rect(screen, (186, 175, 150), (495, 295, 100, 40))
            text_for_win_window('в меню', (275, 300))
            text_for_win_window('заново', (500, 300))

            for sp in all_cat_attack:
                sp.kill()
            for sp in all_enemies:
                sp.kill()
            for sp in all_cats:
                sp.kill()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and \
                        menu_butt.collidepoint(event.pos):
                    gamer = 1
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and \
                        ret_butt.collidepoint(event.pos):
                    gamer = 2
                    running = False

        all_enemies.draw(screen)
        all_cats.draw(screen)
        all_cat_attack.draw(screen)
        all_enemies.update(dt)
        all_cats.update(dt)
        all_cat_attack.update(dt)

        pygame.display.flip()

pygame.quit()