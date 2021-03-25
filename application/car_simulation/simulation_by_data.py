# -*- coding: utf-8 -*-
# @Time     : 2021/3/23 16:56
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : simulation_by_data.py
# @Version  : Python 3.8.5 +

"""
1. Load csv from files
2. Initialize the model
3. Rendering the background
4. Initialize the background
5. Opengl to bmp
6. bmp to gif

:Target: Input a list of data, output a gif pic or js animation
"""
from application import GLWindow

ANGLE = 0
FRAME_RATE = 20
FPS = 60

DATAPATH = [
    './data/2021-03-24-16-29-57-Collision.csv',
    './data/2021-03-24-16-31-03-Collision.csv',
    './data/2021-03-24-16-32-44-Collision.csv',
]


def mainloop():
    x_correction = 0.01171875
    y_correction = -0.02734375
    application = GLWindow(x_correction, y_correction, path=DATAPATH[2])
    application.run()


if __name__ == '__main__':
    mainloop()
    exit()


