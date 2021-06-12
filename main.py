from datetime import datetime
from numpy import array
from PIL import ImageGrab, Image, ImageTk
import cv2
import sys
import tempfile
from win32api import GetSystemMetrics
import pyaudio
import wave
import os
import threading
import tkinter as tk


def print_help():
    print("""
    Usage: ./Recorder [OPTION]...
    Record screen and video.

    Options...

        --no-video         record without video
        --no-screen        record without screen capture
        --no-mic           record without user sound
        --no-audio         record without system audio
        --help             to know about this tool
    
    Example...
        
        Ex1: ./Recorder --no-video
        Ex2: ./Recorder --no-video --no-audio
    """)


def suppress_qt_warnings():
    os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"


class Recorder:
    def __init__(self):
        self.args = sys.argv[1:]
        self.video, self.screen, self.mic, self.audio = self.get_details()
        self.file_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.mp4'
        self.temp_dir = tempfile.gettempdir()

        # Setting up audio
        self.check_audio = True
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 2
        self.fs = 44100
        self.filename = "output.wav"
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.sample_format,
                                  channels=self.channels,
                                  rate=self.fs,
                                  frames_per_buffer=self.chunk,
                                  input=True)

        # Setting up video
        suppress_qt_warnings()
        self.video_frame = None
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.width = GetSystemMetrics(0)
        self.height = GetSystemMetrics(1)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.captured_video = cv2.VideoWriter(self.file_name, fourcc, 20.0, (self.width, self.height))

        # Initiate recording
        thread1 = threading.Thread(target=self.start_video)
        thread2 = threading.Thread(target=self.start_audio)
        self.thread3 = threading.Thread(target=self.start_window)
        thread1.start()
        thread2.start()

    def start_video(self):
        check = True
        while self.capture.isOpened():

            # Record screen
            screen = ImageGrab.grab(bbox=(0, 0, self.width, self.height))
            screen_array = array(screen)
            screen_final = cv2.cvtColor(screen_array, cv2.COLOR_BGR2RGB)

            # Record video
            ret, frame = self.capture.read()
            self.video_frame = frame
            if check:
                self.thread3.start()
                check = False

            self.captured_video.write(screen_final)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.capture.release()
        cv2.destroyAllWindows()

    def start_audio(self):
        frames = []
        while self.capture.isOpened():
            data = self.stream.read(self.chunk)
            frames.append(data)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        # Save audio
        write_audio = wave.open(self.filename, 'wb')
        write_audio.setnchannels(self.channels)
        write_audio.setsampwidth(self.p.get_sample_size(self.sample_format))
        write_audio.setframerate(self.fs)
        write_audio.writeframes(b''.join(frames))
        write_audio.close()

    def start_window(self):
        window = tk.Tk()
        window.wm_title("Webcam")

        image_frame = tk.Frame(window, width=self.width, height=self.height)
        image_frame.grid(row=0, column=0, padx=0, pady=0)

        label_main = tk.Label(image_frame)
        label_main.grid(row=0, column=0)

        def show_frame():
            frame = cv2.flip(self.video_frame, 1)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            img_tk = ImageTk.PhotoImage(image=img)
            label_main.img_tk = img_tk
            label_main.configure(image=img_tk)
            label_main.after(10, show_frame)

        show_frame()
        window.call('wm', 'attributes', '.', '-topmost', '1')
        window.mainloop()

    def get_details(self):
        video = True
        screen = True
        mic = True
        audio = True
        if '--help' in self.args:
            print_help()
            sys.exit()
        if '--no-video' in self.args:
            video = False
        if '--no-screen' in self.args:
            screen = False
        if '--no-mic' in self.args:
            mic = False
        if '--no--audio' in self.args:
            audio = False
        return video, screen, mic, audio


Recorder()
