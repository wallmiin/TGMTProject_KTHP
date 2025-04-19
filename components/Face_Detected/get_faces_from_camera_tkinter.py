import dlib
import numpy as np
import cv2
import os
import shutil
import time
import logging
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
import pandas as pd

import components.Face_Detected.features_extraction_to_csv as features_extraction_to_csv

# Su dung bo nhan dien khuon mat cua Dlib
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')
face_reco_model = dlib.face_recognition_model_v1("data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")

is_register = False

class Face_Register:
    def __init__(self, is_register):
        self.is_register = is_register
        self.current_frame_faces_cnt = 0 
        self.existing_faces_cnt = 0  
        self.ss_cnt = 0  
        # Tkinter GUI
        self.win = tk.Tk()
        self.win.title("Dang Ky Khuon Mat")
        self.win.geometry("1000x800")

        # GUI phan ben trai
        self.frame_left_camera = tk.Frame(self.win)
        self.label = tk.Label(self.win)
        self.label.pack(side=tk.LEFT)
        self.frame_left_camera.pack()

        # GUI phan ben phai
        self.frame_right_info = tk.Frame(self.win)
        self.label_cnt_face_in_database = tk.Label(self.frame_right_info, text=str(self.existing_faces_cnt))
        self.label_fps_info = tk.Label(self.frame_right_info, text="")
        self.input_name = tk.Entry(self.frame_right_info)
        self.input_name_char = ""
        self.label_warning = tk.Label(self.frame_right_info)
        self.label_face_cnt = tk.Label(self.frame_right_info, text="So khuon mat trong khung hinh: ")
        self.log_all = tk.Label(self.frame_right_info)

        self.font_title = tkFont.Font(family='Helvetica', size=20, weight='bold')
        self.font_step_title = tkFont.Font(family='Helvetica', size=15, weight='bold')
        self.font_warning = tkFont.Font(family='Helvetica', size=15, weight='bold')

        self.path_photos_from_camera = "data/data_faces_from_camera/"
        self.current_face_dir = ""
        self.font = cv2.FONT_ITALIC

        # Vi tri khung hinh va khuon mat ROI
        self.current_frame = np.ndarray
        self.face_ROI_image = np.ndarray
        self.face_ROI_width_start = 0
        self.face_ROI_height_start = 0
        self.face_ROI_width = 0
        self.face_ROI_height = 0
        self.ww = 0
        self.hh = 0

        self.out_of_range_flag = False
        self.face_folder_created_flag = False

        # FPS
        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0
        self.fps_show = 0
        self.start_time = time.time()

        # Bien de luu player_name sau khi dang ky
        self.player_name = "unknown"
        self.cap = None  # Bien webcam

    # Xoa cac thu muc khuon mat cu
    def GUI_clear_data(self):
        folders_rd = os.listdir(self.path_photos_from_camera)
        for i in range(len(folders_rd)):
            shutil.rmtree(self.path_photos_from_camera + folders_rd[i])
        
        self.label_cnt_face_in_database['text'] = "0"
        self.existing_faces_cnt = 0
        self.log_all["text"] = "Da xoa anh khuon mat!"

    def GUI_get_input_name(self):
        self.input_name_char = self.input_name.get()
        self.create_face_folder()
        self.label_cnt_face_in_database['text'] = str(self.existing_faces_cnt)

    def GUI_info(self):
        tk.Label(self.frame_right_info,
                 text="Dang Ky Khuon Mat",
                 font=self.font_title).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=2, pady=20)

        tk.Label(self.frame_right_info, text="FPS: ").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_fps_info.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info, text="So khuon mat trong CSDL: ").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_cnt_face_in_database.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info,
                 text="So khuon mat trong khung hinh: ").grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        self.label_face_cnt.grid(row=3, column=2, columnspan=3, sticky=tk.W, padx=5, pady=2)

        self.label_warning.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        # Buoc 1: Xoa du lieu cu
        tk.Label(self.frame_right_info,
                 font=self.font_step_title,
                 text="Xoa anh cu").grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)
        tk.Button(self.frame_right_info,
                  text='Xoa',
                  command=self.GUI_clear_data).grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        # Buoc 2: Nhap ten va tao thu muc cho khuon mat
        tk.Label(self.frame_right_info,
                 font=self.font_step_title,
                 text="Buoc 1: Nhap ten").grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)

        tk.Label(self.frame_right_info, text="Ten: ").grid(row=8, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_name.grid(row=8, column=1, sticky=tk.W, padx=0, pady=2)

        tk.Button(self.frame_right_info,
                  text='Nhap',
                  command=self.GUI_get_input_name).grid(row=8, column=2, padx=5)

        # Buoc 3: Luu khuon mat hien tai trong khung hinh
        tk.Label(self.frame_right_info,
                 font=self.font_step_title,
                 text="Buoc 2: Luu anh khuon mat").grid(row=9, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)

        tk.Button(self.frame_right_info,
                  text='Luu khuon mat hien tai',
                  command=self.save_current_face).grid(row=10, column=0, columnspan=3, sticky=tk.W)
        tk.Button(self.frame_right_info,
                  text='Hoan Tat Dang Ky',
                  command=self.complete_register).grid(row=14, column=0, columnspan=3, sticky=tk.W)
        tk.Button(self.frame_right_info,
                  text='Quay lai menu chinh',
                  command=self.exit_window).grid(row=15, column=0, columnspan=3, sticky=tk.W)

        # Hien thi log tren GUI
        self.log_all.grid(row=11, column=0, columnspan=20, sticky=tk.W, padx=5, pady=20)

        self.frame_right_info.pack()

    def complete_register(self):
        self.is_register = True
        if self.is_register == True:
            features_extraction_to_csv.main()
        self.player_name = self.input_name_char if self.input_name_char else "unknown"
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
        self.win.destroy()

    def exit_window(self):
        self.delete_face_folder()
        self.player_name = "unknown"
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
        self.win.destroy()

    # Tao thu muc de luu anh va csv
    def pre_work_mkdir(self):
        if os.path.isdir(self.path_photos_from_camera):
            pass
        else:
            os.mkdir(self.path_photos_from_camera)

    # Bat dau tu person_x+1
    def check_existing_faces_cnt(self):
        if os.listdir("data/data_faces_from_camera/"):
            person_list = os.listdir("data/data_faces_from_camera/")
            person_num_list = []
            for person in person_list:
                person_order = person.split('_')[1].split('_')[0]
                person_num_list.append(int(person_order))
            self.existing_faces_cnt = max(person_num_list)
        else:
            self.existing_faces_cnt = 0

    # Cap nhat FPS cua video stream
    def update_fps(self):
        now = time.time()
        if str(self.start_time).split(".")[0] != str(now).split(".")[0]:
            self.fps_show = self.fps
        self.start_time = now
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time
        self.frame_start_time = now
        self.label_fps_info["text"] = str(self.fps.__round__(2))

    def delete_face_folder(self):
        try:
            shutil.rmtree(self.current_face_dir)
            self.log_all["text"] = "\"" + self.current_face_dir + "/\" da xoa!"
            logging.info("\n%-40s %s", "Xoa thu muc:", self.current_face_dir)
        except FileNotFoundError:
            self.log_all["text"] = "\"" + self.current_face_dir + "/\" khong tim thay!"
            logging.warning("\n%-40s %s", "Thu muc khong tim thay:", self.current_face_dir)

    def create_face_folder(self):
        self.existing_faces_cnt += 1
        if self.input_name_char:
            self.current_face_dir = self.path_photos_from_camera + \
                                    "person_" + str(self.existing_faces_cnt) + "_" + \
                                    self.input_name_char
        else:
            self.current_face_dir = self.path_photos_from_camera + \
                                    "person_" + str(self.existing_faces_cnt)
        os.makedirs(self.current_face_dir)
        self.log_all["text"] = "\"" + self.current_face_dir + "/\" da tao!"
        logging.info("\n%-40s %s", "Tao thu muc:", self.current_face_dir)
        self.ss_cnt = 0
        self.face_folder_created_flag = True

    def save_current_face(self):
        if self.face_folder_created_flag:
            if self.current_frame_faces_cnt == 1:
                if not self.out_of_range_flag:
                    self.ss_cnt += 1
                    self.face_ROI_image = np.zeros((int(self.face_ROI_height * 2), self.face_ROI_width * 2, 3),
                                                   np.uint8)
                    for ii in range(self.face_ROI_height * 2):
                        for jj in range(self.face_ROI_width * 2):
                            self.face_ROI_image[ii][jj] = self.current_frame[self.face_ROI_height_start - self.hh + ii][
                                self.face_ROI_width_start - self.ww + jj]
                    self.log_all["text"] = "\"" + self.current_face_dir + "/img_face_" + str(
                        self.ss_cnt) + ".jpg\"" + " da luu!"
                    self.face_ROI_image = cv2.cvtColor(self.face_ROI_image, cv2.COLOR_BGR2RGB)
                    cv2.imwrite(self.current_face_dir + "/img_face_" + str(self.ss_cnt) + ".jpg", self.face_ROI_image)
                    logging.info("%-40s %s/img_face_%s.jpg", "Luu vao：",
                                 str(self.current_face_dir), str(self.ss_cnt) + ".jpg")
                else:
                    self.log_all["text"] = "Vui long khong vuot qua gioi han!"
            else:
                self.log_all["text"] = "Khong co khuon mat hoac qua nhieu khuon mat trong khung hinh!"
        else:
            self.log_all["text"] = "Vui long chay buoc 2!"

    def get_frame(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Loi: Khong the mo webcam de dang ky!")
                self.log_all["text"] = "Khong the mo webcam!"
                return False, None
        try:
            ret, frame = self.cap.read()
            if not ret:
                print("Loi: Khong the doc khung hinh tu webcam!")
                self.log_all["text"] = "Khong the doc khung hinh tu webcam!"
                return False, None
            # Giam kich thuoc khung hinh de toi uu
            frame = cv2.resize(frame, (240, 180))
            return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"Loi doc khung hinh: {e}")
            self.log_all["text"] = f"Loi: {e}"
            return False, None

    # Qua trinh chinh cua nhan dien khuon mat va luu
    def process(self):
        ret, self.current_frame = self.get_frame()
        if not ret:
            self.win.after(50, self.process)
            return
        
        # Chi xu ly khuon mat moi 2 khung hinh de giam tai
        self.frame_count = getattr(self, 'frame_count', 0) + 1
        if self.frame_count % 2 == 0:
            faces = detector(self.current_frame, 0)
        else:
            faces = []

        # Cap nhat FPS
        self.update_fps()
        self.label_face_cnt["text"] = str(len(faces))
        
        # Khuon mat duoc nhan dien
        if len(faces) != 0:
            for k, d in enumerate(faces):
                self.face_ROI_width_start = d.left()
                self.face_ROI_height_start = d.top()
                self.face_ROI_height = (d.bottom() - d.top())
                self.face_ROI_width = (d.right() - d.left())
                self.hh = int(self.face_ROI_height / 2)
                self.ww = int(self.face_ROI_width / 2)

                if (d.right() + self.ww) > 240 or (d.bottom() + self.hh > 180) or (d.left() - self.ww < 0) or (d.top() - self.hh < 0):
                    self.label_warning["text"] = "VUOT QUA GIOI HAN"
                    self.label_warning['fg'] = 'red'
                    self.out_of_range_flag = True
                    color_rectangle = (255, 0, 0)
                else:
                    self.out_of_range_flag = False
                    self.label_warning["text"] = ""
                    color_rectangle = (255, 255, 255)
                
                self.current_frame = cv2.rectangle(self.current_frame,
                                                   (d.left() - self.ww, d.top() - self.hh),
                                                   (d.right() + self.ww, d.bottom() + self.hh),
                                                   color_rectangle, 2)
        self.current_frame_faces_cnt = len(faces)

        # Chuyen anh OpenCV sang PIL.Image.Image
        img = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img)
        
        # Chuyen PIL.Image.Image sang PIL.ImageTk.PhotoImage
        photo_image = ImageTk.PhotoImage(image=pil_image)
        self.label.img_tk = photo_image
        self.label.configure(image=photo_image)

        # Lam moi khung hinh
        self.win.after(50, self.process)

    def run(self):
        self.pre_work_mkdir()
        self.check_existing_faces_cnt()
        self.GUI_info()
        self.process()
        self.win.mainloop()
        return self.player_name

    # Ham dang nhap bang nhan dien khuon mat
    def login_face(self, timeout=15):
        face_features_known_list = []
        face_name_known_list = []
        if os.path.exists("data/features_all.csv"):
            try:
                csv_rd = pd.read_csv("data/features_all.csv", header=None, encoding='windows-1258')
                if csv_rd.empty:
                    logging.warning("File 'features_all.csv' trong! Khong co du lieu khuon mat.")
                    return "unknown", "Khong tim thay du lieu khuon mat!"
                for i in range(csv_rd.shape[0]):
                    features_someone_arr = []
                    face_name_known_list.append(csv_rd.iloc[i][0])
                    for j in range(1, 129):
                        features_someone_arr.append('0' if pd.isna(csv_rd.iloc[i][j]) or csv_rd.iloc[i][j] == '' else csv_rd.iloc[i][j])
                    face_features_known_list.append(features_someone_arr)
                logging.info("So khuon mat trong CSDL: %d", len(face_features_known_list))
            except pd.errors.EmptyDataError:
                logging.warning("File 'features_all.csv' trong hoac khong hop le! Khong co du lieu khuon mat.")
                return "unknown", "Khong tim thay du lieu khuon mat!"
        else:
            logging.warning("'features_all.csv' khong tim thay!")
            return "unknown", "Khong tim thay du lieu khuon mat!"

        # Thu mo webcam toi da 3 lan
        cap = None
        max_attempts = 3
        for attempt in range(max_attempts):
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                logging.info("Mo webcam thanh cong tai lan thu %d", attempt + 1)
                break
            logging.warning("Khong mo duoc webcam tai lan thu %d", attempt + 1)
            time.sleep(1)  # Doi 1 giay truoc khi thu lai
            if cap is not None:
                cap.release()

        if not cap or not cap.isOpened():
            logging.error("Khong the mo webcam de dang nhap sau %d lan thu!", max_attempts)
            return "unknown", "Khong the mo webcam! Vui long kiem tra thiet bi."

        player_name = "unknown"
        message = "Dang nhan dien khuon mat..."
        start_time = time.time()
        frame_count = 0  # Bien dem khung hinh de giam tan suat xu ly

        try:
            while time.time() - start_time < timeout:
                ret, img_rd = cap.read()
                if not ret:
                    logging.warning("Khong the doc khung hinh tu webcam!")
                    message = "Khong the doc khung hinh tu webcam!"
                    break

                # Giam kich thuoc khung hinh de toi uu
                img_rd = cv2.resize(img_rd, (240, 180))
                
                # Chi xu ly khuon mat moi 2 khung hinh
                frame_count += 1
                if frame_count % 2 == 0:
                    faces = detector(img_rd, 0)
                else:
                    faces = []

                if len(faces) != 1:
                    logging.info("Tim thay %d khuon mat trong khung hinh, can 1", len(faces))
                    # Hien thi thong bao tren cua so webcam
                    img_rd = cv2.putText(img_rd, "Vui long chi co 1 khuon mat", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                else:
                    shape = predictor(img_rd, faces[0])
                    current_face_feature = face_reco_model.compute_face_descriptor(img_rd, shape)

                    e_distance_list = []
                    for known_features in face_features_known_list:
                        e_distance = np.sqrt(np.sum(np.square(np.array(current_face_feature) - np.array(known_features))))
                        e_distance_list.append(e_distance)

                    min_distance_idx = e_distance_list.index(min(e_distance_list))
                    if min(e_distance_list) < 0.4:
                        player_name = face_name_known_list[min_distance_idx]
                        message = "Dang nhap thanh cong!"
                        logging.info("Nhan dien khuon mat: %s", player_name)
                        break
                    else:
                        img_rd = cv2.rectangle(img_rd, (faces[0].left(), faces[0].top()), (faces[0].right(), faces[0].bottom()), (255, 255, 255), 2)

                # Hien thi thong bao trang thai tren cua so webcam
                img_rd = cv2.putText(img_rd, "Dang Nhap Khuon Mat - Nhan 'q' de thoat", (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.imshow("Dang Nhap Khuon Mat", img_rd)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logging.info("Nguoi dung huy dang nhap bang phim 'q'")
                    message = "Da huy dang nhap!"
                    break
        except Exception as e:
            logging.error(f"Loi khi dang nhap bang khuon mat: {e}")
            message = "Da xay ra loi khi nhan dien khuon mat!"
        finally:
            if cap is not None:
                cap.release()
            cv2.destroyAllWindows()

        if player_name == "unknown" and message == "Dang nhan dien khuon mat...":
            message = "Khong nhan dien duoc khuon mat!"
        return player_name, message

def main():
    logging.basicConfig(level=logging.INFO)
    Face_Register_con = Face_Register(is_register)
    return Face_Register_con.run()

def login():
    Face_Register_con = Face_Register(is_register=False)
    return Face_Register_con.login_face()