import numpy as np
from pydub import AudioSegment
import sounddevice as sd
from queue import Queue, Empty
import threading

class Sound:
    def __init__(self, file_path, chunk_size=1024):
        # MP3ファイルを読み込み
        self.audio = AudioSegment.from_mp3(file_path)
        self.audio = self.audio.set_channels(1)  # モノラルに変換
        self.audio = self.audio.set_frame_rate(44100)  # サンプリングレートを設定

        # 生のデータを取得
        self.raw_data = np.frombuffer(self.audio.raw_data, dtype=np.int16)
        self.sample_rate = self.audio.frame_rate
        self.chunk_size = chunk_size
        self.num_chunks = len(self.raw_data) // self.chunk_size

        # 再生用のフレームカウンタ
        self.audio_frame = [0]

        # 波形データを格納するキュー
        self.data_queue = Queue()

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
            # キューに残りのデータを入れて終了
            self.data_queue.put(data.tolist())
            raise sd.CallbackStop()
        else:
            outdata[:] = data.reshape(-1, 1)
            # 波形データをキューに入れる
            self.data_queue.put(data.tolist())
        self.audio_frame[0] += frames

    def play(self):
        # ストリーミング再生を開始
        self.is_playing.set()
        with sd.OutputStream(samplerate=self.sample_rate, channels=1, dtype='int16',
                             callback=self.audio_callback, blocksize=self.chunk_size):
            sd.sleep(int(len(self.raw_data) / self.sample_rate * 1000))
        self.is_playing.clear()

    def stream_wave_data(self):
        # 再生中の波形データをストリーミング出力
        while self.is_playing.is_set() or not self.data_queue.empty():
            try:
                data = self.data_queue.get(timeout=0.1)
                yield data
            except Empty:
                continue


if __name__ == '__main__':
    # 使用例
    sound = Sound("sound/Dive_To_Mod.mp3")

    # 再生と波形データのストリーミングを別スレッドで行う
    play_thread = threading.Thread(target=sound.play)
    play_thread.start()

    # 波形データをリアルタイムで取得
    for wave_data in sound.stream_wave_data():
        # wave_dataは現在のチャンクの波形データのリスト
        print(wave_data[:10])  # 例として最初の10サンプルを表示

    play_thread.join()
