from multiprocessing import process
import multiprocessing
import time
import os



def test_worker():
    print("Start process {0}...".format(os.getpid()))
    for index in range(10, 0, -1):
        time.sleep(1)
        print("process{1}-count[{0}]th  ...".format(index, os.getpid()))
    print("End process {0}".format(os.getpid()))


def main():
    process_list = []
    worker1 = multiprocessing.Process(target=test_worker)
    worker2 = multiprocessing.Process(target=test_worker)
    worker3 = multiprocessing.Process(target=test_worker)
    process_list.append(worker1)
    process_list.append(worker2)
    process_list.append(worker3)

    for worker in process_list:
        worker.start()

    running_flag = True
    while running_flag:
        running_flag = False
        for worker in process_list:
            if worker.is_alive():
                running_flag = True

    print("End all processes ")


if __name__ == '__main__':
    main()