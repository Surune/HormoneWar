import ctypes

'''기본 화면 설정'''
FPS=30
#화면에 꽉차는 정사각형 모양의 화면 크기 설정
WINWIDTH=640 #ctypes.windll.user32.GetSystemMetrics(1)
WINHEIGHT=640 #ctypes.windll.user32.GetSystemMetrics(1)
#640*640짜리 기준으로 만든 화면을 확대
SCALE_X=WINWIDTH/640
SCALE_Y=WINHEIGHT/640

'''색상 선언'''
BACKGROUNDCOLOR=(0,0,0)
WHITE=(255,255,255)
RED=(255,0,0)
ORANGE=(255,127,39)
YELLOW=(255,240,0)
GREEN=(34,177,76)
BLUE=(63,72,205)
VIOLET=(163,76,173)
COLOR=(RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET) #몬스터 체력바를 위함

'''호르몬 리스트'''
'''("호르몬명", 공격력, 이동속도, 샷스피드, 체력)'''
HORMONE={0: ("Epinephrine", 1,1,1,0),
         1: ("Melatonin", -1,-1,-1,2),
         2: ("Growth Hormone", 0,2,0,1),
         3: ("Serotonin", -1,1,2,0),
         4: ("Dopamine", 5,0,0,0),
         5: ("Oxytocin", 1,0,1,0),
         6: ("Endorphin", 0,1,1,1),
         7: ("Insulin", 1,0,2,0),
         8: ("Glucagon", 2, 0, -1, 0),
         9: ("Cortisol", 3, -1, 0, 0)}

'''기타 게임 플레이와 관련된 상수'''
SHOTGAP=15
CHARGETERM=20
MAXSPEED=1
FLASHRELOAD=60
RELOADCOOL=50
RELOADNUM=8
HACK_RADIUS=100
HACK_DIS=0
INVISIBLETIME=20
HORMONETIME=150
HORMONELAST=200
MAXHEALTH=8401
