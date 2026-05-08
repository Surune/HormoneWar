import random
import sys

import pygame

import constant as c
import image
import Mover as m

pygame.init()
pygame.key.set_repeat(True, True)
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((c.WINWIDTH, c.WINHEIGHT), pygame.FULLSCREEN)
fps_clock = pygame.time.Clock()

menubgm = pygame.mixer.Sound("menusong.wav")
gamebgm = pygame.mixer.Sound("gamesong.m4a")
endbgm = pygame.mixer.Sound("ending.m4a")

tile_rect = image.tile_green.get_rect()
TILEWIDTH = c.WINWIDTH // tile_rect.width
TILEHEIGHT = c.WINHEIGHT // tile_rect.height
WIDTH = tile_rect.width * TILEWIDTH
HEIGHT = tile_rect.height * TILEHEIGHT
HEART_WIDTH = image.heart.get_rect().width

image.menu = pygame.transform.scale(image.menu, (WIDTH, HEIGHT))


def text(string, x, y):
    font = pygame.font.Font(None, 24)
    rendered = font.render(string, True, c.WHITE)
    text_rect = rendered.get_rect()
    text_rect.center = (x, y)
    screen.blit(rendered, text_rect)


def draw_tiles():
    for temp_width in range(TILEWIDTH):
        for temp_height in range(TILEHEIGHT):
            screen.blit(image.tile_green, (temp_width * tile_rect.width, temp_height * tile_rect.height))


class HormoneSystem:
    def __init__(self, player, buff_rect):
        self.player = player
        self.buff_rect = buff_rect
        self.cooldown = 0
        self.hormonenum = 0
        self.position = (0, 0)
        self.current_hormone = c.HORMONE[0]
        self.roll_next_hormone()

    def roll_next_hormone(self):
        self.hormonenum = random.randint(0, 9)
        self.position = (random.randint(15, WIDTH - 40), random.randint(15, HEIGHT - 40))
        self.current_hormone = c.HORMONE[self.hormonenum]

    def update_spawn(self, player_rect):
        self.cooldown += 1
        if self.cooldown < c.HORMONETIME:
            return

        hormone_rect = image.hormone[self.hormonenum].get_rect()
        hormone_rect.center = self.position
        screen.blit(image.hormone[self.hormonenum], self.position)
        if player_rect.colliderect(hormone_rect):
            self.apply_to_player()

    def apply_to_player(self):
        self.player.hormonelist.append([self.hormonenum, c.HORMONELAST])
        self.player.damage += self.current_hormone[1]
        self.player.speed += self.current_hormone[2]
        self.player.shotspeed += self.current_hormone[3]
        self.player.life += self.current_hormone[4]
        self.cooldown = 0
        self.roll_next_hormone()

    def update_effects(self):
        if not self.player.hormonelist:
            return

        for hormone in self.player.hormonelist:
            hormone[1] -= 1
        self.remove_expired_hormone()
        if self.player.hormonelist:
            self.draw_effect_ui()

    def remove_expired_hormone(self):
        if self.player.hormonelist[0][1] != 0:
            return

        expired_hormone = self.player.hormonelist.pop(0)
        self.player.damage -= c.HORMONE[expired_hormone[0]][1]
        self.player.speed -= c.HORMONE[expired_hormone[0]][2]
        self.player.shotspeed -= c.HORMONE[expired_hormone[0]][3]

    def draw_effect_ui(self):
        remain_ratio = self.player.hormonelist[-1][1] / c.HORMONELAST
        pygame.draw.rect(
            screen,
            c.RED,
            (self.player.xpos - 20, self.player.ypos - 30, int(40 * remain_ratio), 3),
        )
        text(self.current_hormone[0], self.player.xpos, self.player.ypos - 45)

    def draw_buff(self):
        if not self.player.hormonelist:
            return
        self.buff_rect.center = (self.player.xpos, self.player.ypos)
        screen.blit(image.buff, self.buff_rect)


class BattleScene:
    def __init__(self):
        self.running = True
        self.endset = 0
        self.healthrange = 5
        self.player = m.Player()
        self.enemy = m.Enemy()
        self.mouseimg_rect = image.mouseimg.get_rect()
        self.buff_rect = image.buff.get_rect()
        self.hormones = HormoneSystem(self.player, self.buff_rect)

    def get_actor_rect(self, sprite, xpos, ypos):
        actor_rect = sprite.get_rect()
        actor_rect.center = (xpos, ypos)
        return actor_rect

    def get_player_rect(self):
        return self.get_actor_rect(self.player.nowplayer, self.player.xpos, self.player.ypos)

    def get_enemy_rect(self):
        return self.get_actor_rect(self.enemy.image, self.enemy.xpos, self.enemy.ypos)

    def draw_mouse_cursor(self):
        mousepos = pygame.mouse.get_pos()
        self.mouseimg_rect.center = mousepos
        screen.blit(image.mouseimg, self.mouseimg_rect)
        return mousepos

    def handle_events(self, mousepos):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.handle_keydown()
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.player.shotcool <= 0 and not self.player.charging:
                    self.player.charging = True
                continue
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.player.charging:
                    self.player.create_shot(mousepos)

    def handle_keydown(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.running = False
            return
        if keys[pygame.K_a]:
            self.player.move_left(WIDTH)
        if keys[pygame.K_d]:
            self.player.move_right(WIDTH)
        if keys[pygame.K_w]:
            self.player.move_up(HEIGHT)
        if keys[pygame.K_s]:
            self.player.move_down(HEIGHT)

    def draw_player_life(self):
        for heart_index in range(self.player.life):
            xpos = 20 + 3 * (heart_index + 1) + HEART_WIDTH * heart_index
            screen.blit(image.heart, (xpos, 20))

    def update_end_state(self):
        if self.player.life == 0:
            self.running = False
            self.endset = 1
            return
        if self.enemy.health <= 0:
            self.running = False
            self.endset = 2

    def draw_player(self, player_rect):
        if self.player.invisible and self.player.invisiblecool % 2 == 0:
            screen.blit(self.player.nowplayer, player_rect)
            return
        if not self.player.invisible:
            screen.blit(self.player.nowplayer, player_rect)

    def draw_enemy(self):
        enemy_rect = self.get_enemy_rect()
        screen.blit(self.enemy.image, enemy_rect)

    def draw_enemy_healthbar(self):
        pygame.draw.rect(screen, c.WHITE, (self.enemy.xpos - 70, self.enemy.ypos - 40, 140, 7))
        current_width = int(0.1 * (self.enemy.health - (1400 * self.healthrange)))
        pygame.draw.rect(screen, c.COLOR[self.healthrange], (self.enemy.xpos - 70, self.enemy.ypos - 40, current_width, 7))
        if current_width <= 0:
            self.healthrange -= 1
            self.enemy.smaller()

    def update_world(self, mousepos):
        self.player.update()
        self.handle_events(mousepos)

        player_rect = self.get_player_rect()
        enemy_rect = self.get_enemy_rect()

        self.hormones.update_spawn(player_rect)
        self.hormones.update_effects()
        if not self.running:
            return player_rect

        self.player.update_shots(enemy_rect, WIDTH, HEIGHT, screen, self.enemy)
        self.enemy.update_attack(self.player, WIDTH, HEIGHT)
        player_rect = self.get_player_rect()
        self.enemy.update_shots(self.player, player_rect, WIDTH, HEIGHT, screen)
        self.update_end_state()
        return self.get_player_rect()

    def draw_world(self, player_rect):
        self.draw_player_life()
        self.draw_player(player_rect)
        self.hormones.draw_buff()
        self.draw_enemy()
        self.draw_enemy_healthbar()

    def run(self):
        menubgm.stop()
        gamebgm.play()
        while self.running:
            screen.fill(c.BACKGROUNDCOLOR)
            draw_tiles()
            mousepos = self.draw_mouse_cursor()
            player_rect = self.update_world(mousepos)
            if not self.running:
                break
            self.draw_world(player_rect)
            fps_clock.tick(c.FPS)
            pygame.display.flip()
        return self.endset


def show_menu():
    selected = False
    menubgm.play()
    while not selected:
        screen.fill(c.BACKGROUNDCOLOR)
        screen.blit(image.menu, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                selected = True
        pygame.display.flip()


def show_mission():
    missioning = 50
    while missioning:
        screen.fill(c.BACKGROUNDCOLOR)
        screen.blit(image.mission, (0, 0))
        missioning -= 1
        pygame.display.flip()


def show_ending(endset):
    screen.fill(c.BACKGROUNDCOLOR)
    gamebgm.stop()
    endbgm.play()
    if endset == 1:
        screen.blit(image.gameover, (0, 0))
    elif endset == 2:
        screen.blit(image.youwin, (0, 0))
    pygame.display.flip()

    ending = True
    while ending:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                ending = False
    return ending


show_menu()
show_mission()
scene = BattleScene()
endset = scene.run()
ending = show_ending(endset)

if not scene.running and not ending:
    pygame.quit()
    sys.exit()
