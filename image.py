import pygame

import constant as c


def load_scaled_image(path, scale=1, rotate=0, flip_x=False):
    image = pygame.image.load(path)
    width, height = image.get_size()
    scaled_size = (int(width * c.SCALE_X * scale), int(height * c.SCALE_Y * scale))
    image = pygame.transform.scale(image, scaled_size)
    if rotate:
        image = pygame.transform.rotate(image, rotate)
    if flip_x:
        image = pygame.transform.flip(image, True, False)
    return image


def load_animation(prefix, count, rotate=0, scale=1):
    frames = []
    for index in range(1, count + 1):
        frames.append(load_scaled_image(f"{prefix}{index}.png", scale=scale, rotate=rotate))
    return tuple(frames)


bullet = load_scaled_image("bullet.png")
hack = load_scaled_image("hack.png")
heart = load_scaled_image("heart.png")

standing_right = load_scaled_image("char_standing.png")
standing_left = pygame.transform.flip(standing_right, True, False)

run_right = list(load_animation("char_run", 3))
run_right.append(load_scaled_image("char_run2.png"))
run_right = tuple(run_right)
run_left = tuple(pygame.transform.flip(frame, True, False) for frame in run_right)

charge_right = load_animation("char_charge", 4)
charge_left = tuple(pygame.transform.flip(frame, True, False) for frame in charge_right)

shooting_right = load_scaled_image("char_shot.png")
shooting_left = pygame.transform.flip(shooting_right, True, False)

tile_green = load_scaled_image("tile_green.png")
tile_red = load_scaled_image("tile_red.png")

hormone = []
for index in range(1, 11):
    hormone.append(load_scaled_image(f"hormone_{index}.png", rotate=-45))

buff = load_scaled_image("buff.png")
shotimg = load_animation("shot_", 4, scale=2 / 3)

mob_shot = load_scaled_image("mob_shot.png")
mouseimg = pygame.image.load("mouse.png")

menu = load_scaled_image("menu.png")
mob = load_scaled_image("monster.png")
mob_charge = load_scaled_image("monster_charging.png")
mob_shoot = load_scaled_image("monster_shooting.png")
mob_ready = load_scaled_image("monster_ready.png")
mob_telpo = load_scaled_image("monster_teleport.png")

mission = load_scaled_image("mission.png")
youwin = load_scaled_image("youwin.png")
gameover = load_scaled_image("gameover.png")
