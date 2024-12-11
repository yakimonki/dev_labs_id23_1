import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button
def calc_freq(length, damp):
    base_freq = np.pi / length
    return np.sqrt(base_freq**2 - damp**2)
def create_pts(length, num_pts):
    return np.linspace(0, length, num_pts)

def update_anim(frame):
    time = frame / 30.0
    freq = calc_freq(params["str_len"], params["damp"])
    y_pts = params["amp"] * np.exp(-params["damp"] * time) * np.cos(freq * time) * np.sin(np.pi * x_pts / params["str_len"])
    line.set_ydata(y_pts)
    return line,
def init_params():
    return {
        "str_len": 1.0,
        "amp": 1.0,
        "damp": 0.1,
        "num_pts": 100
    }
def update_params(val):
    params["str_len"] = sldr_len.val
    params["amp"] = sldr_amp.val
    params["damp"] = sldr_damp.val
    ax.set_xlim(0, params["str_len"])
    ax.set_ylim(-params["amp"], params["amp"])
    global x_pts
    x_pts = create_pts(params["str_len"], params["num_pts"])
    line.set_xdata(x_pts)
    fig.canvas.draw_idle()


def start_anim(event):
    ani.event_source.start()







def reset(event):
    sldr_len.reset()
    sldr_amp.reset()
    sldr_damp.reset()
    ani.event_source.stop()
    update_params(None)
if __name__ == "__main__":
    params = init_params()
    x_pts = create_pts(params["str_len"], params["num_pts"])
    y_pts = params["amp"] * np.sin(np.pi * x_pts / params["str_len"])
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.1, bottom=0.3)
    line, = ax.plot(x_pts, y_pts, lw=2)


    ax.set_xlim(0, params["str_len"])
    ax.set_ylim(-params["amp"], params["amp"])
    ax.set_title("Damped String Oscillations")
    ax.set_xlabel("String Length")
    ax.set_ylabel("Amplitude")

    sldr_len = Slider(plt.axes([0.1, 0.2, 0.65, 0.03]), "Length", 0.5, 2.0, valinit=params["str_len"])
    sldr_amp = Slider(plt.axes([0.1, 0.25, 0.65, 0.03]), "Amplitude", 0.1, 2.0, valinit=params["amp"])
    sldr_damp = Slider(plt.axes([0.1, 0.3, 0.65, 0.03]), "Damping", 0.01, 0.5, valinit=params["damp"])
    btn_start = Button(plt.axes([0.8, 0.2, 0.1, 0.04]), "Start")
    btn_reset = Button(plt.axes([0.8, 0.25, 0.1, 0.04]), "Reset")




    sldr_len.on_changed(update_params)
    sldr_amp.on_changed(update_params)
    sldr_damp.on_changed(update_params)

    btn_start.on_clicked(start_anim)
    btn_reset.on_clicked(reset)
    ani = FuncAnimation(fig, update_anim, frames=600, interval=30, blit=True)




    plt.show()
