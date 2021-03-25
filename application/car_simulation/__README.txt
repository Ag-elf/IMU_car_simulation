This is an OpenGL-based project, simulating car movement based on IMU data.

Usage:
python3 simulation_by_data.py

You can change the specific data file by changing the path in simulation_by_data.py
If you want to use your own csv data. Please check the format below.

=========================================================================
Problem Definition

1. Load the saved imu data from files.
2. Simulate the car movement based on the acc_meter and gyro_meter.
3. Replay the euler angles and positions of the car.

=========================================================================
CSV Definition and format

The acc_meter's unit is g (9.8 m/s^2), gyro_meter's unit is degree (°/s)

The frequency will also affect the results.
In this case, the imu data was collected by 20Hz

CSV columns: acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z

Position Definition:
Acc_x + --->>> Right   Acc_x - --->>> Left
Acc_y + --->>> Forward Acc_y - --->>> Back
Acc_z + --->>> Down    Acc_z - --->>> Up

Gyroscope readings are based on the specific axis.
E.g. gyro_x means the angular speed of spinning around axis x

Sample Data Frame:
 ,    x            ,  y             , z        ,  gx ,    gy ,    gz
0,    0.01171875   ,  -0.02783203125, 1.0078125,  0.0,    0.0,    0.0
1,    0.01123046875,  -0.02783203125, 1.0078125,  0.0,    0.0,    0.0
2,    0.0102504481 ,  -0.02762115841, 1.0076341,  0.0,    0.0,    0.0
...
...
...
=========================================================================
NOTES: 
Some of OpenGL codes are only running under windows 10. (Check application.py for detailed information)
Linux or MacOS may have problems to run the code.
