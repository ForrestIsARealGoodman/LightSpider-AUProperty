from multiprocessing import Process
from multiprocessing import Queue
from lib.common.Util import *
import threading

import time
import os


class DataSampleClass:
    def __init__(self):
        self.data_a = ""
        self.data_b = ""


def test_worker_process(queue_data):
    process_id = os.getpid()
    data_obj = DataSampleClass()
    print("Start process {0}...".format(process_id))
    for index in range(10, 0, -1):
        time.sleep(1)
        data_str = "process{1}-count[{0}]th  ...".format(index, process_id)
        data_obj.data_a = data_str
        data_obj.data_b = index
        queue_data.put(data_obj)
        #print(data_str)
    print("End process {0}".format(process_id))


def test_worker_thread(queue_data):
    print("Reader thread started")
    while True:
        record = queue_data.get()
        if record is None:  # We send this as a sentinel to tell the listener to quit.
            print("Reader thread exits")
            break
        else:
            debug_print(record.data_a)
            debug_print(record.data_b)


def test_processes():
    q_data = Queue()
    reader = threading.Thread(target=test_worker_thread, args=(q_data,))
    reader.start()
    process_list = []
    worker1 = Process(target=test_worker_process, args=(q_data,))
    worker2 = Process(target=test_worker_process, args=(q_data,))
    worker3 = Process(target=test_worker_process, args=(q_data,))
    process_list.append(worker1)
    process_list.append(worker2)
    process_list.append(worker3)

    for each_worker in process_list:
        each_worker.start()

    for each_worker in process_list:
        each_worker.join()

    q_data.put_nowait(None)
    reader.join()

    print("End all processes ")


if __name__ == '__main__':
    test_processes()
