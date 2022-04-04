import serial
import time
import threading
import os
import queue


COM = os.environ.get('PORT', '/dev/ttyACM0')
BAUD = 115200

ser = serial.Serial(COM, BAUD, timeout = .1)

print('Waiting for device')
time.sleep(3)
print(ser.name)
print("Press CTRL+C to exit")

resp_q = queue.Queue()
read_enabled = True

def read_thread():
	while read_enabled:
		val = str(ser.readline().decode().strip('\r\n'))#Capture serial output as a decoded string
		if(val):
			# print("\r", val, end="\n", flush=True)
			resp_q.put(val)




def flush_queue():
	while resp_q.empty():
		time.sleep(0.1)

	while not resp_q.empty():
		yield resp_q.get(True)
		time.sleep(0.1)
		# print("\r", resp_q.get(True), end="\n", flush=True)


def print_queue():
	for line in flush_queue():
		print("\r", line, end="\n", flush=True)


def extract():
	code = communicate("L0000")
	mode = 'w'
	ff_twice = False
	for i in range(30):
		with open("dis.dis", mode) as c:
			c.write(code + "\r\n")
		# time.sleep(0.1)
		code = communicate("")
		mode = 'a'
		if code.strip().endswith("FFFF") and ff_twice:
			break
		if code.strip().endswith("FFFF"):
			ff_twice = True
	return "Done."


def communicate(cmd):
	if cmd == "Extract":
		return extract()

	tosend = (cmd + '\r\n').encode()
	ser.writelines([tosend])
	return "\r\n".join([line for line in flush_queue()])





if __name__ == '__main__':
	t = threading.Thread(target=read_thread, daemon=True)
	t.start()
	time.sleep(1)
	print_queue()
	while True:
		try:
			print(communicate(input(">> ")))
		except (Exception, KeyboardInterrupt) as e:
			print(e)
			break

	print('Exit')
	read_enabled = False
	t.join()

