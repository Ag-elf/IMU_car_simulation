# -*- coding: utf-8 -*-
# @Time     : 2021/3/22 13:20
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : tools.py
# @Version  : Python 3.8.5 +
import math
from queue import Queue


# This queue will drop item automatically when queue is full.
class AutoQueue:
    # Initializing
    def __init__(self, length: int):
        self.queue = Queue()
        self.length = length

    def put(self, item):
        """
        This function is called when you want to put an item into the queue
        :param item: item, can be anything you want
        :return:
        """
        self.queue.put(item)
        if self.queue.qsize() > self.length:
            self.queue.get()

    def get(self):
        """
        This function is used to get the item in the queue. (Item consumed when calling the function)
        :return:
        """
        item = self.queue.get()
        return item

    def clean(self):
        """
        Clean the queue
        :return:
        """
        self.queue.queue.clear()

    def getQueue(self):
        """
        Get the actual list of items for the queue.
        :return:
        """
        return self.queue.queue


# This class is a built in Mahony filter used to calculate the positioning information
class PositionAHRS:
    def __init__(self):
        self.beta = 0
        self.pi = 0
        self.q = [1.0, 0.0, 0.0, 0.0]

    def update(self, acc, w, SamplePeriod=1 / 20, Beta=0.1):
        """
        This function is used to update the quaternion
        :param acc:             (x, y, z)       :acceleration
        :param w:               (wx, wy, wz)    :gyroscope readings
        :param SamplePeriod:    1/20 by default :hz
        :param Beta:            0.1 by default  :hyper parameter
        :return:
        """
        ax, ay, az = acc
        gx, gy, gz = w
        gx = gx / 180 * math.pi
        gy = gy / 180 * math.pi
        gz = gz / 180 * math.pi
        q1 = self.q[0]
        q2 = self.q[1]
        q3 = self.q[2]
        q4 = self.q[3]

        _2q1 = 2 * q1
        _2q2 = 2 * q2
        _2q3 = 2 * q3
        _2q4 = 2 * q4
        _4q1 = 4 * q1
        _4q2 = 4 * q2
        _4q3 = 4 * q3
        _8q2 = 8 * q2
        _8q3 = 8 * q3
        q1q1 = q1 * q1
        q2q2 = q2 * q2
        q3q3 = q3 * q3
        q4q4 = q4 * q4

        norm = math.sqrt(ax * ax + ay * ay + az * az)
        if norm == 0.0:
            return
        norm = 1 / norm
        ax *= norm
        ay *= norm
        az *= norm

        s1 = _4q1 * q3q3 + _2q3 * ax + _4q1 * q2q2 - _2q2 * ay
        s2 = _4q2 * q4q4 - _2q4 * ax + 4 * q1q1 * q2 - _2q1 * ay - _4q2 + _8q2 * q2q2 + _8q2 * q3q3 + _4q2 * az
        s3 = 4 * q1q1 * q3 + _2q1 * ax + _4q3 * q4q4 - _2q4 * ay - _4q3 + _8q3 * q2q2 + _8q3 * q3q3 + _4q3 * az
        s4 = 4 * q2q2 * q4 - _2q2 * ax + 4 * q3q3 * q4 - _2q3 * ay

        norm = 1 / math.sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4)
        s1 *= norm
        s2 *= norm
        s3 *= norm
        s4 *= norm

        qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - Beta * s1
        qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - Beta * s2
        qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - Beta * s3
        qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - Beta * s4

        q1 += qDot1 * SamplePeriod
        q2 += qDot2 * SamplePeriod
        q3 += qDot3 * SamplePeriod
        q4 += qDot4 * SamplePeriod

        norm = 1 / math.sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4)

        self.q[0] = q1 * norm
        self.q[1] = q2 * norm
        self.q[2] = q3 * norm
        self.q[3] = q4 * norm
        return

    def get_euler(self):
        """
        From quaternion to euler angles roll, pitch, yaw
        :return: alpha, beta, theta
        """
        alpha = math.atan2(2 * (self.q[0] * self.q[1] + self.q[2] * self.q[3]),
                           1 - 2 * (self.q[1] * self.q[1] + self.q[2] * self.q[2]))
        beta = math.asin(2 * (self.q[0] * self.q[2] - self.q[3] * self.q[1]))
        theta = math.atan2(2 * (self.q[0] * self.q[3] + self.q[1] * self.q[2]),
                           1 - 2 * (self.q[2] * self.q[2] + self.q[3] * self.q[3]))

        return alpha, beta, theta


# Python Implementation of matlab filter
def filter_matlab(b, a, x):
    y = [b[0] * x[0]]
    for i in range(1, len(x)):
        y.append(0)
        for j in range(len(b)):
            if i >= j:
                y[i] = y[i] + b[j] * x[i - j]
                j += 1
        for k in range(len(b) - 1):
            if i > k:
                y[i] = (y[i] - a[k + 1] * y[i - k - 1])
                k += 1
        i += 1
    return y
