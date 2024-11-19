# sound.py

import numpy as np
from pydub import AudioSegment
import sounddevice as sd
from queue import Queue
import threading


class Sound:
    def __init__(self, file_path, chunk_size=1024, update_interval=0.1):
        # MP3ファイルを読み込み
        self.audio = AudioSegment.from_mp3(file_path)
        self.audio = self.audio.set_channels(1)  # モノラルに変換
        self.audio = self.audio.set_frame_rate(44100)  # サンプリングレートを設定

        # 生のデータを取得
        self.raw_data = np.frombuffer(self.audio.raw_data, dtype=np.int16)
        self.sample_rate = self.audio.frame_rate
        self.chunk_size = chunk_size
        self.update_interval = update_interval

        # 再生用のフレームカウンタ
        self.audio_frame = [0]

        # 振幅データを格納するキュー
        self.amplitude_queue = Queue()

        # 再生中フラグ
        self.is_playing = threading.Event()

    def audio_callback(self, outdata, frames, time, status):
        start = self.audio_frame[0]
        end = start + frames
        data = self.raw_data[start:end]
        if len(data) < frames:
            data = np.pad(data, (0, frames - len(data)), 'constant')
            outdata[:len(data)] = data.reshape(-1, 1)
            outdata[len(data):] = np.zeros((frames - len(data), 1), dtype='int16')
            # 振幅を計算してキューに追加
            amplitude = np.sqrt(np.mean(data.astype(np.float32) ** 2))
            self.amplitude_queue.put(amplitude)
            raise sd.CallbackStop()
        else:
            outdata[:] = data.reshape(-1, 1)
            # 振幅を計算してキューに追加
            amplitude = np.sqrt(np.mean(data.astype(np.float32) ** 2))
            self.amplitude_queue.put(amplitude)
        self.audio_frame[0] += frames

    def play(self):
        # ストリーミング再生を開始
        self.is_playing.set()
        with sd.OutputStream(samplerate=self.sample_rate, channels=1, dtype='int16',
                             callback=self.audio_callback, blocksize=int(self.sample_rate * self.update_interval)):
            sd.sleep(int(len(self.raw_data) / self.sample_rate * 1000))
        self.is_playing.clear()
