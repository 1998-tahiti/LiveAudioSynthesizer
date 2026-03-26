import pyaudio
import numpy as np
import tkinter as Tk
import matplotlib.figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import animation
import matplotlib
from ks_vibrato import KarplusStrong, Vibrato

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading

# Use TkAgg backend
matplotlib.use('TkAgg')

# Audio & DSP parameters
BLOCKLEN = 256
CHANNELS = 1
RATE = 8000
MAXVALUE = 2 ** 15 - 1

# Vibrato setup
VIBRATO_F0 = 1
VIBRATO_WIDTH = 0.0
VIBRATO_BUFFER_LEN = 1024
vibrato_effect = Vibrato(
    rate=RATE,
    vibrato_f0=VIBRATO_F0,
    vibrato_width=VIBRATO_WIDTH,
    buffer_len=VIBRATO_BUFFER_LEN
)

# Karplus–Strong strings
string_tuning = {
    'a': ('E4', 329.63), 's': ('B3', 246.94),
    'd': ('G3', 196.00), 'f': ('D3', 146.83),
    'g': ('A2', 110.00), 'h': ('E2', 82.41)
}
DAMPING = 0.996
ks_strings = {
    k: KarplusStrong(n, f, RATE, damping=DAMPING)
    for k, (n, f) in string_tuning.items()
}

# PyAudio for local playback
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=RATE,
    output=True,
    frames_per_buffer=BLOCKLEN
)

# Flask-SocketIO setup
app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def on_connect():
    print("Web client connected — streaming will start.")
    emit('parameter_update', {
        'vibrato_width': VIBRATO_WIDTH,
        'vibrato_f0': VIBRATO_F0,
        'damping': DAMPING
    })


@socketio.on('control')
def handle_control(data):
    cmd = data['command']
    process_command(cmd)


# Tkinter GUI
root = Tk.Tk()
root.title("DSP String Synthesizer")

active_triggers = set()


def update_status(msg):
    socketio.emit('status', {'message': msg})


def update_parameters():
    socketio.emit('parameter_update', {
        'vibrato_width': VIBRATO_WIDTH,
        'vibrato_f0': VIBRATO_F0,
        'damping': DAMPING
    })


def process_command(cmd):
    global VIBRATO_WIDTH, VIBRATO_F0, DAMPING
    if cmd == 'q':
        update_status("Good bye")
        root.quit()
    elif cmd == ']':
        VIBRATO_WIDTH = min(0.1, VIBRATO_WIDTH + 0.005)
        vibrato_effect.set_width(VIBRATO_WIDTH)
        update_status(f"Vibrato Width: {VIBRATO_WIDTH:.3f}")
    elif cmd == '[':
        VIBRATO_WIDTH = max(0, VIBRATO_WIDTH - 0.005)
        vibrato_effect.set_width(VIBRATO_WIDTH)
        update_status(f"Vibrato Width: {VIBRATO_WIDTH:.3f}")
    elif cmd == '1':
        VIBRATO_F0 = min(20, VIBRATO_F0 + 1)
        vibrato_effect.set_f0(VIBRATO_F0)
        update_status(f"Vibrato Frequency: {VIBRATO_F0} Hz")
    elif cmd == '2':
        VIBRATO_F0 = max(0.1, VIBRATO_F0 - 1)
        vibrato_effect.set_f0(VIBRATO_F0)
        update_status(f"Vibrato Frequency: {VIBRATO_F0} Hz")
    elif cmd == '3':
        DAMPING = min(0.999, DAMPING + 0.01)
        for ks in ks_strings.values():
            ks.set_damping(DAMPING)
        update_status(f"Damping: {DAMPING:.3f}")
    elif cmd == '4':
        DAMPING = max(0.700, DAMPING - 0.01)
        for ks in ks_strings.values():
            ks.set_damping(DAMPING)
        update_status(f"Damping: {DAMPING:.3f}")
    else:
        key = cmd.lower()
        if key in ks_strings:
            active_triggers.add(key)
            update_status(f"Plucked {key.upper()} ({ks_strings[key].note})")
    update_parameters()


root.bind("<Key>", lambda e: process_command(e.char))

# Matplotlib setup
fig = matplotlib.figure.Figure(figsize=(8, 8))
axes = [fig.add_subplot(2, 2, i + 1) for i in range(4)]
lines = []
t = np.arange(BLOCKLEN) * (1000.0 / RATE)
f_axis = np.arange(BLOCKLEN // 2 + 1) * RATE / BLOCKLEN

titles = ["Input Time", "Output Time", "Input FFT", "Output FFT"]
ylims = [(-MAXVALUE, MAXVALUE), (-MAXVALUE, MAXVALUE), (0, 1000), (0, 1000)]

for ax, title, ylim in zip(axes, titles, ylims):
    ax.set_title(title)
    if "Time" in title:
        ax.set_xlim(0, 1000.0 * BLOCKLEN / RATE)
    else:
        ax.set_xlim(0, RATE / 2)
    ax.set_ylim(*ylim)
    size = BLOCKLEN if "Time" in title else (BLOCKLEN // 2 + 1)
    line, = ax.plot(np.zeros(size))
    lines.append(line)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()


def my_init():
    return lines


def my_update(frame):
    global active_triggers
    y_in = np.zeros(BLOCKLEN)
    for k, ks in ks_strings.items():
        if k in active_triggers:
            ks.pluck(amp=8000.0)  # Reduced amplitude to prevent distortion
        y_in += ks.process_block(BLOCKLEN)
    active_triggers.clear()

    y_out = vibrato_effect.process_block(y_in.copy()) if VIBRATO_WIDTH > 0 else y_in

    # Apply soft clipping to prevent distortion
    y_out = np.tanh(y_out / MAXVALUE) * MAXVALUE

    Ys = [
        y_in,
        y_out,
        np.abs(np.fft.rfft(y_in) / BLOCKLEN),
        np.abs(np.fft.rfft(y_out) / BLOCKLEN)
    ]
    for line, Y in zip(lines, Ys):
        line.set_ydata(Y)

    y_clip = np.clip(y_out, -MAXVALUE, MAXVALUE).astype('int16')
    stream.write(y_clip.tobytes(), BLOCKLEN)
    socketio.emit('audio_data', {'data': y_clip.tobytes()})

    return lines


ani = animation.FuncAnimation(
    fig, my_update, init_func=my_init,
    interval=20, blit=True
)


# Start Flask-SocketIO in background
def _run_flask():
    socketio.run(
        app,
        host='127.0.0.1',
        port=5000,
        debug=False,
        allow_unsafe_werkzeug=True
    )


threading.Thread(target=_run_flask, daemon=True).start()

# Start Tk mainloop once
Tk.mainloop()

# Cleanup
stream.stop_stream()
stream.close()
p.terminate()
print("* Finished")