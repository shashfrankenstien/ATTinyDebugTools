import serial
import tkinter as tk
import time
from collections import deque, namedtuple


PORT = '/dev/ttyUSB0'
BAUD = 9600
AMPLITUDE_MAX = 1024
AMPLITUDE_MAX_VOLTAGE = 3.3 # volts
GRID_RESOLUTION = 0.5 # volts
GRID_RESOLUTION_PIXELS = GRID_RESOLUTION * AMPLITUDE_MAX / AMPLITUDE_MAX_VOLTAGE

DEFAULT_SPEED_SCALING = 3

WINDOW_HEIGHT = 500
WINDOW_WIDTH = 1400

root = tk.Tk()
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

Coord = namedtuple('Coord', ['x','y'])

def readInt(port):
    return int.from_bytes(port.read(), 'little')


def readTriplet(port):
    value = -1
    while (port.in_waiting >= 3):
        data = readInt(port)
        if (data == 255):
            value = (readInt(port) << 8) | (readInt(port))
    return value


def readQuintuplet(port):
    value = -1
    value2 = -1
    while (port.in_waiting >= 4):
        data = readInt(port)
        if (data == 255):
            value = (readInt(port) << 8) | (readInt(port))
            value2 = (readInt(port) << 8) | (readInt(port))
    return value, value2



def probe():
    with serial.Serial(PORT, BAUD, timeout=10) as port:
        while True:
            while not port.in_waiting:
                pass
            chan1, chan2 = readQuintuplet(port)
            if chan1 != -1 or chan2 != -1:
                yield chan1, chan2



class Stats(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bd=5, bg="black")
        self.period = tk.StringVar(self.master, "-")
        self.freq = tk.StringVar(self.master, "-")
        self.bugs = tk.StringVar(self.master, "0 Bugs")
        self.bug_count = 0
        self.periods_for_mvavg = deque(maxlen=10)  # only holds 10 items

        label = tk.Label(self, textvariable=self.period, height=1, bg="black", fg="white", justify="right")
        label.pack()
        label = tk.Label(self, textvariable=self.freq, height=1, bg="black", fg="white", justify="right")
        label.pack()
        label = tk.Label(self, textvariable=self.bugs, height=1, bg="black", fg="white", justify="right")
        label.pack()


    def set_period(self, per):
        self.period.set(f"{per*1000:.2f} ms")
        self.freq.set(f"{1/per:.2f} Hz")
        self.periods_for_mvavg.append(per)
        if len(self.periods_for_mvavg) == 10:
            mvavg = sum(self.periods_for_mvavg) / 10
            if per / mvavg < 0.8 or per / mvavg > 1.2:
                self.bug_count += 1
                self.bugs.set(f"{self.bug_count} Bugs")
                print(mvavg, per)



class WaveCanvas(tk.Canvas):

    def __init__(self, parent, width, height, x_scaling=DEFAULT_SPEED_SCALING):
        super().__init__(parent, bg='black', width=width, height=height, bd=0)
        self.height = height
        self.width = width
        self.x_scaling = x_scaling
        self.init_wave()
        self.pack(side='left')
        # self.draw_grid()
        self.zero = [
            (height / 4), # channel 0
            3 * (height / 4) # channel 1
        ]
        self.grid_lines = []


    def init_wave(self):
        size = int(self.width / self.x_scaling)
        self.wave = deque(maxlen=size)  # only holds width * self.x_scaling items
        for i in range(size):
            self.wave.append((0,0))

    def resize_wave(self, x_scaling):
        self.x_scaling = x_scaling
        size = int(self.width / self.x_scaling)
        old_wave = self.wave.copy()
        self.wave = deque(maxlen=size)  # only holds width * self.x_scaling items
        for i in range(min(size, len(old_wave))):
            self.wave.append(old_wave.popleft())

    def translate_y(self, y, channel):
        return self.zero[channel] - (y * (self.height/4) / AMPLITUDE_MAX )

    def draw_grid(self):
        if not self.grid_lines:
            for i in range(0, 7):
                self.grid_lines.append(self.translate_y(i * GRID_RESOLUTION_PIXELS, 0))
                self.grid_lines.append(self.translate_y(-i * GRID_RESOLUTION_PIXELS, 0))
                self.grid_lines.append(self.translate_y(i * GRID_RESOLUTION_PIXELS, 1))
                self.grid_lines.append(self.translate_y(-i * GRID_RESOLUTION_PIXELS, 1))

        for y in self.grid_lines:
            self.create_line(0, y, self.width, y, fill="#13330f", dash=(5,15))


    def draw(self):
        self.delete('all')
        prev_c1 = Coord(0, 0)
        prev_c2 = Coord(0, 0)
        for i, (chan1, chan2) in enumerate(self.wave.copy()):
            new_c1 = Coord(i * self.x_scaling, chan1)
            new_c2 = Coord(i * self.x_scaling, chan2)
            self.create_line(prev_c1.x, self.translate_y(prev_c1.y, 0), new_c1.x, self.translate_y(new_c1.y, 0), fill='green')
            self.create_line(prev_c2.x, self.translate_y(prev_c2.y, 1), new_c2.x, self.translate_y(new_c2.y, 1), fill='green')
            prev_c1 = new_c1
            prev_c2 = new_c2
        self.create_line(0, self.zero[0], self.width, self.zero[0], fill="#914646")
        self.create_line(0, self.zero[1], self.width, self.zero[1], fill="#914646")
        self.draw_grid()
        self.update()

    def append(self, signal):
        self.wave.append(signal)
        self.draw()



class Scope(tk.Frame):

    def __init__(self):
        super().__init__()
        self.plot_height = WINDOW_HEIGHT
        self.plot_width = WINDOW_WIDTH - 200

        self.init_ui()
        self.paused = False


    def init_ui(self):
        self.master.title("Oscilloscope")
        self.pack(fill='both', expand=1)

        self.canvas = WaveCanvas(self, height=self.plot_height, width=self.plot_width)

        self.ctrls = tk.Frame(self, bd=5, bg="black")
        self.stats = Stats(self.ctrls)
        self.stats.pack()
        extras = tk.Frame(self.ctrls, height=self.plot_height-20, bg="grey")

        self.pause_btn = tk.Button(extras, command=lambda : self.pause(), text="Pause")
        self.pause_btn.pack()

        self.closer_btn = tk.Button(extras, command=lambda : self.channels_closer(), text="closer")
        self.closer_btn.pack()
        self.farther_btn = tk.Button(extras, command=lambda : self.channels_farther(), text="farther")
        self.farther_btn.pack()

        self.faster_btn = tk.Button(extras, command=lambda : self.channels_faster(), text="faster")
        self.faster_btn.pack()

        self.slower_btn = tk.Button(extras, command=lambda : self.channels_slower(), text="slower")
        self.slower_btn.pack()

        extras.pack(fill="both", expand=True)
        self.ctrls.pack(side="left", fill="both", expand=True)

    def set_period(self, per):
        # bugs = self.stats.bug_count
        self.stats.set_period(per)
        # if bugs != self.stats.bug_count:
        #     self.pause()



    def start(self):
        gen = probe()
        st = 0
        prev_sig1 = 0
        prev_sig2 = 0

        def _update_task():
            nonlocal st, prev_sig1, prev_sig2

            if not self.paused:
                if st==0:
                    st = time.time()

                sig,sig2 = next(gen)

                if sig < (prev_sig1 / 5) and abs(sig-prev_sig1) > 10: # falling edge
                    self.set_period(time.time() - st)
                    st = 0
                try:
                    self.canvas.append((sig, sig2))
                except Exception as e:
                    print(e)
                    import traceback; traceback.print_exc()
                    return

                prev_sig1 = sig
            else:
                st = 0
                time.sleep(0.1)
            self.after(0, _update_task)

        _update_task()
        print("done")

    def pause(self):
        self.paused = not self.paused
        self.pause_btn['text'] = 'Play' if self.paused else 'Pause'


    # UI controls

    def channels_closer(self):
        self.canvas.zero[0] += 4
        self.canvas.zero[1] -= 4

    def channels_farther(self):
        self.canvas.zero[0] -= 4
        self.canvas.zero[1] += 4


    def channels_faster(self):
        self.canvas.resize_wave(self.canvas.x_scaling + 0.5)

    def channels_slower(self):
        self.canvas.resize_wave(self.canvas.x_scaling - 0.5)



if __name__ == '__main__':
    scope = Scope()
    scope.start()
    # root.protocol("WM_DELETE_WINDOW", scope.die)
    root.mainloop()
