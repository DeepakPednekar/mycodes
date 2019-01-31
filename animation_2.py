#!/usr/bin/env python3.6
import time , string , threading

def ip():
	st = "abc"
	st = string.ascii_lowercase
	st = st[:10]
	st = "loading.........."
	le = st.__len__()
	print("\r" , flush=True , end="")
	count = 0

	for each in range(100):

		if count==le:
			print(st+"\b\b", flush=True, end="")
			count=0
		else:
			print(st[:count]+st[count].upper() , flush=True, end="")#+st[count:]
			count+=1

		time.sleep(0.1)
		print("\r" , flush=True, end="")


threading.Thread(target=ip).start()












