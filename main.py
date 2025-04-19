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

# Cấu hình Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Khởi tạo Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# Thiết lập chung
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

# Kết nối database
db = Database()

# Thiết lập màn hình
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

# Khởi tạo các nút
load_button = Button(screen, screen_width - 165, 30, load_btn)
save_button = Button(screen, screen_width - 165, 80, save_btn)
back_button = Button(screen, screen_width - 165, 130, back_btn)
restart_button = Button(screen, screen_width // 2 - 50, screen_height // 2 - 100, restart_btn)
menu_button = Button(screen, screen_width // 2 - 50, screen_height // 2 - 20, menu_btn)
playnow_button = Button(screen, screen_width // 2 - 90, 450, playnow_btn)
register_button = Button(screen, screen_width // 2 - 90, 560, register_btn)
exit_button = Button(screen, screen_width // 2 - 90, 670, exit_btn)
easy_button = Button(screen, 180, 500, easy_btn)
hard_button = Button(screen, screen_width - 360, 500, hard_btn)
setting_button = Button(screen, 180, 600, setting_btn)
ranking_button = Button(screen, screen_width - 360, 600, ranking_btn)
exit_from_main_button = Button(screen, 180, 700, exit_btn)
back_from_main_button = Button(screen, screen_width - 360, 700, back_from_main_btn)
back_from_ranking_button = Button(screen, 10, 10, back_from_ranking_btn)

# Khởi tạo coin
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# Khởi tạo face detection
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')
face_reco_model = dlib.face_recognition_model_v1("data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")

# Hàm vẽ text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Hàm reset level
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

# Hàm vẽ lưới
def draw_grid():
    for c in range(21):
        pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
        pygame.draw.line(screen, white, (0, c * tile_size), (screen_width - margin, c * tile_size))

# Hàm vẽ thế giới
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

# Hàm tạo thế giới mới
def generate_new_world():
    new_world = [[0 for _ in range(20)] for _ in range(20)]
    for i in range(20):
        new_world[0][i] = 1
        new_world[19][i] = 1
        new_world[i][0] = 1
        new_world[i][19] = 1
    return new_world

# Hàm load dữ liệu thế giới
def load_world_data():
    if os.path.exists(f'./env/level{level}_data'):
        with open(f'./env/level{level}_data', 'rb') as pickle_in:
            return pickle.load(pickle_in)
    return None

# Hàm load background
def load_background():
    return background[random.randint(0, 1)]

# Lớp Player
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
                    if keyaptan [pygame.K_LEFT]:
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

# Lớp Face_Recognizer
class Face_Recognizer:
    def __init__(self):
        self.font = cv2.FONT_ITALIC
        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0
        self.fps_show = 0
        self.start_time = time.time()
        self.frame_cnt = 0
        self.face_features_known_list = []
        self.face_name_known_list = []
        self.last_frame_face_centroid_list = []
        self.current_frame_face_centroid_list = []
        self.last_frame_face_name_list = []
        self.current_frame_face_name_list = []
        self.last_frame_face_cnt = 0
        self.current_frame_face_cnt = 0
        self.current_frame_face_X_e_distance_list = []
        self.current_frame_face_position_list = []
        self.current_frame_face_feature_list = []
        self.last_current_frame_centroid_e_distance = 0
        self.reclassify_interval_cnt = 0
        self.reclassify_interval = 10

    def get_face_database(self):
        if os.path.exists("data/features_all.csv"):
            path_features_known_csv = "data/features_all.csv"
            try:
                csv_rd = pd.read_csv(path_features_known_csv, header=None, encoding='windows-1258')
                if csv_rd.empty:
                    logging.warning("File 'features_all.csv' is empty! No face data available.")
                    return 0
                for i in range(csv_rd.shape[0]):
                    features_someone_arr = []
                    self.face_name_known_list.append(csv_rd.iloc[i][0])
                    for j in range(1, 129):
                        features_someone_arr.append('0' if pd.isna(csv_rd.iloc[i][j]) or csv_rd.iloc[i][j] == '' else csv_rd.iloc[i][j])
                    self.face_features_known_list.append(features_someone_arr)
                logging.info("Faces in Database: %d", len(self.face_features_known_list))
                return 1
            except pd.errors.EmptyDataError:
                logging.warning("File 'features_all.csv' is empty or invalid! No face data available.")
                return 0
        else:
            logging.warning("'features_all.csv' not found!")
            logging.warning("Please run 'get_faces_from_camera.py' and 'features_extraction_to_csv.py' to generate face data.")
            return 0

    def update_fps(self):
        now = time.time()
        if str(self.start_time).split(".")[0] != str(now).split(".")[0]:
            self.fps_show = self.fps
        self.start_time = now
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time if self.frame_time > 0 else 0
        self.frame_start_time = now

    @staticmethod
    def return_euclidean_distance(feature_1, feature_2):
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2)
        return np.sqrt(np.sum(np.square(feature_1 - feature_2)))

    def draw_note(self, img_rd):
        cv2.putText(img_rd, "Face Recognizer with Deep Learning", (20, 40), self.font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img_rd, f"Frame: {self.frame_cnt}", (20, 100), self.font, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(img_rd, f"FPS: {self.fps.__round__(2)}", (20, 130), self.font, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(img_rd, f"Faces: {self.current_frame_face_cnt}", (20, 160), self.font, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(img_rd, "Q: Quit", (20, 450), self.font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

# Khởi tạo biến webcam
cap = None
webcam_active = False

# Khởi tạo game
world_data = load_world_data() or generate_new_world()
world = World(screen, world_data, blob_group, platform_group, lava_group, coin_group, exit_group)
player = Player(screen, 100, screen_height - 130)
face_recognizer = Face_Recognizer()

# Vòng lặp chính
with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while run:
        clock.tick(fps)
        screen.blit(menu_background, (0, 0))

        if login_screen:
            if not player_name:
                if face_recognizer.get_face_database():
                    face_recognizer.frame_cnt += 1
                    logging.debug(f"Frame {face_recognizer.frame_cnt} starts")
                    if cap is None or not cap.isOpened():
                        cap = cv2.VideoCapture(0)
                        if not cap.isOpened():
                            print("Không thể mở webcam trong login. Vui lòng kiểm tra thiết bị.")
                            run = False
                            break
                    ret, img_rd = cap.read()
                    if not ret:
                        print("Không thể đọc khung hình từ webcam trong login.")
                        continue
                    faces = detector(img_rd, 0)
                    face_recognizer.last_frame_face_cnt = face_recognizer.current_frame_face_cnt
                    face_recognizer.current_frame_face_cnt = len(faces)
                    face_recognizer.last_frame_face_name_list = face_recognizer.current_frame_face_name_list[:]
                    face_recognizer.last_frame_face_centroid_list = face_recognizer.current_frame_face_centroid_list
                    face_recognizer.current_frame_face_centroid_list = []

                    face_recognizer.current_frame_face_position_list = []
                    face_recognizer.current_frame_face_X_e_distance_list = []
                    face_recognizer.current_frame_face_feature_list = []
                    face_recognizer.reclassify_interval_cnt = 0

                    if face_recognizer.current_frame_face_cnt == 0:
                        face_recognizer.current_frame_face_name_list = []
                    else:
                        face_recognizer.current_frame_face_name_list = []
                        for i in range(len(faces)):
                            shape = predictor(img_rd, faces[i])
                            face_recognizer.current_frame_face_feature_list.append(face_reco_model.compute_face_descriptor(img_rd, shape))
                            face_recognizer.current_frame_face_name_list.append("unknown")
                            player_name = "unknown"

                        for k in range(len(faces)):
                            face_recognizer.current_frame_face_X_e_distance_list = []
                            face_recognizer.current_frame_face_position_list.append((
                                faces[k].left(), int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)
                            ))
                            for i in range(len(face_recognizer.face_features_known_list)):
                                if str(face_recognizer.face_features_known_list[i][0]) != '0.0':
                                    e_distance_tmp = face_recognizer.return_euclidean_distance(
                                        face_recognizer.current_frame_face_feature_list[k],
                                        face_recognizer.face_features_known_list[i]
                                    )
                                    face_recognizer.current_frame_face_X_e_distance_list.append(e_distance_tmp)
                                else:
                                    face_recognizer.current_frame_face_X_e_distance_list.append(999999999)

                            similar_person_num = face_recognizer.current_frame_face_X_e_distance_list.index(
                                min(face_recognizer.current_frame_face_X_e_distance_list)
                            )
                            if min(face_recognizer.current_frame_face_X_e_distance_list) < 0.4:
                                player_name = face_recognizer.current_frame_face_name_list[k] = face_recognizer.face_name_known_list[similar_person_num]

            screen.blit(logo, (screen_width // 2 - 200, 20))
            draw_text("Adventure", pygame.font.SysFont('Bauhaus 93', 100), (241, 196, 15), 190, 260)
            draw_text(f"Player: {player_name}", font_main, (44, 62, 80), 250, 380)
            if register_button.draw():
                register.main()
                player_name = ""
            if playnow_button.draw():
                main_menu = True
                login_screen = False
            if exit_button.draw():
                run = False
                if cap:
                    cap.release()
                break
            pygame.display.update()

        elif main_menu:
            if cap and cap.isOpened():
                cap.release()
                cv2.destroyAllWindows()
            screen.blit(logo, (screen_width // 2 - 200, 20))
            draw_text("Adventure", pygame.font.SysFont('Bauhaus 93', 100), (241, 196, 15), 190, 260)
            draw_text(f"Player: {player_name}", font_main, (44, 62, 80), 250, 380)
            if exit_from_main_button.draw():
                run = False
                break
            if easy_button.draw():
                mode = "EASY"
                main_menu = False
                level = 1
                webcam_active = True
            if hard_button.draw():
                mode = "HARD"
                main_menu = False
                level = 1
                webcam_active = True
            if setting_button.draw():
                setting_menu = True
                main_menu = False
                tile_size = 30
            if back_from_main_button.draw():
                main_menu = False
                login_screen = True
                player_name = ""
            if ranking_button.draw():
                ranking_screen = True
                main_menu = False
                try:
                    data_easy_ranking = [data for data in db.get_statistic() if data.get("mode") == "EASY"]
                    data_hard_ranking = [data for data in db.get_statistic() if data.get("mode") == "HARD"]
                except Exception as e:
                    print(f"Lỗi khi lấy dữ liệu xếp hạng: {e}")
                    data_easy_ranking = []
                    data_hard_ranking = []
            pygame.display.update()

        elif setting_menu:
            if cap and cap.isOpened():
                cap.release()
                cv2.destroyAllWindows()
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
            draw_text('Press UP or DOWN to change level', pygame.font.SysFont('Futura', 32), white, 100, screen_height - 110)
            pygame.display.update()

        elif ranking_screen:
            if cap and cap.isOpened():
                cap.release()
                cv2.destroyAllWindows()
            screen.blit(background[0], (0, 0))
            draw_text('Ranking', pygame.font.SysFont('Bauhaus 93', 55), wet_asphalt, 300, 10)
            draw_text('EASY', font_main, wet_asphalt, 150, 80)
            draw_text('HARD', font_main, wet_asphalt, 540, 80)
            size_of_easy_ranking = min(10, len(data_easy_ranking) if data_easy_ranking else 0)
            size_of_hard_ranking = min(10, len(data_hard_ranking) if data_hard_ranking else 0)
            draw_text("ID", font_ranking, wet_asphalt, 40, 160)
            draw_text("Player", font_ranking, wet_asphalt, 100, 160)
            draw_text("Score", font_ranking, wet_asphalt, 300, 160)
            draw_text("ID", font_ranking, wet_asphalt, 470, 160)
            draw_text("Player", font_ranking, wet_asphalt, 530, 160)
            draw_text("Score", font_ranking, wet_asphalt, 730, 160)
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

        else:  # Chế độ chơi
            if webcam_active:
                if cap is None or not cap.isOpened():
                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        print("Không thể mở webcam trong chế độ chơi. Vui lòng kiểm tra thiết bị.")
                        run = False
                        break
                ret, image = cap.read()
                if not ret:
                    print("Không thể đọc khung hình từ webcam trong chế độ chơi. Đang thử lại...")
                    cap.release()
                    cap = cv2.VideoCapture(0)  # Thử khởi tạo lại webcam
                    ret, image = cap.read()
                    if not ret:
                        print("Vẫn không thể đọc khung hình. Kiểm tra webcam hoặc kết nối.")
                        continue

                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
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

                cv2.imshow('Hand detector', cv2.flip(image, 1))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    webcam_active = False
                    main_menu = True
                    if cap:
                        cap.release()
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
                    if cap:
                        cap.release()
                        cv2.destroyAllWindows()

            if game_over == -1:
                if accept_save_database and player_name != 'unknown':
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
                    if cap:
                        cap.release()
                        cv2.destroyAllWindows()

            if game_over == 1:
                level += 1
                if load_world_data():
                    my_background = load_background()
                    world_data = generate_new_world()
                    world = reset_level(player, level)
                    game_over = 0
                else:
                    if accept_save_database and player_name != 'unknown':
                        db.save_statistic(player_name, score, level, mode)
                        accept_save_database = False
                    draw_text('YOU WIN!', font, yellow, (screen_width // 2) - 140, screen_height // 2 - 215)
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
                        if cap:
                            cap.release()
                            cv2.destroyAllWindows()

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

# Dọn dẹp khi thoát
pygame.quit()
if cap:
    cap.release()
cv2.destroyAllWindows()