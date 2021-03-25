This is an OpenGL-based project, simulating car movement based on IMU data.

Usage:
python3 simulation_by_data.py

You can change the specific data file by changing the path in simulation_by_data.py

If you want to use your own csv data. Please check the following format.

=========================================================================

The acc_meter's unit is g (9.8), gyro_meter's unit is degree

The frequency will also affect the results
In this case, the imu data collected by 20Hz

CSV columns: acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z

Position Definition:
Acc_x + --->>> Right   Acc_x - --->>> Left
Acc_y + --->>> Forward Acc_y - --->>> Back
Acc_z + --->>> Down    Acc_z - --->>> Up

Sample Data Frame:
 ,    x            ,  y             , z        ,  x  ,    gy ,    gz
0,    0.01171875   ,  -0.02783203125, 1.0078125,  0.0,    0.0,    0.0
1,    0.01123046875,  -0.02783203125, 1.0078125,  0.0,    0.0,    0.0
...
...
...

=========================================================================

NOTES: 
Some of OpenGL codes are only running under windows 10. (Check application.py for detailed information)
Linux or MacOS may have problems to run the code.
