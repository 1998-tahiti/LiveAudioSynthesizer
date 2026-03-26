import numpy as np
import matplotlib
import matplotlib.figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import animation


class GraphManager:
    def __init__(self, root, enable_graphs, blocklen, rate, maxvalue):
        self.enable_graphs = enable_graphs
        self.BLOCKLEN = blocklen
        self.RATE = rate
        self.MAXVALUE = maxvalue

        if not self.enable_graphs:
            return

        matplotlib.use('TkAgg')
        self.fig = matplotlib.figure.Figure(figsize=(8, 8))
        self.axes = [self.fig.add_subplot(2, 2, i + 1) for i in range(4)]
        self.lines = []
        t = np.arange(self.BLOCKLEN) * (1000.0 / self.RATE)
        f_axis = np.arange(self.BLOCKLEN // 2 + 1) * self.RATE / self.BLOCKLEN

        titles = ["Input Time", "Output Time", "Input FFT", "Output FFT"]
        ylims = [(-self.MAXVALUE, self.MAXVALUE), (-self.MAXVALUE, self.MAXVALUE), (0, 1000), (0, 1000)]

        for ax, title, ylim in zip(self.axes, titles, ylims):
            ax.set_title(title)
            if "Time" in title:
                ax.set_xlim(0, 1000.0 * self.BLOCKLEN / self.RATE)
            else:
                ax.set_xlim(0, self.RATE / 2)
            ax.set_ylim(*ylim)
            size = self.BLOCKLEN if "Time" in title else (self.BLOCKLEN // 2 + 1)
            line, = ax.plot(np.zeros(size))
            self.lines.append(line)

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

    def update_graphs(self, y_in, y_out):
        if not self.enable_graphs:
            return

        Ys = [
            y_in,
            y_out,
            np.abs(np.fft.rfft(y_in) / self.BLOCKLEN),
            np.abs(np.fft.rfft(y_out) / self.BLOCKLEN)
        ]
        for line, Y in zip(self.lines, Ys):
            line.set_ydata(Y)

    def start_animation(self, callback):
        return animation.FuncAnimation(
            self.fig,
            lambda frame: callback(),
            init_func=lambda: self.lines if self.enable_graphs else None,
            interval=20,
            blit=True
        )
