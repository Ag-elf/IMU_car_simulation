# -*- coding: utf-8 -*-
# @Time     : 2021/3/24 10:17
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : application.py
# @Version  : Python 3.8.5 +

import pandas as pd
import sencyber.tools as tools
import math

from OpenGL.GL import *
from OpenGL.GLUT import *
from PIL import Image
from OpenGL.raw.WGL.EXT.swap_control import wglSwapIntervalEXT


class GLWindow:
    def __init__(self, x_correction=0, y_correction=0, path='2021-03-23-14-15-45-Collision-processed.csv', ):
        self.previous_time = -1

        # Acc correction_data, in order to avoid drifting
        # ToDo: Better Algorithm needed
        self.x_correction = x_correction
        self.y_correction = y_correction

        # Car Speed
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.speed_z = 0.0

        # Car Position
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        # Previous Position
        self.x_temp = 0.0
        self.y_temp = 0.0
        self.z_temp = 0.0

        # Car Euler Angle
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0

        # Magwick implementation of Mahony AHRS
        self.position = tools.PositionAHRS()

        # OpenGL Initialization
        self.GL_init()

        """
        Data Loading
        
        Note: the acc_meter's unit is g (9.8), gyro_meter's unit is degree
        
        The frequency will also affect the results
        In this case, the imu data collection is by 20Hz
        
        CSV column format: acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z
        Position Definition:
        
        Acc_x + --->>> Right  Acc_x - --->>> Left
        Acc_y + --->>> Front  Acc_y - --->>> Back
        Acc_z + --->>> Down   Acc_z - --->>> Up
        
        Sample Data Frame:
         ,    x            ,  y             , z        ,  x  ,    gy ,    gz
        0,    0.01171875   ,  -0.02783203125, 1.0078125,  0.0,    0.0,    0.0
        1,    0.01123046875,  -0.02783203125, 1.0078125,  0.0,    0.0,    0.0
        ...
        ...
        ...
        """
        self.data = pd.read_csv(path)
        try:
            self.data = self.data.drop(columns='Unnamed: 0').values
        except:
            self.data = self.data.values
        self.index = 0
        self.start_index = 0

        self.first = True
        self.play = True
        self.angleList = []
        self.rangeList = []

        self.g = 9.82606

        return

    def GL_init(self):
        """
        OpenGL Initialization
        :return:
        """
        # Please refer to OpenGL Tutorials for this part
        glutInit()
        displayMode = GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH
        glutInitDisplayMode(displayMode)

        glutInitWindowSize(640, 640)
        glutInitWindowPosition(300, 200)
        glutCreateWindow('Car Simulation')

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        self.load_texture()

        glDepthFunc(GL_LEQUAL)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glOrtho(-200, 200, -200, 200, -1000, 1000)

        glutDisplayFunc(self.GL_draw)
        glutIdleFunc(self.GL_idle)
        glutMouseFunc(self.GL_click)

        # Only for windows Vertical synchronization
        wglSwapIntervalEXT(1)
        return

    def load_texture(self):
        """
        Use to load textures
        :return:
        """
        # Please refer to OpenGL Tutorials for this part
        # Load Texture
        img = Image.open('road.jpg')
        img = img.tobytes('raw', 'RGBX', 0, -1)
        # print(img)
        glGenTextures(2)
        glBindTexture(GL_TEXTURE_2D, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, 1169, 300, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    def GL_draw(self):
        """
        OpenGL Drawing Function
        :return:
        """
        # Make the car run within range
        if self.y <= -5:
            self.y += 5
        elif self.y >= 5:
            self.y -= 5

        if self.x >= 1.5:
            self.x -= 1.5
        elif self.x <= -1.5:
            self.x += 1.5

        # Scaling
        x_diff = self.y * 200
        y_diff = self.z * 200
        z_diff = self.x * 200

        # Start Painting
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()

        # Main Axis
        glRotatef(25, 1.0, 0.0, 0.0)
        glRotatef(150, 0.0, 1.0, 0.0)

        # =================================================
        # World Axis
        # Thanks for the author of this blog: https://blog.csdn.net/xufive/article/details/86565130
        glBegin(GL_LINES)

        # Red x axis
        glColor4f(1.0, 0.0, 0.0, 1.0)  # Color Red with alpha 1.0
        glVertex3f(-100, 0.0, 0.0)
        glVertex3f(100, 0.0, 0.0)

        # Green y axis
        glColor4f(0.0, 1.0, 0.0, 1.0)  # Color Green wiht alpha 1.0
        glVertex3f(0.0, -80, 0.0)
        glVertex3f(0.0, 80, 0.0)

        # Blue z axis
        glColor4f(0.0, 0.0, 1.0, 1.0)  # Color Blue
        glVertex3f(0.0, 0.0, -80)
        glVertex3f(0.0, 0.0, 80)

        glEnd()  # End Painting
        # =================================================
        # Moving the ground instead of moving the car to create the animation
        # Paint Ground
        glBindTexture(GL_TEXTURE_2D, 1)
        glBegin(GL_QUADS)
        glColor3f(1, 1, 1)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(3000 + x_diff,   -25 + y_diff,  300 + z_diff)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(3000 + x_diff,   -25 + y_diff, -300 + z_diff)
        glTexCoord2f(6.0, 1.0)
        glVertex3f(-3000 + x_diff,  -25 + y_diff, -300 + z_diff)
        glTexCoord2f(6.0, 0.0)
        glVertex3f(-3000 + x_diff,  -25 + y_diff,  300 + z_diff)
        glEnd()
        # =================================================
        # Fit roll pitch yaw to main axis
        # Note: the car axis definition is different from the main axis
        # Car axis ref:       y    z    x
        glRotatef(self.yaw,   0.0, 1.0, 0.0)
        glRotatef(self.roll,  1.0, 0.0, 0.0)
        glRotatef(self.pitch, 0.0, 0.0, 1.0)

        # =================================================
        # Drawing the Car
        # Thanks for the author of this blog: https://blog.csdn.net/xiaosidi/article/details/79308932
        # Car Bottom
        glBegin(GL_POLYGON)
        glColor3f(0.1, 0.1, 0.8)
        glVertex3f(-40.0, 0.0, 15.0)
        glVertex3f(40.0, 0.0, 15.0)
        glColor3f(1, 0.5, 0.8)
        glVertex3f(40.0, -15.0, 15.0)
        glVertex3f(-40.0, -15.0, 15.0)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(0.3, 0.2, 0.5)
        glVertex3f(40.0, 0.0, -15.0)
        glVertex3f(40.0, 0.0, 15.0)
        glVertex3f(40.0, -15.0, 15.0)
        glVertex3f(40.0, -15.0, -15.0)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(0.3, 0.1, 0.3)
        glVertex3f(-40.0, 0.0, -15.0)
        glVertex3f(-40.0, 0.0, 15.0)
        glVertex3f(-40.0, -15.0, 15.0)
        glVertex3f(-40.0, -15.0, -15.0)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(0.1, 0.1, 0.8)
        glVertex3f(-40.0, 0.0, -15.0)
        glVertex3f(40.0, 0.0, -15.0)
        glColor3f(1, 0.5, 0.8)
        glVertex3f(40.0, -15.0, -15.0)
        glVertex3f(-40.0, -15.0, -15.0)
        glEnd()

        # =================================================
        # Car Body
        glBegin(GL_POLYGON)
        glColor3f(0, 0, 1)
        glVertex3f(-40.0, 0.0, 15.0)
        glVertex3f(-40.0, 0.0, -15.0)
        glVertex3f(40.0, 0.0, -15.0)
        glVertex3f(40.0, 0.0, 15.0)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(0.8, 0.5, 0.2)
        glVertex3f(-40.0, -15.0, 15.0)
        glVertex3f(-40.0, -15.0, -15.0)
        glVertex3f(40.0, -15.0, -15.0)
        glVertex3f(40.0, -15.0, 15.0)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(0, 0, 1)
        glVertex3f(-20.0, 0.0, 15.0)
        glVertex3f(-10.0, 10.0, 15.0)
        glVertex3f(20.0, 10.0, 15.0)
        glVertex3f(25.0, 0.0, 15.0)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(0, 0, 1)
        glVertex3f(-20.0, 0.0, -15.0)
        glVertex3f(-10.0, 10.0, -15.0)
        glVertex3f(20.0, 10.0, -15.0)
        glVertex3f(25.0, 0.0, -15.0)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(0, 1, 1)
        glVertex3f(-10.0, 10.0, 15.0)
        glVertex3f(-10.0, 10.0, -15.0)
        glVertex3f(20.0, 10.0, -15.0)
        glVertex3f(20.0, 10.0, 15.0)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(0.5, 0.8, 0.8)
        glVertex3f(-10.0, 10.0, 15.0)
        glVertex3f(-20.0, 0.0, 15.0)
        glVertex3f(-20.0, 0.0, -15.0)
        glVertex3f(-10.0, 10.0, -15.0)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(0, 0.5, 0.5)
        glVertex3f(20.0, 10.0, 15.0)
        glVertex3f(20.0, 10.0, -15.0)
        glVertex3f(25.0, 0.0, -15.0)
        glVertex3f(25.0, 0.0, 15.0)
        glEnd()

        glBegin(GL_POLYGON)
        glColor3f(0, 0, 1)
        glVertex3f(-30.0, -15.0, 15.0)
        glVertex3f(-30.0, -15.0, -15.0)
        glVertex3f(30.0, -15.0, -15.0)
        glVertex3f(30.0, -15.0, 15.0)
        glEnd()

        # =================================================
        # Wheel
        glColor3f(0.2, 0.2, 0.2)
        glTranslated(-20.0, -15.0, 15.0)
        glutSolidTorus(2, 5, 5, 100)
        glTranslated(0.0, 0.0, -30.0)
        glutSolidTorus(2, 5, 5, 100)
        glTranslated(45.0, 0.0, 0.0)
        glutSolidTorus(2, 5, 5, 100)
        glTranslated(0.0, 0.0, 30.0)
        glutSolidTorus(2, 5, 5, 100)

        glPopMatrix()
        glutSwapBuffers()

    def GL_idle(self):
        """
        OpenGL Idle Function
        First play using    update
        Replay using        update_by_saved
        :return:
        """
        # Load the GPU time to calculate frame
        times = glutGet(GLUT_ELAPSED_TIME)

        # Calculate the right frame to display
        index = math.floor(times / 50) - 20

        # Playing now
        if self.play:
            # First time running
            if self.first:
                if index <= 0 or self.index == index:
                    # Note that we have turned on Vertical synchronization
                    # 60hz on my screen, while data is sampled by 20hz
                    # Do nothing but wait if it's not time to update
                    glutPostRedisplay()
                else:
                    # Update every 3 frame
                    self.index = index
                    self.update()
                    glutPostRedisplay()
            # Replay
            else:
                if index <= self.start_index or index == self.index + self.start_index:
                    glutPostRedisplay()
                else:
                    self.index = index - self.start_index
                    self.update_by_saved()
                    glutPostRedisplay()
        # Stop Playing
        else:
            glutPostRedisplay()

    def GL_click(self, button, state, x, y):
        """
        OpenGL Click Function
        :param button:
        :param state:
        :param x:
        :param y:
        :return:
        """
        # print("Clicked")
        if not self.first and button == GLUT_LEFT_BUTTON and state == GLUT_UP:
            self.x = 0
            self.y = 0
            self.z = 0
            # print("OK")
            self.first = False
            self.play = True
            times = glutGet(GLUT_ELAPSED_TIME)
            self.start_index = math.floor(times / 50) - 15
            self.index = 0

    def update(self):
        """
        This function is used to update the data by the loaded file
        """
        # ToDo A better algorithm to scale and filter out the signal for calculating postions (Kalman Filter maybe?)
        # Load Data
        try:
            dat = self.data[self.index]
        except IndexError:
            self.play = False
            self.first = False
            return

        # ========================================================
        # AHRS for angles
        # (x, y, z), (gx, gy, gz)
        self.position.update((dat[0], dat[1], dat[2]), (dat[3], dat[4], dat[5]))

        if self.z >= 0:
            self.z = 0
            self.speed_z = 0

        # ========================================================
        # Self Correction For Static States

        # Processing Acc Data to Position
        # The car should be viewed as static in this case
        # Note again! The acc_meter's unit is g (9.8)
        total = dat[0] * dat[0] + dat[1] * dat[1] + dat[2] * dat[2]

        # The threshold is learned in the data:
        # 1. Take several lines of data where you think the car should be static
        # 2. Calculate x^2 + y^2 + z^2
        # 3. Figure out the threshold for your data.
        if 1.016 <= total <= 1.017:
            self.speed_y -= self.speed_y / 5
            self.speed_x -= self.speed_x / 5

        # ========================================================
        # Acc Correction

        # Small euler rpy angles leading to acc drifting
        # Compensation data coming from input
        dat[0] -= self.x_correction
        dat[1] -= self.y_correction

        # Acc Compensation.
        # Only if abs(acc_y) >= 20, try to scale acc_y
        if abs(dat[1] * 9.82606) >= 20:
            dat[1] *= 3/4

        # ========================================================
        # Position update, physics
        # Formula: d = d + v t + 1/2 a t^2
        self.x += 1 / 2 * (dat[0]) * 1/20 * 1/20 * 9.82606 + self.speed_x * 1/20
        self.x_temp = self.x

        self.y += 1 / 2 * (dat[1]) * 1 / 20 * 1 / 20 * 9.82606 + self.speed_y * 1 / 20
        self.y_temp = self.y

        self.z += 1 / 2 * (dat[2]) * 1 / 20 * 1 / 20 * 9.82606 + self.speed_z * 1 / 20
        self.z_temp = self.z

        # Speed Update
        # Formula: v = v + a t
        self.speed_x += dat[0] * 9.82606 * 1/20
        self.speed_y += dat[1] * 9.82606 * 1/20
        self.speed_z += dat[2] * 9.82606 * 1/20

        # ========================================================
        # Data Compensation: in order to avoid being out of range
        # ToDo There may be a better algorithm for this part.
        if self.speed_y <= -0.4:
            self.speed_y += 0.3

        if self.speed_x <= -0.4:
            self.speed_x += 0.3
        elif self.speed_x >= 0.4:
            self.speed_x -= 0.3

        # ========================================================
        # Get Euler Angle
        self.pitch, self.roll, self.yaw = self.position.get_euler()

        # Radian to Degree
        self.pitch = self.pitch / math.pi * 180
        self.roll = self.roll / math.pi * 180
        self.yaw = self.yaw / math.pi * 180

        # Save in the list for replay
        self.angleList.append((self.pitch, self.roll, self.yaw))
        self.rangeList.append((self.x, self.y, self.z))

    def update_by_saved(self):
        """
        Replay update
        """
        try:
            dat = self.angleList[self.index]
            dat2 = self.rangeList[self.index]
        except IndexError:
            self.play = False
            return
        self.pitch, self.roll, self.yaw = dat
        self.x, self.y, self.z = dat2

    def run(self):
        """
        Start the OpenGL function
        """
        glutMainLoop()
