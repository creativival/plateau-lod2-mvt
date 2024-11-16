import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pydub import AudioSegment
import sounddevice as sd

used_fft = False

# MP3ファイルを読み込み
audio = AudioSegment.from_mp3("sound/Dive_To_Mod.mp3")
audio = audio.set_channels(1)  # モノラルに変換
audio = audio.set_frame_rate(44100)  # サンプリングレートを設定

# 生のデータを取得
raw_data = np.frombuffer(audio.raw_data, dtype=np.int16)
sample_rate = audio.frame_rate

# データをチャンクに分割
chunk_size = 1024
num_chunks = len(raw_data) // chunk_size

# 再生用のフレームカウンタ
audio_frame = [0]

if used_fft:
    # プロットの設定（波形用）
    fig, ax = plt.subplots()
    x = np.arange(chunk_size)
    line, = ax.plot(x, np.ones(chunk_size))
    ax.set_xlim(0, chunk_size)
    ax.set_ylim(-2**15, 2**15)
    ax.set_xlabel('Time [samples]')
    ax.set_ylabel('Amplitude')

    def update(frame):
        start = frame * chunk_size
        end = start + chunk_size
        data = raw_data[start:end]
        if len(data) < chunk_size:
            data = np.pad(data, (0, chunk_size - len(data)), 'constant')
        line.set_ydata(data)
        return line,
else:
    # プロットの設定
    fig, ax = plt.subplots()
    x = np.arange(0, chunk_size)
    line, = ax.plot(x, np.zeros(chunk_size))
    ax.set_ylim(-32768, 32767)  # 16ビットの音声データ範囲

    def update(frame):
        start = frame * chunk_size
        end = start + chunk_size
        data = raw_data[start:end]
        if len(data) < chunk_size:
            data = np.pad(data, (0, chunk_size - len(data)), 'constant')
        line.set_ydata(data)
        return line,

def audio_callback(outdata, frames, time, status):
    start = audio_frame[0]
    end = start + frames
    data = raw_data[start:end]
    if len(data) < frames:
        data = np.pad(data, (0, frames - len(data)), 'constant')
        outdata[:len(data)] = data.reshape(-1, 1)
        outdata[len(data):] = np.zeros((frames - len(data), 1), dtype='int16')
        raise sd.CallbackStop()
    else:
        outdata[:] = data.reshape(-1, 1)
    audio_frame[0] += frames

ani = FuncAnimation(fig, update, frames=num_chunks, interval=chunk_size/sample_rate*1000, blit=True)

# ストリーミングと可視化を同時に行う
with sd.OutputStream(samplerate=sample_rate, channels=1, dtype='int16',
                     callback=audio_callback, blocksize=chunk_size):
    plt.show()
