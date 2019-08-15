import threading
import time


def print_hello(num):
    for i in range(4):
        time.sleep(0.5)
        print("Hello {num}")


def print_hi(num):
    for i in range(4):
        time.sleep(0.7)
        print("Hi {num}")


for num in range(10):
    t1 = threading.Thread(target=print_hello, args=(num,))
    t1.start()
for num in range(10):
    t2 = threading.Thread(target=print_hi, args=(num,))
    t2.start()
