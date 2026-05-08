import constant as c
import image as i
import math
import pygame
import random as r

'''플레이어 클래스'''
class Player:
    def __init__(self):
        self.speed = c.MAXSPEED
        self.damage=15
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
        self.invisible=False
        self.invisiblecool=0
        self.hormonelist=[]
        self.shotimg = i.shotimg[0]
        self.chargelevel = 0
    def nextpic(self):
        if (self.index == 3):
            self.index=0
        else:
            self.index+=1

        if self.direction=="right":
            self.nowplayer=i.run_right[self.index]
        elif self.direction=="left":
            self.nowplayer=i.run_left[self.index]
    def move_left(self, width):
        self.direction = "left"
        self.nextpic()
        self.xpos -= self.speed
        if self.xpos < 10 or self.xpos > width - 15:
            self.xpos += self.speed
    def move_right(self, width):
        self.direction = "right"
        self.nextpic()
        self.xpos += self.speed
        if self.xpos < 10 or self.xpos > width - 15:
            self.xpos -= self.speed
    def move_up(self, height):
        self.ypos -= self.speed
        if self.ypos < 10 or self.ypos > height - 15:
            self.ypos += self.speed
    def move_down(self, height):
        self.ypos += self.speed
        if self.ypos < 10 or self.ypos > height - 15:
            self.ypos -= self.speed
    def update(self):
        self.shotcool -= 1
        self.invisiblecool -= 1
        if self.invisiblecool <= 0:
            self.invisible = False
        if self.charging == True:
            self.update_charge()
        elif self.direction == "left":
            self.nowplayer = i.standing_left
        elif self.direction == "right":
            self.nowplayer = i.standing_right
    def update_charge(self):
        self.chargingtime += 1
        self.speed = 0
        self.chargelevel = self.chargingtime // c.CHARGETERM
        if self.chargelevel >= 3:
            self.chargelevel = 3
        self.shotimg = i.shotimg[self.chargelevel]
        if self.direction == "left":
            self.nowplayer = i.charge_left[self.chargelevel]
        elif self.direction == "right":
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
            rotated_shotimg = pygame.transform.rotate(i.shotimg[shot[0]], 90 + int(math.degrees(shot[3])))
            shot[1] += self.shotspeed * math.sin(shot[3])
            shot[2] += self.shotspeed * math.cos(shot[3])
            if shot[1] < 0 or shot[2] < 0 or shot[1] > width or shot[2] > height:
                continue
            elif monster_rect.collidepoint(shot[1], shot[2]):
                enemy.health -= self.damage
                continue
            else:
                screen.blit(rotated_shotimg, (shot[1], shot[2]))
                active_shots.append(shot)
        self.shotposlist = active_shots

'''몬스터 이미지'''
class Enemy:
    def __init__(self):
        self.health=c.MAXHEALTH
        self.xpos= r.randint(25, c.WINWIDTH - 60)
        self.ypos= r.randint(25, c.WINHEIGHT - 60)
        self.level=4
        self.bullet = []
        self.i = 0
        self.temp_theta = 0
        self.shotspeed=19
        self.image=i.mob
        self.shot=i.mob_shot
        self.choice=r.randint(1,self.level)
        self.time=0
        self.attack_frame = 0
        self.pattern_frame = 0
    def smaller(self):
        w, h = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(w * c.SCALE_X*0.8), int(h * c.SCALE_Y*0.8)))
    def shot_1(self):
        for k in range(15):
            theta = math.pi * 5 * self.i / 360
            theta += r.random() / 9
            temp_x = r.randint(-5, 5)
            temp_y = r.randint(5, 5)
            self.bullet.append([0, self.xpos + temp_x, self.ypos + temp_y, theta, 1])
            self.i+=30
    def shot_2(self):
        for i in range(15):
            theta = r.random() / 3
            temp_x = r.randint(-25, 25)
            temp_y = r.randint(-25, 25)
            self.bullet.append([0, self.xpos + temp_x, self.ypos + temp_y, self.temp_theta + theta, 2])
            self.temp_theta += 1.256
    def shot_3(self, pl):
        theta = (math.atan2(pl.xpos - self.xpos, pl.ypos - self.ypos))
        for i in range(16):
            self.bullet.append([0, self.xpos, self.ypos, theta, 3])
            theta+=math.pi/8
    def shot_4(self, pl):
        dx=0
        dy=-50
        for i in range(10):
            dx+=3
            dy+=9
            theta = (math.atan2(pl.xpos-self.xpos-dx, pl.ypos-self.ypos-dy))
            self.bullet.append([0, self.xpos+dx, self.ypos +dy, theta, 4])
        for i in range(10):
            dx-=8
            dy-=5.6
            theta = (math.atan2(pl.xpos - self.xpos - dx, pl.ypos - self.ypos - dy))
            self.bullet.append([0, self.xpos + dx, int(self.ypos + dy), theta, 4])
        for i in range(10):
            dx+=9.9
            dy-=0
            theta = (math.atan2(pl.xpos - self.xpos - dx, pl.ypos - self.ypos - dy))
            self.bullet.append([0, self.xpos + dx, int(self.ypos + dy), theta, 4])
        for i in range(10):
            dx-=8
            dy+=5.6
            theta = (math.atan2(pl.xpos - self.xpos - dx, pl.ypos - self.ypos - dy))
            self.bullet.append([0, self.xpos + dx, int(self.ypos + dy), theta, 4])
        for i in range(10):
            dx+=3
            dy-=9
            theta = (math.atan2(pl.xpos - self.xpos - dx, pl.ypos - self.ypos - dy))
            self.bullet.append([0, self.xpos+dx, self.ypos +dy, theta, 4])
    def update_attack(self, pl, width, height):
        self.attack_frame += 1
        if self.attack_frame < 30:
            self.image = i.mob
            return
        if self.attack_frame == 30:
            if self.choice == 5:
                self.image = i.mob_ready
            else:
                self.image = i.mob_charge
            return
        if self.attack_frame < 35:
            return

        self.image = i.mob_shoot
        if self.choice == 1:
            self.update_pattern_1()
        elif self.choice == 2:
            self.update_pattern_2(pl)
        elif self.choice == 3:
            self.update_pattern_3(pl)
        elif self.choice == 4:
            self.update_pattern_4(pl)
        else:
            self.teleport(width, height)

    def update_pattern_1(self):
        self.pattern_frame += 1
        if self.pattern_frame <= 5:
            self.shot_1()
        elif self.pattern_frame <= 13:
            return
        elif self.pattern_frame <= 18:
            self.shot_1()
        elif self.pattern_frame <= 26:
            return
        elif self.pattern_frame <= 31:
            self.shot_1()
        else:
            self.reset_attack_cycle()

    def update_pattern_2(self, pl):
        self.pattern_frame += 1
        if self.pattern_frame < 5:
            self.shot_2()
        elif self.pattern_frame < 7:
            self.temp_theta = math.atan2(pl.xpos - self.xpos, pl.ypos - self.ypos)
        elif self.pattern_frame < 11:
            self.shot_2()
        elif self.pattern_frame < 13:
            self.temp_theta = math.atan2(pl.xpos - self.xpos, pl.ypos - self.ypos)
        elif self.pattern_frame < 17:
            self.shot_2()
        elif self.pattern_frame < 19:
            self.temp_theta = math.atan2(pl.xpos - self.xpos, pl.ypos - self.ypos)
        elif self.pattern_frame < 23:
            self.shot_2()
        else:
            self.temp_theta = 0
            self.reset_attack_cycle()

    def update_pattern_3(self, pl):
        self.pattern_frame += 1
        if self.pattern_frame < 90:
            if self.pattern_frame % 3 == 0:
                self.shot_3(pl)
        else:
            self.reset_attack_cycle()

    def update_pattern_4(self, pl):
        self.pattern_frame += 1
        if self.pattern_frame <= 49:
            if self.pattern_frame % 7 == 0:
                self.shot_4(pl)
        else:
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
            if enemyshot[4] == 4 and self.time < 600:
                self.time += 1
                active_enemy_shots.append(enemyshot)
                continue
            enemyshot[1] += self.shotspeed * math.sin(enemyshot[3])
            enemyshot[2] += self.shotspeed * math.cos(enemyshot[3])
            if enemyshot[1] < 0 or enemyshot[2] < 0 or enemyshot[1] > width or enemyshot[2] > height:
                continue
            elif player_rect.collidepoint((enemyshot[1], enemyshot[2])) and player.invisible == False:
                player.invisible = True
                player.invisiblecool = c.INVISIBLETIME
                player.life -= 1
                continue
            else:
                screen.blit(self.shot, (enemyshot[1], enemyshot[2]))
                active_enemy_shots.append(enemyshot)
        self.bullet = active_enemy_shots
