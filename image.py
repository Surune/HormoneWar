import pygame
import constant as c

'''탄알수 이미지'''
bullet=pygame.image.load("bullet.png")
w,h=bullet.get_size()
bullet=pygame.transform.scale(bullet, (int(c.SCALE_X*w), int(c.SCALE_Y*h)))

'''해킹횟수 이미지'''
hack=pygame.image.load("hack.png")
w,h=hack.get_size()
hack=pygame.transform.scale(hack, (int(c.SCALE_X*w), int(c.SCALE_Y*h)))

'''체력 이미지'''
heart=pygame.image.load("heart.png")
w,h=heart.get_size()
heart=pygame.transform.scale(heart, (int(c.SCALE_X*w), int(c.SCALE_Y*h)))

'''플레이어 서 있는 이미지'''
standing_right=pygame.image.load("char_standing.png")
w,h=standing_right.get_size()
standing_right=pygame.transform.scale(standing_right, (int(c.SCALE_X*w), int(c.SCALE_Y*h)))
standing_left=pygame.transform.flip(standing_right, True, False)

'''플레이어 달리는 모션 이미지'''
run_right=[]; run_left=[]
for i in range(1,4):
    run = pygame.image.load("char_run"+str(i)+".png")
    w, h = run.get_size()
    run = pygame.transform.scale(run, (int(c.SCALE_X * w), int(c.SCALE_Y * h)))
    run_right.append(run)
    run_left.append(pygame.transform.flip(run, True, False))
run=pygame.image.load("char_run2.png")
w,h=run.get_size()
run=pygame.transform.scale(run, (int(c.SCALE_X*w), int(c.SCALE_Y*h)))
run_right.append(run)
run_left.append(pygame.transform.flip(run, True, False))
run_right=tuple(run_right); run_left=tuple(run_left)

'''플레이어 차징 모션 이미지'''
charge_right=[] ; charge_left=[]
for i in range(1,5):
    charge=pygame.image.load("char_charge"+str(i)+".png")
    w,h=charge.get_size()
    charge_right.append(pygame.transform.scale(charge, (int(w*c.SCALE_X), int(h*c.SCALE_Y))))
    charge_left.append(pygame.transform.flip(charge_right[i-1], True, False))
charge_right=tuple(charge_right); charge_left=tuple(charge_left)

'''플레이어 총알 쏘는 이미지'''
shooting_right=pygame.image.load("char_shot.png")
w,h=shooting_right.get_size()
shooting_right=pygame.transform.scale(shooting_right, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))
shooting_left=pygame.transform.flip(shooting_right, True, False)

'''타일(밑바닥 배경) 이미지'''
tile_green=pygame.image.load("tile_green.png")
w,h=tile_green.get_size()
tile_green=pygame.transform.scale(tile_green, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))
tile_red=pygame.image.load("tile_red.png")
w,h=tile_red.get_size()
tile_red=pygame.transform.scale(tile_red, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))

'''호르몬 이미지'''
hormone=[]
for i in range(1,11):
    hrm=pygame.image.load("hormone_"+str(i)+".png")
    w,h=hrm.get_size()
    hrm=pygame.transform.scale(hrm, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))
    hormone.append(pygame.transform.rotate(hrm, -45))

'''호르몬 버프 이미지'''
buff=pygame.image.load("buff.png")
w,h=buff.get_size()
buff=pygame.transform.scale(buff, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))

'''플레이어 총알 이미지'''
shotimg=[]
scale=2/3
for i in range(1,5):
    shot=pygame.image.load("shot_"+str(i)+".png")
    w,h=shot.get_size()
    shotimg.append(pygame.transform.scale(shot, (int(scale*w*c.SCALE_X), int(scale*h*c.SCALE_Y))))
shotimg=tuple(shotimg)

'''마우스 커서 이미지'''
mouseimg=pygame.image.load("mouse.png")

menu=pygame.image.load("menu.png")
w,h=menu.get_size()
menu=pygame.transform.scale(menu, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))

'''몬스터 이미지_기본'''
mob=pygame.image.load("monster.png")
w,h=mob.get_size()
mob=pygame.transform.scale(mob, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))

'''몬스터 이미지_공격대기모션'''
mob_charge=pygame.image.load("monster_charging.png")
w,h=mob_charge.get_size()
mob_charge=pygame.transform.scale(mob_charge, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))

'''몬스터 이미지_공격 모션'''
mob_shoot=pygame.image.load("monster_shooting.png")
w,h=mob_shoot.get_size()
mob_shoot=pygame.transform.scale(mob_shoot, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))

'''몬스터 이미지_텔레포트대기모션'''
mob_ready=pygame.image.load("monster_ready.png")
w,h=mob_ready.get_size()
mob_ready=pygame.transform.scale(mob_ready, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))

'''몬스터 이미지_텔레포트 모션'''
mob_telpo=pygame.image.load("monster_teleport.png")
w,h=mob_telpo.get_size()
mob_telpo=pygame.transform.scale(mob_telpo, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))

'''미션 화면'''
mission=pygame.image.load("mission.png")
w,h=mission.get_size()
mission=pygame.transform.scale(mission, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))

'''게임 종료 화면(몬스터 사살 시)'''
youwin=pygame.image.load("youwin.png")
w,h=youwin.get_size()
youwin=pygame.transform.scale(youwin, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))

'''게임 종료 화면(몬스터 사망 시)'''
gameover=pygame.image.load("gameover.png")
w,h=gameover.get_size()
gameover=pygame.transform.scale(gameover, (int(w*c.SCALE_X), int(h*c.SCALE_Y)))