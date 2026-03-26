import numpy as np
import math

class KarplusStrong:
    def __init__(self, note, freq, rate, damping=0.996):
        self.note = note
        self.freq = freq
        self.rate = rate
        self.N = max(int(rate / freq), 2)
        self.damping = damping
        self.buffer = [0.0] * self.N

    def pluck(self, amp=10000.0):
        self.buffer = list(np.random.uniform(-amp, amp, self.N))

    def process_block(self, blocklen):
        y = np.zeros(blocklen)
        for n in range(blocklen):
            y_val = self.buffer[0]
            if len(self.buffer) > 1:
                new_val = self.damping * 0.5 * (self.buffer[0] + self.buffer[1])
            else:
                new_val = self.damping * self.buffer[0]
            self.buffer.pop(0)
            self.buffer.append(new_val)
            y[n] = y_val
        return y

    def set_damping(self, new_damping):
        self.damping = new_damping


class Vibrato:
    def __init__(self, rate, vibrato_f0=2, vibrato_width=0.0, buffer_len=1024):
        self.rate = rate
        self.vibrato_f0 = vibrato_f0
        self.vibrato_width = vibrato_width
        self.buffer_len = buffer_len
        self.vibrato_Wd = self.vibrato_width * rate
        self.buffer = [0.0] * buffer_len
        self.i1 = 0
        self.kw = int(0.5 * buffer_len)
        self.sample_index = 0

    def set_width(self, new_width):
        self.vibrato_width = new_width
        self.vibrato_Wd = self.vibrato_width * self.rate

    def set_f0(self, new_f0):
        self.vibrato_f0 = new_f0

    def process_block(self, input_block):
        blocklen = len(input_block)
        output = np.zeros(blocklen)
        for n in range(blocklen):
            x0 = input_block[n]
            vib_kr = self.i1 + self.vibrato_Wd * math.sin(2 * math.pi * self.vibrato_f0 * self.sample_index / self.rate)
            if vib_kr >= self.buffer_len:
                vib_kr -= self.buffer_len
            elif vib_kr < 0:
                vib_kr += self.buffer_len
            kr_prev = int(math.floor(vib_kr))
            frac = vib_kr - kr_prev
            kr_next = kr_prev + 1 if (kr_prev + 1) < self.buffer_len else 0
            y_v = (1 - frac) * self.buffer[kr_prev] + frac * self.buffer[kr_next]
            output[n] = y_v
            self.buffer[self.kw] = x0
            self.i1 = (self.i1 + 1) % self.buffer_len
            self.kw = (self.kw + 1) % self.buffer_len
            self.sample_index += 1
        return output