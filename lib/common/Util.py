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
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def get_parser():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-l", "--log",
                        help="debug, info, warning, error, critical",
                        metavar="<log level>",
                        required=False)
    parser.add_argument("-i", "--increment",
                        help="only dump the newly updated data to excel",
                        action='store_true',
                        required=False)
    parser.set_defaults(help=False)
    return parser


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


def get_db_path():
    db_path = os.path.join(get_project_dir(), "db\\")
    return db_path


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


# Main test
if __name__ == '__main__':
    pass

