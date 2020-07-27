import pygame
import os
import sys

FPS = 60
WIN_WIDTH = 1000
WIN_HEIGHT = 1000

WHITE = (255, 255, 255)
ORANGE = (255, 150, 100)
GREEN = (152, 250, 130)

pygame.init()

clock = pygame.time.Clock()

sc = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))


def load_image(name, colorkey=None, sz=()):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    image = image.convert_alpha()
    if sz != ():
        image = pygame.transform.scale(image, sz)
    return image


r = 10
R = 20
X = -1
Y = -1
X_cent = 0
Y_cent = 0
x = X_cent - R
y = Y_cent
V = 1
X_fin = 10
Y_fin = 10


class Animal(pygame.sprite.Sprite):
    image = load_image("sheep.png", sz=(50, 50))

    def __init__(self, x, y):
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.X_fin = x
        self.Y_fin = y
        self.v = 1
        self.robot = Robot(0, 0)

    def update(self):
        if self.rect.x > self.X_fin:
            self.rect.x -= self.v
        elif self.rect.x < self.X_fin:
            self.rect.x += self.v

        if self.rect.y > self.Y_fin:
            self.rect.y -= self.v
        elif self.rect.y < self.Y_fin:
            self.rect.y += self.v

    def move(self, pose):
        self.X_fin = pose[0]
        self.Y_fin = pose[1]

    def allow(self, robot):
        self.robot = robot

    def __repr__(self):
        return '<Animal>'


class Robot(pygame.sprite.Sprite):
    image = load_image("robot.png", sz=(50, 50))

    def __init__(self, x, y, flag=False):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.V = 1
        self.flag = flag
        self.X_home = x
        self.Y_home = y
        self.k = 0
        self.R = 100
        self.X = -1
        self.Y = -1

    def update(self, anim=None):
        try:
            if self.k == 1:
                if self.rect.x > anim.rect.x:
                    self.rect.x -= self.V
                elif self.rect.x < anim.rect.x:
                    self.rect.x += self.V

                if self.rect.y > anim.rect.y:
                    self.rect.y -= self.V
                elif self.rect.y < anim.rect.y:
                    self.rect.y += self.V
            elif self.k == 2:
                new_y = self.rect.y - anim.rect.y
                new_x = self.rect.x - anim.rect.x
                if self.X == -1 and self.Y == -1:
                    if new_y < self.R:
                        new_y += self.V
                        new_x = int((self.R * self.R - new_y * new_y) ** 0.5) * (-1)
                    else:
                        self.X = 1
                if self.X == 1 and self.Y == -1:
                    if new_x < R:
                        new_x += self.V
                        new_y = int((self.R * self.R - new_x * new_x) ** 0.5)
                    else:
                        self.Y = 1
                if self.X == 1 and self.Y == 1:
                    if new_y > 0:
                        new_y -= self.V
                        new_x = int((self.R * self.R - new_y * new_y) ** 0.5)
                    else:
                        self.X = -1
                if self.X == -1 and self.Y == 1:
                    if new_x > 0:
                        new_x -= self.V
                        new_y = int((self.R * self.R - new_x * new_x) ** 0.5) * (-1)
                    else:
                        self.Y = -1
                self.rect.x = anim.rect.x + new_x
                self.rect.y = anim.rect.y + new_y
                if anim.rect.x < anim.X_fin:
                    anim.rect.x += anim.v
                    self.rect.x += anim.v
                elif anim.rect.x > anim.X_fin:
                    anim.rect.x -= anim.v
                    self.rect.x -= anim.v
                if anim.rect.y < anim.Y_fin:
                    anim.rect.y += anim.v
                    self.rect.y += anim.v
                elif anim.rect.y > anim.Y_fin:
                    anim.rect.y -= anim.v
                    self.rect.y -= anim.v
            elif self.k == 3:
                if self.rect.x > self.X_home:
                    self.rect.x -= self.V
                elif self.rect.x < self.X_home:
                    self.rect.x += self.V

                if self.rect.y > self.Y_home:
                    self.rect.y -= self.V
                elif self.rect.y < self.Y_home:
                    self.rect.y += self.V
            else:
                self.rect = self.rect
        except Exception as e:
            pass

    def move(self, x, y):
        self.update(x, y)

    def __repr__(self):
        return '<Robot {}, {}>'.format(self.X_home, self.Y_home)

    def check(self, an):
        return self.near(an) <= self.R + 10

    def home(self):
        return self.rect.x == self.X_home and self.rect.y == self.Y_home

    def near(self, an):
        x = abs(an.rect.x - self.rect.x + 25)
        y = abs(an.rect.y - self.rect.y + 25)
        r = int((x * x + y * y) ** 0.5)
        return r


class GroupRobot(pygame.sprite.Group):
    def move(self, an):
        for i in self.sprites():
            if i.check(an):
                if i != an.robot:
                    an.allow(i)
                    i.k = 1
                    an.robot.k = 3
                    self.change(i, an.robot.k)
                    i.update(an)
                    an.allow(i)
                    break
                else:
                    if i.near(an) <= i.R + 10:
                        i.k = 2
                    else:
                        i.k = 1
                    i.update(an)
            else:
                i.update(an)

    def change(self, one, an):
        for i in self.sprites():
            if i != one and i != an:
                if i.home():
                    i.k = 0
                else:
                    i.k = 3


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, name, g, sz):
        super().__init__(g)
        self.image = load_image(name, sz=(sz, sz))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect = self.rect

    def process_event(self, event):
        if self.rect.collidepoint(event.pos):
            return True


def start():
    intro_text = ["", "",
                  "ПРАВИЛА ИГРЫ:",
                  "Действия игры происходят на тренировочном поле,",
                  "на котором нашем роботам предстоит следить за овцами.",
                  "Вам предстоит побыть на месте овец (здесь для условности изображена 1 овца)",
                  "и выбирать куда пастись",
                  "ВЫ можете нажимать ЛКМ или ПКМ по полю и туда направятся овцы",
                  "за овцами будет наблюдать ройвой интеллект и не упускать из виду.",
                  "Данная игра показывает имитацию роевого интеллекта в сель/хозе."]

    fon = pygame.transform.scale(load_image('fon.png'), (WIN_WIDTH, WIN_HEIGHT))
    sc.blit(fon, (0, 0))
    name_font = pygame.font.Font(None, 60)
    font = pygame.font.Font(None, 30)
    text_coord = 150
    string_rendered = name_font.render("SheepRobot", 1, pygame.Color('black'))
    intro_rect = string_rendered.get_rect()
    text_coord += 15
    intro_rect.top = text_coord
    intro_rect.x = 400
    text_coord += intro_rect.height
    sc.blit(string_rendered, intro_rect)
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 15
        intro_rect.top = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        sc.blit(string_rendered, intro_rect)
    btn_group_start = pygame.sprite.Group()
    btn_1 = Button(400, 700, "start.png", btn_group_start, 200)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_1.process_event(event):
                    return 1
            pygame.mouse.set_visible(True)
        btn_group_start.update()
        btn_group_start.draw(sc)
        pygame.display.flip()
        clock.tick(FPS)


def play():
    gr = GroupRobot()
    an = Animal(400, 400)
    b = pygame.sprite.Group()
    mm = []
    for i in range(4):
        for j in range(4):
            gr.add(Robot(i * 250 + 125, j * 250 + 125))
    # gr.add(Robot(705, 400))
    btn = Button(0, 0, "finish.png", b, 50)
    playing = True
    while playing:
        sc.fill(GREEN)

        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                exit()
            if i.type == pygame.MOUSEBUTTONDOWN:
                an.move(i.pos)
            if i.type == pygame.MOUSEBUTTONDOWN:
                if btn.process_event(i):
                    playing = False
        gr.draw(sc)
        b.draw(sc)
        b.update()
        sc.blit(an.image, an.rect)
        pygame.display.flip()
        clock.tick(FPS)

        gr.move(an)
        an.update()


while 1:
    sc.fill(WHITE)

    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            exit()
    k = start()
    if k:
        play()
