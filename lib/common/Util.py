import os
from os import path
import sys
import traceback
import time
from decimal import *
import random
from bs4 import BeautifulSoup
from lib.common.URLHandler import *
from datetime import datetime
import re

import logging
import logging.handlers
import logging.config

import inspect
import multiprocessing
import threading
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def get_parser():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-l", "--log",
                        help="debug, info, warning, error, critical",
                        metavar="<log level>",
                        required=False)
    parser.set_defaults(help=False)
    return parser

"""
# initialize project directory
def initialize_sys_path():
    current_dir = os.path.dirname(os.getcwd())
    print("current_dir:", current_dir)
    project_dir = os.path.dirname(current_dir)
    project_dir = path.abspath(project_dir)
    print("project_dir:", project_dir)
    #sys.path.append(project_dir)
    sys.path.append(os.getcwd())
"""


def retrieve_name_ex():
    stacks = inspect.stack()
    try:
        call_func = stacks[1].function
        code = stacks[2].code_context[0]
        start_index = code.strip().index(call_func)
        start_index = code.index("(", start_index + len(call_func)) + 1
        end_index = code.rindex(")", start_index)
        return code[start_index:end_index].strip()
    except:
        return ""


def debug_print(var):
    print("Debug Expression: {} = {}".format(retrieve_name_ex(), var))


def get_project_dir():
    project_name = 'LightSpider-AUProperty'
    root_path = os.path.abspath(os.path.dirname(__file__)).split(project_name)[0]
    project_path = os.path.join(root_path, project_name)
    return project_path


def get_search_config_path():
    search_config = os.path.join(get_project_dir(), "AUPropertySpider.yaml")
    debug_print(get_project_dir())
    return search_config


def get_log_path():
    log_path = os.path.join(get_project_dir(), "log\\AUPropertySpider.log")
    return log_path


def get_data_path_with_date():
    data_path = os.path.join(get_project_dir(), "data\\")
    date_string = datetime.now().strftime("%Y%m%d")
    data_path = data_path + date_string + "\\"
    if not os.path.exists(data_path):
        debug_print(data_path)
        os.mkdir(data_path)
    return data_path


def get_real_estate_data_path():
    data_path = os.path.join(get_project_dir(), "data\\realestate\\")
    return data_path


def get_candidate_suburbs(data_query_suburb):
    url_query_suburbs = "https://auspost.com.au/postcode"
    result_suburbs = []
    rst_content, rst_flag = URLHandlerClass.post_content_from_html(url_query_suburbs, data_query_suburb)
    if rst_flag:
        """
        Get all house info
        Each house:
        house address, price, beds, baths, cars, land size, link
        """
        rst_bs4 = BeautifulSoup(rst_content, 'lxml')
        result_list = rst_bs4.find('table', class_="resultsList fn_tableResultsList fn_tablePostcodeList")
        result_tbody = result_list.find('tbody')
        result_tr = result_tbody.find_all('tr')
        for each_tr in result_tr:
            # print(each_house)
            try:
                result_post = each_tr.find('td', class_="first")
                result_p = result_post.find("a")
                result_post_code = result_p.text.strip()

                result_loc = each_tr.find('td', class_="second")
                result_l = result_loc.find("a")
                result_suburb = result_l.text.strip()

                full_suburb_name = result_suburb + ", " + result_post_code

                result_suburbs.append(full_suburb_name)
            except BaseException as err:
                print("BaseException:{0}-url page:{1}".format(str(err), url_query_suburbs))

    return result_suburbs


def remove_left_open_angle(string_with_angle):
    string_without_quote = string_with_angle.replace('"', "")
    return re.search('"property-features-text-container">(.*?)<', string_without_quote).group(1)


class SleeperClass:
    c_min_time_interval = 100
    c_max_time_interval = 1500
    c_min_time_step = 300

    def __init__(self):
        pass

    @classmethod
    def sleep_random(cls):
        sleep_millisecond = random.randrange(cls.c_min_time_interval, cls.c_max_time_interval, cls.c_min_time_step)
        sleep_sec = Decimal(sleep_millisecond)/1000
        print("sleep [{0}] seconds...".format(sleep_sec))
        time.sleep(sleep_sec)
'''
logging.debug('This is a debug message')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')
'''


def get_log_level(log_level):
    if log_level.lower() == "debug":
        return logging.DEBUG
    if log_level.lower() == "info":
        return logging.INFO
    if log_level.lower() == "warning":
        return logging.WARNING
    if log_level.lower() == "error":
        return logging.ERROR
    if log_level.lower() == "critical":
        return logging.CRITICAL
    return logging.INFO


# logger
class LoggerClass:
    worker_logger = None
    listener_logger = None
    cls_queue = multiprocessing.Queue(-1)

    def __init__(self):
        pass

    @classmethod
    def get_worker_logger(cls, log_queue, log_level=logging.INFO):
        if cls.worker_logger is None:
            handler_queue = logging.handlers.QueueHandler(log_queue)  # Just the one handler needed
            formatter = logging.Formatter(
                "[%(asctime)s]-[%(processName)s-%(threadName)s-(%(levelname)s)%(filename)s:%(lineno)d]:%(message)s")
            handler_queue.setFormatter(formatter)
            root = logging.getLogger()
            root.addHandler(handler_queue)
            # send all messages, for demo; no other level or filter logic applied.
            root.setLevel(log_level)
            cls.worker_logger = logging.getLogger(str(os.getpid()))

        return cls.worker_logger

    @classmethod
    def get_listener_logger(cls):
        if cls.listener_logger is None:
            # logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S')
            cls.listener_logger = logging.getLogger(__name__)
            cls.listener_logger.setLevel(logging.DEBUG)

            # file handler
            handler_file = logging.handlers.TimedRotatingFileHandler(get_log_path(), "h", 1)
            cls.listener_logger.addHandler(handler_file)

            # Console handler
            console_handler = logging.StreamHandler()
            cls.listener_logger.addHandler(console_handler)

        return cls.listener_logger

    @classmethod
    def listener_thread(cls, logger_queue):
        logger = cls.get_listener_logger()
        logger.info("listener_thread started[{}]".format(os.getpid()))
        while True:
            try:
                record = logger_queue.get()
                if record is None:  # We send this as a sentinel to tell the listener to quit.
                    break
                # logger = logging.getLogger(record.name)
                logger.info(record.message)
            except Exception:
                print('Whoops! Problem:', file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
        logger.info("listener_thread finished[{}]".format(os.getpid()))
'''
Only for main test
@classmethod
    def worker_process(cls, logger_queue, logger_configurer):
        worker_logger = logger_configurer(logger_queue)
        worker_logger.debug("Worker started[{}]".format(str(os.getpid())))
        for i in range(10):
            time.sleep(1)
            # logger = logging.getLogger(choice(LOGGERS))
            worker_logger.error("Process[{0}]-[{1}th] sec".format(str(os.getpid()), str(i)))
        worker_logger.debug("Worker finished[{}]".format(str(os.getpid())))
'''




# Main test
if __name__ == '__main__':
    main_logger = LoggerClass.get_listener_logger()
    main_logger.info("main thread started - created sub processes[{}]".format(os.getpid()))
    log_dir_path = os.path.dirname(get_log_path())
    if not os.path.exists(log_dir_path):
        os.mkdir(log_dir_path)
    queue = multiprocessing.Queue(-1)
    listener = threading.Thread(target=LoggerClass.listener_thread, args=(queue,))
    listener.start()

    workers = []
    for i in range(1):
        worker = multiprocessing.Process(target=LoggerClass.worker_process,
                                         args=(queue, LoggerClass.get_worker_logger))
        workers.append(worker)
        worker.start()
    for w in workers:
        w.join()

    queue.put_nowait(None)
    listener.join()
    main_logger.info("main thread started - stopped[{}]".format(os.getpid()))


