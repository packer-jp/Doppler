import pyaudio
import struct
import threading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fs = 44100
A = 15000
om1 = 2 * np.pi * 770
om2 = 2 * np.pi * 960
T = 20
sonic = 340
gain = 3
step = 4410  # アニメーションを作るときのステップ

# 音の再生関数
def play(signal):
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = fs,
                    output = True)

    signal = np.array(signal, dtype = "int16")
    signal = struct.pack("h" * len(signal), *signal)

    chunk = 1024
    sp = 0
    buffer = signal[sp:sp + chunk]
    while buffer != b'':
        stream.write(buffer)
        sp = sp + chunk
        buffer = signal[sp:sp + chunk]

    stream.close()
    p.terminate()

# 発される音
def org(t):
    if int(t * 2) % 2 == 0:
        return A * np.sin(om1 * t)
    else:
        return A * np.sin(om2 * t)

# 音源の動き
def src_x(t):
    return (2 * t - T) * 100 / 6

def src_y(t):
    return 20

# 観測者の動き
def obs_x(t):
    return 0

def obs_y(t):
    return 0

# 二点間の距離
def dist(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

t = np.linspace(0, T, fs * T)
signal = []

# シミュレーション（尺取法 + 二分法）
idx = 0
for ti in t:
    while idx < len(t) and dist(src_x(t[idx]), src_y(t[idx]), obs_x(ti), obs_y(ti)) < (ti - t[idx]) * sonic:
        idx = idx + 1

    lb = t[idx - 1] if idx > 0 else t[0]
    ub = t[idx] if idx < len(t) else t[len(t) - 1]
    for j in range(0, 10):
        tau = (lb + ub) / 2;
        if dist(src_x(tau), src_y(tau), obs_x(ti), obs_y(ti)) < (ti - tau) * sonic:
            lb = tau
        else:
            ub = tau

    signal.append(org(tau) / ((ti - tau) * gain + 1))

# アニメーションの準備
fig = plt.figure()
ims = []
for ti in t[::step]:
    im = plt.plot(src_x(ti), src_y(ti), 'ro', obs_x(ti), obs_y(ti), 'bo')
    ims.append(im)

# 音の再生（別スレッド）
thread_p = threading.Thread(target = play, args = ([signal]))
thread_p.start()

# アニメーションの再生
ani = animation.ArtistAnimation(fig, ims, interval = 1000 * step / fs, repeat = False)
plt.show()

# なんかちょっとずれる！
