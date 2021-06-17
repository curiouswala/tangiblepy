import serial

with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser:
    x = ser.write(b'import os;os.uname()\r')          # read one byte
    for i in range(5):
    	line = ser.readline()
    	print(line)
    	if 'sysname=' in line.decode('utf-8'):
    		break
    line_str = line.decode('utf-8').strip()
    # (sysname='esp32', nodename='esp32', release='1.13.0', version='v1.13 on 2020-09-02', machine='ESP32 module with ESP32')
    firmware_version_str = line_str.split(',')[2]
    # device_firmware_info = eval(dict_str)
    firmware_version = firmware_version_str.split("'")[1]
    print(firmware_version)