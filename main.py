from datetime import datetime
import os
from numpy import array
import cv2
import sys
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
from win32api import GetSystemMetrics
from pydub import AudioSegment
from pydub.utils import make_chunks


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


class Recorder:
    def __init__(self):
        self.args = sys.argv[1:]
        self.video, self.screen, self.mic, self.audio = self.get_details()
        self.file_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.mp4'
        self.temp_dir = tempfile.gettempdir()

        # Setting up audio
        self.freq = 44100
        self.duration = 600
        self.recording = sd.rec(int(self.duration * self.freq),
                                samplerate=self.freq, channels=2)

        # Setting up video
        self.capture = cv2.VideoCapture(0)
        width = GetSystemMetrics(0)
        height = GetSystemMetrics(1)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.captured_video = cv2.VideoWriter(self.file_name, fourcc, 20.0, (width, height))
        self.start_video()

    def start_video(self):
        while True:
            ret, frame = self.capture.read()
            cv2.imshow('frame', frame)
            self.captured_video.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.capture.release()
        cv2.destroyAllWindows()
        write("recording.wav", self.freq, self.recording)

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

# from pydub import AudioSegment
# from pydub.utils import make_chunks
#
# ##bluesfile 30s
# audio = AudioSegment.from_file("blues.00000.wav", "wav")
#
#  size = 10000 ##The milliseconds of cutting
#
#  chunks = make_chunks(audio, size) ##Cut the file into 10s pieces
#
# for i, chunk in enumerate(chunks):
#          ##Enumeration, i is the index, chunk is the cut file
#     chunk_name = "bulues{0}.wav".format(i)
#     print(chunk_name)
#          ##save document
#     chunk.export(chunk_name, format="wav")
