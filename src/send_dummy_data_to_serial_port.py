import time
import serial
import sys

port = sys.argv[1] # '/dev/pts/2'

ser = serial.Serial(port, 115200, timeout=0.050)
count = 0

while 1:
    ser.write((str(time.time())+'\n').encode('utf-8'))
    time.sleep(1)
    count += 1
