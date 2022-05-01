import constant as c
import image as i
import math, pygame
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
        self.check = True
        self.charging = False
        self.chargingtime = 0
        self.nowplayer = i.standing_right
        self.direction = "right"
        self.index = 0
        self.hacknum = 3
        self.hacking = False
        self.invisible=False
        self.invisiblecool=0
        self.relaoding=False
        self.hormonelist=[]
    def nextpic(self):
        if (self.index == 3):
            self.index=0
        else:
            self.index+=1

        if self.direction=="right":
            self.nowplayer=i.run_right[self.index]
        elif self.direction=="left":
            self.nowplayer=i.run_left[self.index]

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
        self.shot=pygame.image.load("mob_shot.png")
        w, h = self.shot.get_size()
        self.shot = pygame.transform.scale(self.shot, (int(w * c.SCALE_X), int(h * c.SCALE_Y)))
        self.choice=r.randint(1,self.level)
        self.time=0
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
    def shot_4(self, scr, pl):
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