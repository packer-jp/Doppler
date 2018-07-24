import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fs = 44100
A = 15000
om1 = 2 * np.pi * 770
om2 = 2 * np.pi * 960
T = 10
sonic = 340
gain = 3
step = 4410  # アニメーションを作るときのステップ

# 再生
def play(signal):
  p = pyaudio.PyAudio()
  stream = p.open(format = pyaudio.paInt16,
                  channels = 1,
                  rate = fs,
                  output = True)

  signal = np.array(signal, dtype="int16")
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
  return 10

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

# シミュレーション（二分法）
for ti in t:
  lb = 0
  ub = T
  for j in range(0, 30):
    tau = (lb + ub) / 2;
    if (dist(src_x(tau), src_y(tau), obs_x(ti), obs_y(ti)) > (ti - tau) * sonic):
      ub = tau
    else:
      lb = tau
  signal.append(org(tau) / ((ti - tau) * gain + 1))

play(signal)

# アニメーション
fig = plt.figure()
ims = []
for ti in t[::step]:
  im = plt.plot(src_x(ti), src_y(ti), 'ro', obs_x(ti), obs_y(ti), 'bo')
  ims.append(im)
ani = animation.ArtistAnimation(fig, ims, interval = 1000 / fs * step)
plt.show()
