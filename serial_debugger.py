import serial
import time
import threading
import os

COM = os.environ.get('PORT', '/dev/ttyUSB0')
BAUD = 115200

ser = serial.Serial(COM, BAUD, timeout = .1)

print('Waiting for device')
time.sleep(3)
print(ser.name)
print("Press CTRL+C to exit")

read_enabled = True

def read_thread():
	while read_enabled:
		val = str(ser.readline().decode().strip('\r\n'))#Capture serial output as a decoded string
		if(val):
			print("\r", val, end="\n", flush=True)


if __name__ == '__main__':
	t = threading.Thread(target=read_thread, daemon=True)
	t.start()
	while True:
		try:
			time.sleep(2)
			tosend = (input(">> ") + '\r\n').encode()
			# if tosend == b'\r\n': continue
			ser.writelines([tosend])
		except (Exception, KeyboardInterrupt) as e:
			print(e)
			break

	print('Exit')
	read_enabled = False
	t.join()

