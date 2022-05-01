import pygame, sys, math
import constant as c
import image
import random
import Mover as m

'''PYGAME 기본 설정'''
pygame.init()
pygame.key.set_repeat(True, True)
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((c.WINWIDTH, c.WINHEIGHT), pygame.FULLSCREEN)
fpsClock = pygame.time.Clock()
running=True

'''게임에 필요한 변수 목록'''
menubgm=pygame.mixer.Sound("menusong.wav")
gamebgm=pygame.mixer.Sound("gamesong.m4a")
endbgm=pygame.mixer.Sound("ending.m4a")
mobcnt = 0
picindex = 0
healthrange=5
shotposlist = []
nowshot = image.shotimg[0]
charge_temp = 0
TILESIZE=image.tile_green.get_rect()
TILEWIDTH=c.WINWIDTH//TILESIZE[2]
TILEHEIGHT=c.WINHEIGHT//TILESIZE[3]
WIDTH=TILESIZE[2]*TILEWIDTH
HEIGHT=TILESIZE[3]*TILEHEIGHT
HEARTSIZE=image.heart.get_rect()
dmg, spd, ssd, lif= 0,0,0,0
endset=0

'''텍스트 출력 함수'''
def text(string, x, y) :
    font = pygame.font.Font(None, 24)
    text = font.render(string, True, c.WHITE)
    textRect = text.get_rect()
    textRect.center = (x,y)
    screen.blit(text, textRect)

'''기타 변수 선언'''
player = m.Player()
bang = m.Enemy()
surune = 0
hormonecool=0
hormoning=False
mouseimg_rect = image.mouseimg.get_rect()
hormonetime=0
hormonenum=random.randint(0,9)
yap=0
screen.fill(c.BACKGROUNDCOLOR)
selected = False

w,h=image.menu.get_size()
image.menu=pygame.transform.scale(image.menu, (WIDTH, HEIGHT))
buff_rect=image.buff.get_rect()
horpos=(random.randint(15, WIDTH-40), random.randint(15, HEIGHT-40))

'''메뉴 선택 화면 출력'''
menubgm.play()
while not selected:
    screen.fill(c.BACKGROUNDCOLOR)
    screen.blit(image.menu, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_SPACE:
                selected = True
    pygame.display.flip()

missioning=50
while missioning:
    screen.fill(c.BACKGROUNDCOLOR)
    screen.blit(image.mission, (0,0))
    missioning-=1
    pygame.display.flip()

'''게임 화면 출력'''
menubgm.stop()
gamebgm.play()
while running:
    screen.fill(c.BACKGROUNDCOLOR)

    '''타일 출력'''
    for temp_width in range(TILEWIDTH):
        for temp_height in range(TILEHEIGHT):
            screen.blit(image.tile_green, (temp_width * TILESIZE[2], temp_height * TILESIZE[3]))

    player.shotcool-=1
    player.invisiblecool-=1
    if player.invisiblecool<=0:
        player.invisible=False

    '''호르몬 출력'''
    hormonecool += 1
    if hormonecool>=c.HORMONETIME:
        hormone_rect=image.hormone[hormonenum].get_rect()
        hormone_rect.center=horpos
        screen.blit(image.hormone[hormonenum], horpos)
        if nowplayer_rect.colliderect(hormone_rect):
            '''호르몬을 먹었다면,'''
            nowhormone=c.HORMONE[hormonenum]
            player.hormonelist.append([hormonenum, c.HORMONELAST])
            dmg, spd, ssd, lif = (nowhormone[1], nowhormone[2], nowhormone[3], nowhormone[4])
            player.damage += nowhormone[1]
            player.speed += nowhormone[2]
            player.shotspeed += nowhormone[3]
            player.life += nowhormone[4]

            hormonecool=0
            hormoning=True
            hormonetime=c.HORMONELAST
            hormonenum=random.randint(0,9)
            horpos = (random.randint(15, WIDTH - 40), random.randint(15, HEIGHT - 40))

    '''호르몬 효과가 발동중이라면,'''
    if hormoning:
        for horm in player.hormonelist:
            horm[1]-=1
        if player.hormonelist[0][1]==0:
            '''호르몬 효과가 끝났다면,'''
            player.damage -= c.HORMONE[horm[0]][1]
            player.speed -= c.HORMONE[horm[0]][2]
            player.shotspeed -= c.HORMONE[horm[0]][3]
            del(player.hormonelist[0])
        if not player.hormonelist:
            hormoning=False
            pass
        elif hormoning:
            pygame.draw.rect(screen, c.RED, (player.xpos-20, player.ypos-30, 40 * player.hormonelist[len(player.hormonelist)-1][1] // c.HORMONELAST, 3))
            text(nowhormone[0], player.xpos, player.ypos-45)

    '''마우스 커서 표시'''
    mousepos = pygame.mouse.get_pos()
    mouseimg_rect.center = (mousepos[0], mousepos[1])
    screen.blit(image.mouseimg, mouseimg_rect)

    '''플레이어 이미지 조정'''
    if player.charging == True:
        player.chargingtime += 1
        player.speed = 0
        charge_temp = player.chargingtime//c.CHARGETERM
        if(charge_temp>=3):
            charge_temp=3
        nowshot=image.shotimg[charge_temp]
        if player.direction=="left":
            player.nowplayer=image.charge_left[charge_temp]
        elif player.direction=="right":
            player.nowplayer=image.charge_right[charge_temp]
    else:
        if player.direction=="left":
            player.nowplayer = image.standing_left
        elif player.direction=="right":
            player.nowplayer = image.standing_right

    '''이벤트가 발생하면,'''
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit
        if event.type == pygame.KEYDOWN:
            if keys[pygame.K_ESCAPE]:
                running = False
                break
            if keys[pygame.K_a]:
                player.direction="left"
                player.nextpic()
                player.xpos -= player.speed
                if player.xpos<10 or player.xpos>WIDTH-15:
                        player.xpos+=player.speed
            if keys[pygame.K_d]:
                player.direction="right"
                player.nextpic()
                player.xpos += player.speed
                if player.xpos<10 or player.xpos>WIDTH-15:
                        player.xpos-=player.speed
            if keys[pygame.K_w]:
                player.ypos -= player.speed
                if player.ypos<10 or player.ypos>HEIGHT-15:
                        player.ypos+=player.speed
            if keys[pygame.K_s]:
                player.ypos += player.speed
                if player.ypos<10 or player.ypos>HEIGHT-15:
                        player.ypos-=player.speed
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_d:
                dx = 0
            if keys[pygame.K_w] == False or keys[pygame.K_s] == False:
                dy = 0
        if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            if player.shotcool <= 0 and player.charging==False:
                player.charging=True
                player.chargingtime+=1
                player.shotcool==c.SHOTGAP
        if event.type == pygame.MOUSEBUTTONUP and event.button==1:
            player.speed=c.MAXSPEED
            player.charging=False
            player.chargingtime=0
            theta = math.pi / 2 - (math.atan2(mousepos[1] - player.ypos + 5, mousepos[0] - player.xpos - 10))
            shotposlist.append([charge_temp, player.xpos - 10, player.ypos + 5, theta])
            shotcool = c.SHOTGAP
            if player.xpos>mousepos[0]:
                nowplayer=image.standing_left
            else:
                nowplayer=image.standing_right

    '''종료 조건 검사'''
    if not running:
        break

    '''플레이어 체력 표시'''
    for k in range(player.life):
        screen.blit(image.heart, (20 + 3 * (k + 1) + HEARTSIZE[2]* k, 20))

    '''플레이어가 쏜 탄알 출력'''
    index = 0
    for shot in shotposlist:
        rotated_shotimg = pygame.transform.rotate(image.shotimg[shot[0]], 90 + (int(math.degrees(shot[3]))))
        shot[1] += player.shotspeed * math.sin(shot[3])
        shot[2] += player.shotspeed * math.cos(shot[3])
        shotimg_rect = nowshot.get_rect()
        if (shot[1] < 0 or shot[2] < 0 or shot[1] > WIDTH or shot[2] > HEIGHT) :
            del (shotposlist[index])
        elif (monster_rect.collidepoint(shot[1], shot[2])):
            bang.health-=player.damage
            del(shotposlist[index])
        else:
            screen.blit(rotated_shotimg, (shot[1], shot[2]))
            index += 1

    '''몬스터의 공격'''
    yap+=1
    if yap<30:
        bang.image=image.mob
    elif yap==30:
        if bang.choice==5:
            bang.image = image.mob_ready
        else:
            bang.image=image.mob_charge
    elif yap>=35:
        bang.image=image.mob_shoot
        if (bang.choice == 1):
            '''엷은 탄막 3개'''
            surune+=1
            if surune <= 5:
                bang.shot_1()
            elif surune<=13:
                pass
            elif surune<=18:
                bang.shot_1()
            elif surune<=26:
                pass
            elif surune<=31:
                bang.shot_1()
            else:
                bang.image=image.mob
                yap=0
                surune = 0
                bang.choice = 5
        elif (bang.choice == 2):
            '''오각형 산탄 패턴'''
            surune += 1
            if surune < 5:
                bang.shot_2()
            elif surune < 7:
                bang.temp_theta = (math.atan2(player.xpos - bang.xpos, player.ypos - bang.ypos))
            elif surune < 11:
                bang.shot_2()
            elif surune < 13:
                bang.temp_theta = (math.atan2(player.xpos - bang.xpos, player.ypos - bang.ypos))
            elif surune < 17:
                bang.shot_2()
            elif surune < 19:
                bang.temp_theta = (math.atan2(player.xpos - bang.xpos, player.ypos - bang.ypos))
            elif surune < 23:
                bang.shot_2()
            else:
                bang.temp_theta = 0
                bang.image=image.mob
                surune=0
                bang.choice = 5
                yap=0
        elif (bang.choice==3):
            '''원형 유도탄 패턴'''
            surune+=1
            if surune<90:
                if surune%3==0:
                    bang.shot_3(player)
            else:
                bang.image=image.mob
                surune=0
                yap=0
                bang.choice = 5
        elif (bang.choice==4):
            '''별 패턴'''
            surune+=1
            if surune<=49:
                if surune%7==0:
                    bang.shot_4(screen, player)
            else:
                bang.image=image.mob
                surune=0
                yap=0
                bang.choice = 5
        else:
            '''몬스터 텔레포트'''
            bang.image=image.mob_telpo
            surune=0
            yap=0
            bang.choice=random.randint(1,bang.level)
            bang.xpos = random.randint(20, WIDTH - 50)
            bang.ypos = random.randint(20, HEIGHT - 50)

    '''몬스터 공격 출력'''
    for enemyshot in bang.bullet:
        if enemyshot[4]==4 and bang.time < 600:
            bang.time+=1
            continue
        else:
            enemyshot[1] += bang.shotspeed * math.sin(enemyshot[3])
            enemyshot[2] += bang.shotspeed * math.cos(enemyshot[3])
        if (enemyshot[1] < 0 or enemyshot[2] < 0 or enemyshot[1] > WIDTH or enemyshot[2] > HEIGHT):
            del(enemyshot)
        elif (nowplayer_rect.collidepoint((enemyshot[1], enemyshot[2])) and player.invisible==False):
            player.invisible=True
            player.invisiblecool=c.INVISIBLETIME
            player.life-=1
            del(enemyshot)
        else:
            screen.blit(bang.shot, (enemyshot[1], enemyshot[2]))

    '''플레이어가 사망했다면'''
    if player.life==0:
        running = False
        endset=1

    '''몬스터가 사살되었다면'''
    if bang.health<=0:
        running = False
        endset=2
        break

    '''캐릭터 이미지 출력'''
    nowplayer_rect = player.nowplayer.get_rect()
    nowplayer_rect.center = (player.xpos, player.ypos)
    if player.invisible == True and player.invisiblecool%2==0:
        #피격무적이 발동중이라면 깜빡거리게 출력
        screen.blit(player.nowplayer, nowplayer_rect)
    elif player.invisible == False:
        screen.blit(player.nowplayer, nowplayer_rect)

    '''호르몬 투여시 버프 모양 출력'''
    if hormoning:
        buff_rect.center = (player.xpos, player.ypos)
        screen.blit(image.buff, buff_rect)

    '''몬스터 이미지 출력'''
    monster_rect = bang.image.get_rect()
    monster_rect.center = (bang.xpos, bang.ypos)
    screen.blit(bang.image, monster_rect)

    '''몬스터 체력바 출력'''
    pygame.draw.rect(screen, c.WHITE, (bang.xpos-70, bang.ypos-40, 140, 7))
    pygame.draw.rect(screen, c.COLOR[healthrange], (bang.xpos - 70, bang.ypos - 40, int(0.1 * (bang.health-(1400*healthrange))), 7))
    if (int(0.1 * (bang.health - (1400 * healthrange))) <= 0) :
        healthrange -= 1
        bang.smaller()

    fpsClock.tick(c.FPS)
    pygame.display.flip()

'''게임 오버 (승리/패배)'''
screen.fill(c.BACKGROUNDCOLOR)
gamebgm.stop()
endbgm.play()
if endset==1:
    screen.blit(image.gameover, (0,0))
elif endset==2:
    screen.blit(image.youwin, (0,0))
pygame.display.flip()

ending=True
while ending:
    for event in pygame.event.get():
        if event.key==pygame.K_ESCAPE:
            ending=False

'''게임 종료시'''
if running==False and ending==False:
    running = False
    pygame.quit()
    sys.exit
