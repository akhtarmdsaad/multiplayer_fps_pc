from functools import partial

import math
import pygame
import time
pygame.init()
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
screenX = 700
screenY = 700

def resize_rect(rectangle,FACTOR):
    if FACTOR<=0:return rectangle
    rect=rectangle.copy()
    rect.width/=FACTOR
    rect.height/=FACTOR
    rect.left/=FACTOR
    rect.top/=FACTOR
    return rect

class Environment:

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)

    def show(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)

    def showrect(self, screen, ox, oy):
        pygame.draw.rect(screen, GREEN, self.rect.move(ox, oy))

    def show_min_rect(self, screen, ox, oy, px, py):
        factor = 10
        rect = self.rect.copy()
        rect.width /= factor
        rect.height /= factor
        rect.left /= factor
        rect.top /= factor
        rect.left += px
        rect.top += py
        pygame.draw.rect(screen, GREEN, rect.move(ox, oy))

class Envx(Environment):
    def __init__(self, x, y, length):
        super().__init__(x, y, length, 20)
class Envy(Environment):
    def __init__(self, x, y, height):
        super().__init__(x, y, 20, height)

class Scale:

    def __init__(self, pos, max_level,min = 0):
        self.min = min
        self.max = max_level
        self.pos = pos
        self.level = min
        self.factor = 1
        self.font = pygame.font.Font(pygame.font.get_default_font(), 20)
        self.rectangle = pygame.Rect(*self.pos, self.max + 15 - self.min, 40)

    def write(self, screen, pos, text, color):
        text = str(text)
        screen.blit(self.font.render(text, True, color), pos)

    def show(self, screen):
        length = 100
        width = 40
        pygame.draw.rect(screen, (0, 0, 0), (*self.pos, length, width), 3)
        pygame.draw.line(screen, (200, 0, 0), (self.pos[0] + 5, self.pos[1] + width // 2),
                         [self.pos[0] + length - 5, self.pos[1] + width // 2])
        pygame.draw.circle(screen, (255, 0, 0), (self.pos[0] + 5 + length//self.max*self.level, self.pos[1] + width // 2), 7)
        self.write(screen, (self.pos[0] - 15 - 10 * len(str(self.level)), self.pos[1] + 5), self.level, (0, 0, 0))

        if pygame.mouse.get_pressed()[0] == 1 and self.rectangle.collidepoint(*pygame.mouse.get_pos()):
            self.level = (pygame.mouse.get_pos()[0] - self.pos[0])*self.max//length
            if self.level < self.min:
                self.level = self.min
            elif self.level > self.max:
                self.level = self.max


class Player:

    def __init__(self, pos):
        self.pos = list(pos)
        self.rect = pygame.Rect(*pos, 20, 20)
        self.st = time.time()
        self.angle = 0
        self.gun = Gun(5, 0.05, max=50)
        self.bomb_thrown = False
        self.health = 100
        self.lives = 3
        self.deaths = 0
        self.speed = 3
        self.image_key = None
        self.lost = False

    def __str__(self):
        return f"{self.angle}"

    def show(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)

    # pygame.

    def showrect(self, screen, image, ox, oy):
        rotatedImage = pygame.transform.rotate(image, self.angle)
        screen.blit(rotatedImage, self.rect.move(ox, oy).topleft)

    def hit(self, damage):
        self.health -= damage

    def show_min_rect(self, screen, ox, oy, px, py):
        factor = 10
        rect = self.rect.copy()
        rect.width /= factor
        rect.height /= factor
        rect.left /= factor
        rect.top /= factor
        rect.left += px
        rect.top += py
        pygame.draw.rect(screen, (0, 0, 200), rect)

    # screen.blit(self.rotatedImage,rect.move(ox,oy).topleft)

    def updateMove(self, dx, dy):
        self.rect.left += dx*self.speed
        self.rect.top += dy*self.speed
        self.pos = list(self.rect.topleft)

    def fire(self,name):
        if time.time() - self.st > 0.2 and self.gun.available_bullets:
            return self.gun.fire(self.rect.center, self.angle, name)

    def reset(self, died=True):
        # return	#uncomment in developer mode
        print("You got knocked out")
        self.pos = [100, 50]
        self.rect.topleft = self.pos
        if died:
            self.lives -= 1
            self.deaths += 1
        self.health = 100
        self.gun.available_bullets = self.gun.max_bullets


class Bomb:

    def __init__(self, pos, angle, name):
        self.pos = list(pos)
        self.angle = math.radians(angle)
        self.thrownBy = name
        self.radius = 5
        self.bombDistance = 800
        self.st = time.time()
        self.max_living_time = 4  #secs
        self.blastlength = self.bombDistance // 2
        self.to_reach = [self.pos[0] - self.bombDistance * math.sin(self.angle),
                         self.pos[1] - self.bombDistance * math.cos(self.angle)]
        self.blast = False
        self.diffx = self.to_reach[0] - self.pos[0]
        self.diffy = self.to_reach[1] - self.pos[1]
        self.blastTime = 0.5
        self.rect = pygame.Rect(*self.pos, 10, 10)

    def show(self, screen):
        pygame.draw.circle(screen, (0, 0, 200), self.rect.topleft, self.radius)

    def showrect(self, screen, ox, oy):
        pygame.draw.circle(screen, (0, 0, 200), self.rect.move(ox, oy).topleft, self.radius)

    def show_min_rect(self, screen, ox, oy, px, py):
        factor = 10
        rect = self.rect.copy()
        rect.width /= factor
        rect.height /= factor
        rect.left /= factor
        rect.top /= factor
        rect.left += px
        rect.top += py
        pygame.draw.circle(screen, (0, 0, 200), rect.move(ox, oy).topleft, self.radius / factor)

    def fire(self):
        self.diffx = self.to_reach[0] - self.pos[0]
        self.diffy = self.to_reach[1] - self.pos[1]
        self.pos[0] += self.diffx / 100
        self.pos[1] += self.diffy / 100
        self.rect.topleft = self.pos

class BombRect:
    def __init__(self,rect):
        self.rect = pygame.Rect(*rect.topleft,rect.width*30,rect.width*30)
        self.rect.center = rect.topleft
        # self.rect.width*=30
        # self.rect.height*=30
        self.st = time.time()
        self.max_living_time = 0.5  #secs

class Bullet:
    def __init__(self, pos, angle, damage, pehchan=''):
        super().__init__()
        self.pehchan = pehchan
        self.pos = pos
        self.speed = 5
        self.angle = math.radians(angle)
        assert type(damage) == type(5), "Damage should be integer"
        self.damage = damage
        self.rect = pygame.Rect(*pos, 5, 5)

    def fire(self):
        x, y = self.pos
        x -= self.speed * math.sin(self.angle)
        y -= self.speed * math.cos(self.angle)
        self.rect.topleft = (x, y)
        self.pos = [x, y]

    # self.show(screen)

    def show(self, screen, image):
        rotatedImage = pygame.transform.rotate(image, math.degrees(self.angle))
        screen.blit(rotatedImage, self.rect.topleft)

    def show_min_rect(self, screen, ox, oy, px, py):
        return
        rect = self.rect.copy()
        rect.width /= factor
        rect.height /= factor
        rect.left /= factor
        rect.top /= factor
        rect.left += px
        rect.top += py
        pygame.draw.rect(screen, GREEN, rect.move(ox, oy))

class Gun:
    def __init__(self, damage, _time, max=30, rd=1, name=''):
        self.damage = damage
        self.fire_time = _time
        self.max_bullets = max
        self.available_bullets = self.max_bullets
        self.st = time.time()
        self.reload_time = rd
        self.reload_st = None
        self.name = name

    def fire(self, pos, angle, pehchan):
        if time.time() - self.st > self.fire_time:
            self.st = time.time()
            self.available_bullets -= 1
            if self.available_bullets <= 0:
                if not self.reload_st:
                    self.reload_st = time.time()
                self.reload()
                return
            return Bullet(pos, angle, self.damage, pehchan)
        return None

    def reload(self, enemy=True):

        if time.time() - self.reload_st > self.reload_time:
            self.available_bullets = self.max_bullets
            self.reload_st = None



def create_gun(a, b, c, d, name):
    return Gun(a, b, c, d, name)


gun = {
    # gun parameters - damage, fire time, total bullets, reload time, name to show
    "m249": partial(create_gun, 10, 0.05, 100, 5, 'm249'),
    "m416": partial(create_gun, 15, 0.1, 30, 1, "m416"),
    "shotgun": partial(create_gun, 100, 1, 2, 2, "shotgun"),
    "m762": partial(create_gun, 20, 0.1, 40, 1, "m762"),
    "slr": partial(create_gun, 30, 0.5, 10, 2, "slr"),
    "2m249": partial(create_gun, 10, 0.001, 500, 20, "2m249"),
    "hand": partial(create_gun, 0, 0, 0, 0, "hand")

}
