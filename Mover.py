import math
import random as r

import pygame

import constant as c
import image as i


SHOT_LEVEL = 0
SHOT_X = 1
SHOT_Y = 2
SHOT_THETA = 3

BULLET_X = 1
BULLET_Y = 2
BULLET_THETA = 3
BULLET_PATTERN = 4


class Player:
    def __init__(self):
        self.speed = c.MAXSPEED
        self.damage = 15
        self.life = 5
        self.xpos = c.WINWIDTH // 2
        self.ypos = c.WINHEIGHT // 2
        self.shotcool = 0
        self.shotspeed = 10
        self.shotposlist = []
        self.charging = False
        self.chargingtime = 0
        self.nowplayer = i.standing_right
        self.direction = "right"
        self.index = 0
        self.invisible = False
        self.invisiblecool = 0
        self.hormonelist = []
        self.shotimg = i.shotimg[0]
        self.chargelevel = 0

    def nextpic(self):
        self.index = (self.index + 1) % len(i.run_right)
        if self.direction == "right":
            self.nowplayer = i.run_right[self.index]
            return
        self.nowplayer = i.run_left[self.index]

    def move_left(self, width):
        self.direction = "left"
        self.nextpic()
        self.move_within_bounds("xpos", -self.speed, 10, width - 15)

    def move_right(self, width):
        self.direction = "right"
        self.nextpic()
        self.move_within_bounds("xpos", self.speed, 10, width - 15)

    def move_up(self, height):
        self.move_within_bounds("ypos", -self.speed, 10, height - 15)

    def move_down(self, height):
        self.move_within_bounds("ypos", self.speed, 10, height - 15)

    def move_within_bounds(self, axis, delta, minimum, maximum):
        position = getattr(self, axis) + delta
        if minimum <= position <= maximum:
            setattr(self, axis, position)

    def update(self):
        self.shotcool -= 1
        self.invisiblecool -= 1
        if self.invisiblecool <= 0:
            self.invisible = False
        if self.charging:
            self.update_charge()
            return
        self.update_idle_sprite()

    def update_idle_sprite(self):
        if self.direction == "left":
            self.nowplayer = i.standing_left
            return
        self.nowplayer = i.standing_right

    def update_charge(self):
        self.chargingtime += 1
        self.speed = 0
        self.chargelevel = min(self.chargingtime // c.CHARGETERM, 3)
        self.shotimg = i.shotimg[self.chargelevel]
        if self.direction == "left":
            self.nowplayer = i.charge_left[self.chargelevel]
            return
        self.nowplayer = i.charge_right[self.chargelevel]

    def reset_charge(self):
        self.speed = c.MAXSPEED
        self.charging = False
        self.chargingtime = 0
        self.shotcool = c.SHOTGAP

    def create_shot(self, mousepos):
        theta = math.pi / 2 - math.atan2(mousepos[1] - self.ypos + 5, mousepos[0] - self.xpos - 10)
        self.shotposlist.append([self.chargelevel, self.xpos - 10, self.ypos + 5, theta])
        self.reset_charge()

    def update_shots(self, monster_rect, width, height, screen, enemy):
        active_shots = []
        for shot in self.shotposlist:
            self.advance_shot(shot)
            if self.is_out_of_bounds(shot[SHOT_X], shot[SHOT_Y], width, height):
                continue
            if monster_rect.collidepoint(shot[SHOT_X], shot[SHOT_Y]):
                enemy.health -= self.damage
                continue
            rotated_image = pygame.transform.rotate(i.shotimg[shot[SHOT_LEVEL]], 90 + int(math.degrees(shot[SHOT_THETA])))
            screen.blit(rotated_image, (shot[SHOT_X], shot[SHOT_Y]))
            active_shots.append(shot)
        self.shotposlist = active_shots

    def advance_shot(self, shot):
        shot[SHOT_X] += self.shotspeed * math.sin(shot[SHOT_THETA])
        shot[SHOT_Y] += self.shotspeed * math.cos(shot[SHOT_THETA])

    def is_out_of_bounds(self, xpos, ypos, width, height):
        return xpos < 0 or ypos < 0 or xpos > width or ypos > height


class Enemy:
    def __init__(self):
        self.health = c.MAXHEALTH
        self.xpos = r.randint(25, c.WINWIDTH - 60)
        self.ypos = r.randint(25, c.WINHEIGHT - 60)
        self.level = 4
        self.bullet = []
        self.i = 0
        self.temp_theta = 0
        self.shotspeed = 19
        self.image = i.mob
        self.shot = i.mob_shot
        self.choice = r.randint(1, self.level)
        self.time = 0
        self.attack_frame = 0
        self.pattern_frame = 0

    def smaller(self):
        width, height = self.image.get_size()
        scaled_size = (int(width * c.SCALE_X * 0.8), int(height * c.SCALE_Y * 0.8))
        self.image = pygame.transform.scale(self.image, scaled_size)

    def shot_1(self):
        for _ in range(15):
            theta = math.pi * 5 * self.i / 360 + r.random() / 9
            temp_x = r.randint(-5, 5)
            temp_y = r.randint(5, 5)
            self.bullet.append([0, self.xpos + temp_x, self.ypos + temp_y, theta, 1])
            self.i += 30

    def shot_2(self):
        for _ in range(15):
            theta = r.random() / 3
            temp_x = r.randint(-25, 25)
            temp_y = r.randint(-25, 25)
            self.bullet.append([0, self.xpos + temp_x, self.ypos + temp_y, self.temp_theta + theta, 2])
            self.temp_theta += 1.256

    def shot_3(self, player):
        theta = math.atan2(player.xpos - self.xpos, player.ypos - self.ypos)
        for _ in range(16):
            self.bullet.append([0, self.xpos, self.ypos, theta, 3])
            theta += math.pi / 8

    def shot_4(self, player):
        dx = 0
        dy = -50
        for _ in range(10):
            dx += 3
            dy += 9
            theta = math.atan2(player.xpos - self.xpos - dx, player.ypos - self.ypos - dy)
            self.bullet.append([0, self.xpos + dx, self.ypos + dy, theta, 4])
        for _ in range(10):
            dx -= 8
            dy -= 5.6
            theta = math.atan2(player.xpos - self.xpos - dx, player.ypos - self.ypos - dy)
            self.bullet.append([0, self.xpos + dx, int(self.ypos + dy), theta, 4])
        for _ in range(10):
            dx += 9.9
            theta = math.atan2(player.xpos - self.xpos - dx, player.ypos - self.ypos - dy)
            self.bullet.append([0, self.xpos + dx, int(self.ypos + dy), theta, 4])
        for _ in range(10):
            dx -= 8
            dy += 5.6
            theta = math.atan2(player.xpos - self.xpos - dx, player.ypos - self.ypos - dy)
            self.bullet.append([0, self.xpos + dx, int(self.ypos + dy), theta, 4])
        for _ in range(10):
            dx += 3
            dy -= 9
            theta = math.atan2(player.xpos - self.xpos - dx, player.ypos - self.ypos - dy)
            self.bullet.append([0, self.xpos + dx, self.ypos + dy, theta, 4])

    def update_attack(self, player, width, height):
        self.attack_frame += 1
        if self.attack_frame < 30:
            self.image = i.mob
            return
        if self.attack_frame == 30:
            self.image = i.mob_ready if self.choice == 5 else i.mob_charge
            return
        if self.attack_frame < 35:
            return

        self.image = i.mob_shoot
        if self.choice == 1:
            self.update_pattern_1()
            return
        if self.choice == 2:
            self.update_pattern_2(player)
            return
        if self.choice == 3:
            self.update_pattern_3(player)
            return
        if self.choice == 4:
            self.update_pattern_4(player)
            return
        self.teleport(width, height)

    def update_pattern_1(self):
        self.pattern_frame += 1
        if self.pattern_frame in (1, 2, 3, 4, 5, 14, 15, 16, 17, 18, 27, 28, 29, 30, 31):
            self.shot_1()
            return
        if self.pattern_frame > 31:
            self.reset_attack_cycle()

    def update_pattern_2(self, player):
        self.pattern_frame += 1
        if self.pattern_frame in (1, 2, 3, 4, 8, 9, 10, 14, 15, 16, 20, 21, 22):
            self.shot_2()
            return
        if self.pattern_frame in (5, 6, 11, 12, 17, 18):
            self.temp_theta = math.atan2(player.xpos - self.xpos, player.ypos - self.ypos)
            return
        self.temp_theta = 0
        self.reset_attack_cycle()

    def update_pattern_3(self, player):
        self.pattern_frame += 1
        if self.pattern_frame < 90:
            if self.pattern_frame % 3 == 0:
                self.shot_3(player)
            return
        self.reset_attack_cycle()

    def update_pattern_4(self, player):
        self.pattern_frame += 1
        if self.pattern_frame <= 49:
            if self.pattern_frame % 7 == 0:
                self.shot_4(player)
            return
        self.reset_attack_cycle()

    def teleport(self, width, height):
        self.image = i.mob_telpo
        self.attack_frame = 0
        self.pattern_frame = 0
        self.choice = r.randint(1, self.level)
        self.xpos = r.randint(20, width - 50)
        self.ypos = r.randint(20, height - 50)

    def reset_attack_cycle(self):
        self.image = i.mob
        self.attack_frame = 0
        self.pattern_frame = 0
        self.choice = 5

    def update_shots(self, player, player_rect, width, height, screen):
        active_enemy_shots = []
        for enemyshot in self.bullet:
            if enemyshot[BULLET_PATTERN] == 4 and self.time < 600:
                self.time += 1
                active_enemy_shots.append(enemyshot)
                continue
            self.advance_bullet(enemyshot)
            if self.is_out_of_bounds(enemyshot, width, height):
                continue
            if player_rect.collidepoint((enemyshot[BULLET_X], enemyshot[BULLET_Y])) and not player.invisible:
                player.invisible = True
                player.invisiblecool = c.INVISIBLETIME
                player.life -= 1
                continue
            screen.blit(self.shot, (enemyshot[BULLET_X], enemyshot[BULLET_Y]))
            active_enemy_shots.append(enemyshot)
        self.bullet = active_enemy_shots

    def advance_bullet(self, enemyshot):
        enemyshot[BULLET_X] += self.shotspeed * math.sin(enemyshot[BULLET_THETA])
        enemyshot[BULLET_Y] += self.shotspeed * math.cos(enemyshot[BULLET_THETA])

    def is_out_of_bounds(self, enemyshot, width, height):
        return (
            enemyshot[BULLET_X] < 0
            or enemyshot[BULLET_Y] < 0
            or enemyshot[BULLET_X] > width
            or enemyshot[BULLET_Y] > height
        )
