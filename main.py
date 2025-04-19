import dlib
import numpy as np
import cv2
import os
import pandas as pd
import time
import os.path
import logging
import mediapipe as mp
import pygame
from pygame.locals import *
import pickle
import random
from pygame import mixer

from config.database import Database
from assets.assets import (
    game_over_fx, jump_fx, background, setting_background, menu_background,
    back_btn, save_btn, load_btn, restart_btn, menu_btn, playnow_btn,
    register_btn, exit_btn, ranking_btn, easy_btn, hard_btn, setting_btn,
    back_from_main_btn, back_from_ranking_btn, logo, blob_group, lava_group,
    exit_group, platform_group, coin_group, coin_fx, font, font_main,
    font_score, font_ranking, margin, dirt_img, grass_img, blob_img,
    platform_x_img, platform_y_img, lava_img, coin_img, exit_img2
)
from env.constants import (
    tile_size, screen_width, screen_height, fps, white, blue, yellow, green,
    wet_asphalt
)
from components.Coin import Coin
from components.World import World
from components.Button import Button
import components.Face_Detected.get_faces_from_camera_tkinter as register

# Cau hinh Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Khoi tao Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# Thiet lap chung
clock = pygame.time.Clock()
run = True
game_over = 0
main_menu = False
setting_menu = False
login_screen = True
ranking_screen = False
level = 1
score = 0
pedding = False
up_action = False
left_action = False
right_action = False
reset_up_action = False
accept_save_database = True
data_easy_ranking = None
data_hard_ranking = None
mode = "EASY"
player_name = ""
my_background = background[0]
login_active = False
login_message = ""

# Ket noi database
db = Database()

# Thiet lap man hinh
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

# Tai anh button login va logout, resize de dong nhat kich thuoc
login_btn_img = pygame.image.load("D:\\MINHNGUYET\\NAM3\\TGMT1\\DoAn\\TGMTFINAL\\resources\\img\\button\\login.png")
logout_btn_img = pygame.image.load("D:\\MINHNGUYET\\NAM3\\TGMT1\\DoAn\\TGMTFINAL\\resources\\img\\button\\logout.png")
login_btn = pygame.transform.scale(login_btn_img, (100, 40))
logout_btn = pygame.transform.scale(logout_btn_img, (100, 40))

# Khoi tao cac nut
load_button = Button(screen, screen_width - 165, 30, load_btn)
save_button = Button(screen, screen_width - 165, 80, save_btn)
back_button = Button(screen, screen_width - 165, 130, back_btn)
restart_button = Button(screen, screen_width // 2 - 50, screen_height // 2 - 100, restart_btn)
menu_button = Button(screen, screen_width // 2 - 50, screen_height // 2 - 20, menu_btn)
playnow_button = Button(screen, screen_width // 2 - 90, 450, playnow_btn)
login_button = Button(screen, 10, 10, login_btn)
register_button = Button(screen, screen_width // 2 - 90, 510, register_btn)
exit_button = Button(screen, screen_width // 2 - 90, 610, exit_btn)
easy_button = Button(screen, 180, 500, easy_btn)
hard_button = Button(screen, screen_width - 360, 500, hard_btn)
setting_button = Button(screen, 180, 600, setting_btn)
ranking_button = Button(screen, screen_width - 360, 600, ranking_btn)
logout_button = Button(screen, screen_width - 110, 10, logout_btn)
exit_from_main_button = Button(screen, 180, 700, exit_btn)
back_from_main_button = Button(screen, screen_width - 360, 700, back_from_main_btn)
back_from_ranking_button = Button(screen, 10, 10, back_from_ranking_btn)

# Khoi tao coin
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# Ham ve text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Ham reset level
def reset_level(player, level):
    print(f'level: {level}')
    blob_group.empty()
    platform_group.empty()
    coin_group.empty()
    lava_group.empty()
    exit_group.empty()
    player.reset(100, screen_height - 130)
    world_data = load_world_data()
    world = World(screen, world_data, blob_group, platform_group, lava_group, coin_group, exit_group)
    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)
    return world

# Ham ve luoi
def draw_grid():
    for c in range(21):
        pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
        pygame.draw.line(screen, white, (0, c * tile_size), (screen_width - margin, c * tile_size))

# Ham ve the gioi
def draw_world():
    for row in range(20):
        for col in range(20):
            if world_data[row][col] > 0:
                if world_data[row][col] == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    screen.blit(img, (col * tile_size, row * tile_size))
                elif world_data[row][col] == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    screen.blit(img, (col * tile_size, row * tile_size))
                elif world_data[row][col] == 3:
                    img = pygame.transform.scale(blob_img, (tile_size, int(tile_size * 0.75)))
                    screen.blit(img, (col * tile_size, row * tile_size + (tile_size * 0.25)))
                elif world_data[row][col] == 4:
                    img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2))
                    screen.blit(img, (col * tile_size, row * tile_size))
                elif world_data[row][col] == 5:
                    img = pygame.transform.scale(platform_y_img, (tile_size, tile_size // 2))
                    screen.blit(img, (col * tile_size, row * tile_size))
                elif world_data[row][col] == 6:
                    img = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
                    screen.blit(img, (col * tile_size, row * tile_size + (tile_size // 2)))
                elif world_data[row][col] == 7:
                    img = pygame.transform.scale(coin_img, (tile_size // 2, tile_size // 2))
                    screen.blit(img, (col * tile_size + (tile_size // 4), row * tile_size + (tile_size // 4)))
                elif world_data[row][col] == 8:
                    img = pygame.transform.scale(exit_img2, (tile_size, int(tile_size * 1.5)))
                    screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))

# Ham tao the gioi moi
def generate_new_world():
    new_world = [[0 for _ in range(20)] for _ in range(20)]
    for i in range(20):
        new_world[0][i] = 1
        new_world[19][i] = 1
        new_world[i][0] = 1
        new_world[i][19] = 1
    return new_world

# Ham load du lieu the gioi
def load_world_data():
    if os.path.exists(f'./env/level{level}_data'):
        with open(f'./env/level{level}_data', 'rb') as pickle_in:
            return pickle.load(pickle_in)
    return None

# Ham load background
def load_background():
    return background[random.randint(0, 1)]

# Lop Player
class Player:
    def __init__(self, screen, x, y):
        self.screen = screen
        self.reset(x, y)
        self.blob_group = blob_group
        self.platform_group = platform_group
        self.lava_group = lava_group
        self.exit_group = exit_group

    def update(self, game_over):
        dx, dy = 0, 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            key = pygame.key.get_pressed()
            if not pedding:
                if up_action and not self.jumped and not self.in_air:
                    jump_fx.play()
                    self.vel_y = -15
                    self.jumped = True
                if not up_action:
                    self.jumped = False
                if left_action:
                    dx -= 5
                    self.counter += 1
                    self.direction = -1
                if right_action:
                    dx += 5
                    self.counter += 1
                    self.direction = 1
                if not left_action and not right_action:
                    self.counter = 0
                    self.index = 0
                    self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]

                if mode == "EASY":
                    if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                        jump_fx.play()
                        self.vel_y = -15
                        self.jumped = True
                    if not key[pygame.K_SPACE]:
                        self.jumped = False
                    if key[pygame.K_LEFT]:
                        dx -= 5
                        self.counter += 1
                        self.direction = -1
                    if key[pygame.K_RIGHT]:
                        dx += 5
                        self.counter += 1
                        self.direction = 1
                    if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT] and not (left_action or right_action):
                        self.counter = 0
                        self.index = 0
                        self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]

            if self.counter > walk_cooldown:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images_right)
                self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]

            self.vel_y = min(self.vel_y + 1, 10)
            dy += self.vel_y

            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            if pygame.sprite.spritecollide(self, self.blob_group, False):
                game_over = -1
                game_over_fx.play()
            if pygame.sprite.spritecollide(self, self.lava_group, False):
                game_over = -1
                game_over_fx.play()
            if pygame.sprite.spritecollide(self, self.exit_group, False):
                game_over = 1

            for platform in self.platform_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 180, screen_height // 2 - 215)
            if self.rect.y > 200:
                self.rect.y -= 5

        self.screen.blit(self.image, self.rect)
        return game_over

    def reset(self, x, y):
        self.images_right = [pygame.transform.scale(pygame.image.load(f'./resources/img/guy{i}.png'), (32, 68)) for i in range(1, 5)]
        self.images_left = [pygame.transform.flip(img, True, False) for img in self.images_right]
        self.dead_image = pygame.image.load('./resources/img/ghost.png')
        self.image = self.images_right[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True
        self.index = 0
        self.counter = 0

# Khoi tao game
world_data = load_world_data() or generate_new_world()
world = World(screen, world_data, blob_group, platform_group, lava_group, coin_group, exit_group)
player = Player(screen, 100, screen_height - 130)

# Vong lap chinh
with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    webcam_active = False
    game_webcam = None  # Bien luu webcam trong che do choi
    while run:
        clock.tick(fps)

        # Xu ly su kien truoc de tranh xung dot
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        if login_screen:
            # Giao dien login screen
            screen.blit(menu_background, (0, 0))
            screen.blit(logo, (screen_width // 2 - 200, 20))
            draw_text("Adventure", pygame.font.SysFont('Bauhaus 93', 100), (241, 196, 15), 190, 260)
            display_name = player_name if player_name else "unknown"
            draw_text(f"Player: {display_name}", font_main, (44, 62, 80), 250, 380)
            draw_text(login_message, font_main, (44, 62, 80), 250, 410)

            # Xu ly nut Login
            if login_button.draw():
                login_active = True
                login_message = "Dang mo webcam, vui long cho..."

            if login_active:
                # Hien thi thong bao truoc khi mo webcam
                screen.blit(menu_background, (0, 0))
                screen.blit(logo, (screen_width // 2 - 200, 20))
                draw_text("Adventure", pygame.font.SysFont('Bauhaus 93', 100), (241, 196, 15), 190, 260)
                draw_text(f"Player: {display_name}", font_main, (44, 62, 80), 250, 380)
                draw_text("Dang mo webcam, vui long cho...", font_main, (44, 62, 80), 250, 410)
                pygame.display.update()

                # Dong tat ca cua so webcam truoc do
                cv2.destroyAllWindows()
                # Dong webcam cua Mediapipe neu dang mo
                if webcam_active and game_webcam is not None:
                    game_webcam.release()
                    webcam_active = False
                # Goi ham login() va dung vong lap Pygame
                player_name, login_message = register.login()
                login_active = False
                if player_name != "unknown":
                    main_menu = True
                    login_screen = False
                # Sau khi login xong, ve lai man hinh truoc khi tiep tuc vong lap
                screen.blit(menu_background, (0, 0))
                screen.blit(logo, (screen_width // 2 - 200, 20))
                draw_text("Adventure", pygame.font.SysFont('Bauhaus 93', 100), (241, 196, 15), 190, 260)
                draw_text(f"Player: {player_name if player_name else 'unknown'}", font_main, (44, 62, 80), 250, 380)
                draw_text(login_message, font_main, (44, 62, 80), 250, 410)
                pygame.display.update()
                continue

            # Cac nut khac trong login screen
            if playnow_button.draw():
                main_menu = True
                login_screen = False
                login_message = ""
            if register_button.draw():
                # Dong tat ca cua so webcam truoc khi goi Register
                cv2.destroyAllWindows()
                if webcam_active and game_webcam is not None:
                    game_webcam.release()
                    webcam_active = False
                player_name = register.main()
                login_message = ""
                if player_name != "unknown":
                    main_menu = True
                    login_screen = False
            if exit_button.draw():
                run = False
                break
            pygame.display.update()

        elif main_menu:
            screen.blit(menu_background, (0, 0))
            screen.blit(logo, (screen_width // 2 - 200, 20))
            draw_text("Adventure", pygame.font.SysFont('Bauhaus 93', 100), (241, 196, 15), 190, 260)
            display_name = player_name if player_name else "unknown"
            draw_text(f"Player: {display_name}", font_main, (44, 62, 80), 250, 380)
            if exit_from_main_button.draw():
                run = False
                break
            if easy_button.draw():
                mode = "EASY"
                main_menu = False
                level = 1
                webcam_active = True
                # Mo webcam mot lan duy nhat khi bat dau che do choi
                game_webcam = cv2.VideoCapture(0)
                if not game_webcam.isOpened():
                    print("Khong the mo webcam trong che do choi. Vui long kiem tra thiet bi.")
                    webcam_active = False
                    main_menu = True
            if hard_button.draw():
                mode = "HARD"
                main_menu = False
                level = 1
                webcam_active = True
                # Mo webcam mot lan duy nhat khi bat dau che do choi
                game_webcam = cv2.VideoCapture(0)
                if not game_webcam.isOpened():
                    print("Khong the mo webcam trong che do choi. Vui long kiem tra thiet bi.")
                    webcam_active = False
                    main_menu = True
            if setting_button.draw():
                setting_menu = True
                main_menu = False
                tile_size = 30
            if back_from_main_button.draw():
                main_menu = False
                login_screen = True
                player_name = ""
                login_message = ""
            if ranking_button.draw():
                ranking_screen = True
                main_menu = False
                try:
                    data_easy_ranking = [data for data in db.get_statistic() if data.get("mode") == "EASY"]
                    data_hard_ranking = [data for data in db.get_statistic() if data.get("mode") == "HARD"]
                except Exception as e:
                    print(f"Loi khi lay du lieu xep hang: {e}")
                    data_easy_ranking = []
                    data_hard_ranking = []
            if logout_button.draw():
                main_menu = False
                login_screen = True
                player_name = ""
                login_message = ""
                login_active = False
            pygame.display.update()

        elif setting_menu:
            screen.fill(green)
            screen.blit(setting_background, (0, 0))
            if save_button.draw():
                with open(f'./env/level{level}_data', 'wb') as pickle_out:
                    pickle.dump(world_data, pickle_out)
                level = 1
                world = reset_level(player, level)
            if load_button.draw():
                world_data = load_world_data() or generate_new_world()
            if back_button.draw():
                setting_menu = False
                main_menu = True
            draw_grid()
            draw_world()
            draw_text(f'Level: {level}', pygame.font.SysFont('Futura', 32), white, 100, screen_height - 140)
            draw_text('Nhan UP hoac DOWN de thay doi level', pygame.font.SysFont('Futura', 32), white, 100, screen_height - 110)
            pygame.display.update()

        elif ranking_screen:
            screen.blit(background[0], (0, 0))
            draw_text('Xep Hang', pygame.font.SysFont('Bauhaus 93', 55), wet_asphalt, 300, 10)
            draw_text('EASY', font_main, wet_asphalt, 150, 80)
            draw_text('HARD', font_main, wet_asphalt, 540, 80)
            size_of_easy_ranking = min(10, len(data_easy_ranking) if data_easy_ranking else 0)
            size_of_hard_ranking = min(10, len(data_hard_ranking) if data_hard_ranking else 0)
            draw_text("ID", font_ranking, wet_asphalt, 40, 160)
            draw_text("Nguoi Choi", font_ranking, wet_asphalt, 100, 160)
            draw_text("Diem", font_ranking, wet_asphalt, 300, 160)
            draw_text("ID", font_ranking, wet_asphalt, 470, 160)
            draw_text("Nguoi Choi", font_ranking, wet_asphalt, 530, 160)
            draw_text("Diem", font_ranking, wet_asphalt, 730, 160)
            if data_easy_ranking:
                for i in range(size_of_easy_ranking):
                    draw_text(str(i + 1), font_ranking, wet_asphalt, 40, 200 + 40 * i)
                    draw_text(data_easy_ranking[i]["player_name"], font_ranking, wet_asphalt, 100, 200 + 40 * i)
                    draw_text(str(data_easy_ranking[i]["score"]), font_ranking, wet_asphalt, 300, 200 + 40 * i)
            if data_hard_ranking:
                for i in range(size_of_hard_ranking):
                    draw_text(str(i + 1), font_ranking, wet_asphalt, 470, 200 + 40 * i)
                    draw_text(data_hard_ranking[i]["player_name"], font_ranking, wet_asphalt, 530, 200 + 40 * i)
                    draw_text(str(data_hard_ranking[i]["score"]), font_ranking, wet_asphalt, 730, 200 + 40 * i)
            if back_from_ranking_button.draw():
                main_menu = True
                ranking_screen = False
            pygame.display.update()

        else:
            if webcam_active:
                if game_webcam is None or not game_webcam.isOpened():
                    print("Khong the mo webcam trong che do choi. Vui long kiem tra thiet bi.")
                    webcam_active = False
                    main_menu = True
                    continue

                ret, image = game_webcam.read()
                if not ret:
                    print("Khong the doc khung hinh tu webcam trong che do choi. Dang thu lai...")
                    game_webcam.release()
                    game_webcam = cv2.VideoCapture(0)
                    ret, image = game_webcam.read()
                    if not ret:
                        print("Van khong the doc khung hinh. Kiem tra webcam hoac ket noi.")
                        webcam_active = False
                        main_menu = True
                        continue

                # Khong giam kich thuoc khung hinh, giu nguyen kich thuoc goc
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Xu ly Mediapipe tren moi khung hinh
                results = hands.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results and results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style()
                        )
                        handList = [[landmark.x, landmark.y, landmark.z] for landmark in hand_landmarks.landmark]
                        if (handList[6][1] - handList[8][1]) * 1000 > 70:
                            if reset_up_action:
                                up_action = True
                                reset_up_action = False
                                print(f'up_action: {up_action}')
                        if handList[8][1] > handList[6][1]:
                            reset_up_action = True
                            up_action = False
                        if (handList[18][1] - handList[20][1]) * 1000 > 70:
                            right_action = True
                            print(f'right_action: {right_action}')
                        if (handList[4][0] - handList[2][0]) * 1000 > 70:
                            left_action = True
                            print(f'left_action: {left_action}')
                        if handList[20][1] > handList[18][1]:
                            right_action = False
                        if handList[2][0] > handList[4][0]:
                            left_action = False

                cv2.imshow('Nhan Dien Tay', cv2.flip(image, 1))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    webcam_active = False
                    main_menu = True
                    if game_webcam is not None:
                        game_webcam.release()
                        game_webcam = None
                    cv2.destroyAllWindows()

            screen.blit(my_background, (0, 0))
            world.draw()
            if game_over == 0:
                if not pedding:
                    blob_group.update()
                    platform_group.update()
                if pygame.sprite.spritecollide(player, coin_group, True):
                    score += 1
                    coin_fx.play()
                draw_text(f'X {score}', font_score, white, tile_size, 6)

            blob_group.draw(screen)
            platform_group.draw(screen)
            lava_group.draw(screen)
            coin_group.draw(screen)
            exit_group.draw(screen)
            game_over = player.update(game_over)

            if pedding:
                if restart_button.draw():
                    pedding = False
                if menu_button.draw():
                    world_data = load_world_data() or generate_new_world()
                    world = reset_level(player, level)
                    game_over = score = 0
                    main_menu = True
                    pedding = False
                    webcam_active = False
                    if game_webcam is not None:
                        game_webcam.release()
                        game_webcam = None

            if game_over == -1:
                if accept_save_database:
                    db.save_statistic(player_name, score, level, mode)
                    accept_save_database = False
                if restart_button.draw():
                    world_data = generate_new_world()
                    world = reset_level(player, level)
                    game_over = score = 0
                    accept_save_database = True
                if menu_button.draw():
                    world_data = load_world_data() or generate_new_world()
                    world = reset_level(player, level)
                    game_over = score = 0
                    main_menu = True
                    accept_save_database = True
                    webcam_active = False
                    if game_webcam is not None:
                        game_webcam.release()
                        game_webcam = None

            if game_over == 1:
                level += 1
                if load_world_data():
                    my_background = load_background()
                    world_data = generate_new_world()
                    world = reset_level(player, level)
                    game_over = 0
                else:
                    if accept_save_database:
                        db.save_statistic(player_name, score, level, mode)
                        accept_save_database = False
                    draw_text('BAN THANG!', font, yellow, (screen_width // 2) - 140, screen_height // 2 - 215)
                    if restart_button.draw():
                        level = 1
                        world_data = generate_new_world()
                        world = reset_level(player, level)
                        game_over = score = 0
                        accept_save_database = True
                    if menu_button.draw():
                        level = 1
                        world_data = load_world_data() or generate_new_world()
                        world = reset_level(player, level)
                        main_menu = True
                        game_over = score = 0
                        accept_save_database = True
                        webcam_active = False
                        if game_webcam is not None:
                            game_webcam.release()
                            game_webcam = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pedding = True
                elif setting_menu:
                    if event.key == pygame.K_UP:
                        level += 1
                    elif event.key == pygame.K_DOWN and level > 1:
                        level -= 1
            elif event.type == pygame.MOUSEBUTTONDOWN and setting_menu and 'clicked' not in locals():
                clicked = True
                pos = pygame.mouse.get_pos()
                x, y = pos[0] // tile_size, pos[1] // tile_size
                if x < 20 and y < 20:
                    if pygame.mouse.get_pressed()[0]:
                        world_data[y][x] = (world_data[y][x] + 1) % 9
                    elif pygame.mouse.get_pressed()[2]:
                        world_data[y][x] = (world_data[y][x] - 1) if world_data[y][x] > 0 else 8
            elif event.type == pygame.MOUSEBUTTONUP and setting_menu:
                clicked = False

        pygame.display.update()

# Don dep khi thoat
if game_webcam is not None:
    game_webcam.release()
pygame.quit()
cv2.destroyAllWindows()