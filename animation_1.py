#!/usr/bin/env python3.6
import random , string , time , sys

st = "()[]"
# st = string.punctuation
sys.stdout.write("Starting hack............ ")
for _ in range(100):
	# sys.stdout.write(random.choice(st))
	print(random.choice(st) , end="" , flush=True)#, end="\r"
	time.sleep(0.1)
	sys.stdout.write("\b")
	# sys.stdout.flush()

sys.stdout.write("\n")
# print("flusingin" , flush=True)
# time.sleep(0.5)

# for x in range (0,5):  
#     b = "Loading" + "." * x
#     print (b, end="\r")
#     time.sleep(1)

# msg = 'I am going to erase this line from the console window.'
# sys.stdout.write(msg); sys.stdout.flush()
# time.sleep(1)

# sys.stdout.write('\r' + ' '*len(msg))
# sys.stdout.flush()
# time.sleep(0.5)
# print()

