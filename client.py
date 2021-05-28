# ----NECESSITIES----
NAME = "Saad"
TEAM = None

# ---CODE-----
from pygame.locals import *

from classes import *
from network import Network

pygame.init()

screen = pygame.display.set_mode((screenX, screenY))
pygame.display.set_caption(NAME)
# bullets
# bulets order - pos(tuple), angle(in radians)
# Note : 'transform.rotate uses angle in degrees'
bullet_image = pygame.image.load("bullet.png")
bullets = []
_bullet = None

# bombs
bombs = []
bomb_rect=[]
_bomb = None

# players
players = []

# myself
n = Network()
me = n.get_player()
me.name = NAME
me.gun = gun["m249"]()
movex = movey = 0

# environments
environments = n.recv()
players_images = n.recv()

for key in players_images.keys():
    players_images[key] = pygame.image.load(players_images[key])
me.rect = players_images[me.image_key].get_rect()
me.rect.topleft = me.pos

# Camera
camera = pygame.Rect(*me.pos, screenX, screenY)
cx, cy = camera.center
cam_speed = 80
rmain = pygame.Rect(0, 0, screenX, screenY)
zoom_scaler = Scale((200,20),100,20)
ZOOMFACTOR = zoom_scaler.level

while True:
    screen.fill((255, 255, 255))
    ZOOMFACTOR = zoom_scaler.level / 10
    zoom_scaler.show(screen)

    # Drawing stuffs
    ox = -camera.centerx + (screenX / 2)*ZOOMFACTOR
    oy = -camera.centery + (screenY / 2)*ZOOMFACTOR

    #Showing everything on screen according to camera
    for env in environments:
        pygame.draw.rect(screen, GREEN, resize_rect(env.rect.move(ox, oy), ZOOMFACTOR))
    for p in players:
        rotatedImage = pygame.transform.rotate(pygame.transform.scale(players_images[p.image_key],(int(64/ZOOMFACTOR),int(64/ZOOMFACTOR))), p.angle)
        screen.blit(rotatedImage, resize_rect(p.rect.move(ox, oy), ZOOMFACTOR).topleft)
    for rect,angle in bullets:
        rotatedImage = pygame.transform.rotate(pygame.transform.scale(bullet_image,(int(16/ZOOMFACTOR),int(16/ZOOMFACTOR))), math.degrees(angle))
        screen.blit(rotatedImage, resize_rect(rect.move(ox, oy), ZOOMFACTOR).topleft)
    for rect,radius in bombs:
        pygame.draw.circle(screen, (0, 0, 200), resize_rect(rect.move(ox, oy), ZOOMFACTOR).topleft, math.ceil(radius/ZOOMFACTOR))
    for rect in bomb_rect:
        pygame.draw.rect(screen, (200, 200, 0), resize_rect(rect.move(ox, oy), ZOOMFACTOR))


    if pygame.mouse.get_pressed()[1]:
            if not scrolling:
                pygame.mouse.get_rel()
                scrolling = True
            else:
                dx, dy = pygame.mouse.get_rel()
                camera.centerx -= dx
                camera.centery -= dy


    else:
            scrolling = False
            if camera.centerx < me.rect.centerx:
                camera.centerx += (me.rect.centerx - camera.centerx) / 1000 * cam_speed
            elif camera.centerx > me.rect.centerx:
                camera.centerx -= -(me.rect.centerx - camera.centerx) / 1000 * cam_speed
            if camera.centery < me.rect.centery:
                camera.centery += (me.rect.centery - camera.centery) / 1000 * cam_speed
            elif camera.centery > me.rect.centery:
                camera.centery -= -(me.rect.centery - camera.centery) / 1000 * cam_speed

    # DATA IN AND OUT
    players, bullets, bombs, bomb_rect = n.send([me, _bullet, _bomb])

    # data reset
    _bullet = None
    _bomb = None

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == KEYDOWN:
            if event.key == K_UP:
                movey = -1
            elif event.key == K_DOWN:
                movey = 1
            if event.key == K_RIGHT:
                movex = 1
            elif event.key == K_LEFT:
                movex = -1
            if event.key == K_SPACE:
                _bullet = (me.rect.center, me.angle, me.gun.damage, TEAM if TEAM else NAME)
            if event.key == K_KP0:
                _bomb = (me.rect.center, me.angle, NAME)
        if event.type == KEYUP:
            if event.key == K_UP:
                movey = 0
            elif event.key == K_DOWN:
                movey = 0
            if event.key == K_RIGHT:
                movex = 0
            elif event.key == K_LEFT:
                movex = 0
        if event.type == MOUSEBUTTONDOWN:
                _bullet = (me.rect.center, me.angle, me.gun.damage, TEAM if TEAM else NAME)
        if event.type == MOUSEMOTION:
                rect = resize_rect(me.rect.move(ox, oy), ZOOMFACTOR)
                x = event.pos[0] - rect.centerx
                y = event.pos[1] - rect.centery

                if y == 0:
                    y = 0.000001
                if x == 0:
                    x = 0.000001

                me.angle = -math.degrees(math.atan(y / x)) + 90
                if x > 0:
                    me.angle += 180




    # collision for player and env
    if movex or movey:
        temp_movex,temp_movey = movex,movey
        for env in environments:
            if env.rect.collidepoint(me.rect.centerx, me.rect.top):
                if temp_movey < 0:
                    temp_movey = 0
            elif env.rect.collidepoint(me.rect.centerx, me.rect.bottom):
                if temp_movey > 0:
                    temp_movey = 0
            elif env.rect.collidepoint(me.rect.left, me.rect.centery):
                if temp_movex<0:
                    temp_movex=0
            elif env.rect.collidepoint(me.rect.right, me.rect.centery):
                if temp_movex>0:
                    temp_movex = 0

        me.updateMove(temp_movex, temp_movey)

    pygame.display.update()
