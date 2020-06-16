import os
import sys
import yaml

from lib.common.Util import *
from lib.common.URLHandler import *

from lib.core.Controller import *
from lib.parameter.BaseParam import *



class ConfigParserException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


def __init__(self, project_config_file, search_config_file):
    print("----------------Begin to Parse all config file----------------")
    # self.parse_project_config_file(project_config_file)
    debug_print(sys.path)
    debug_print(get_project_dir())
    self.parse_project_search_file(search_config_file)
    print("----------------Parse End----------------")


def parse_project_search_file(search_config_file, dict_search, crawler_sites):
    # parse all param list based on BaseParamClass
    try:
        debug_print(search_config_file)
        yaml_object = get_config_yaml(search_config_file)
        debug_print(yaml_object)
        for key, value in yaml_object.items():
            debug_print(key)
            debug_print(value)
            # Check search job
            if key == "SearchJob":
                location_list = value[G_LOCATION_LIST]
                if location_list:
                    for each_location in location_list:
                        inst_bp = BaseParamClass()
                        inst_bp.set_location_name(each_location)
                        dict_search[each_location] = inst_bp
                        inst_bp.initialize_parameters(value)
                else:
                    inst_bp = BaseParamClass()
                    location_name = value[G_STATE_NAME]
                    if location_name:
                        inst_bp.set_location_name(location_name)
                        dict_search[location_name] = inst_bp
                        inst_bp.initialize_parameters(value)
                    else:
                        raise BaseException("Config - Location_list and State name are both empty!!!")
            if key == "RequestHeaders":
                if G_HEADER_REAL_ESTATE in value.keys():
                    dict_header = {}
                    for head_key, head_value in value[G_HEADER_REAL_ESTATE].items():
                        dict_header[head_key] = head_value
                    URLHandlerClass.request_header_dict[G_HEADER_REAL_ESTATE] = dict_header
                    debug_print(URLHandlerClass.request_header_dict[G_HEADER_REAL_ESTATE])
                if G_HEADER_DOMAIN in value.keys():
                    dict_header = {}
                    for head_key, head_value in value[G_HEADER_DOMAIN].items():
                        dict_header[head_key] = head_value
                    URLHandlerClass.request_header_dict[G_HEADER_DOMAIN] = dict_header
                    debug_print(URLHandlerClass.request_header_dict[G_HEADER_DOMAIN])
            if key == "RequestTimeInterval":
                SleeperClass.c_min_time_interval = value["min_time_interval"]
                SleeperClass.c_max_time_interval = value["max_time_interval"]
                SleeperClass.c_min_time_step = value["min_time_step"]
                debug_print(SleeperClass.c_min_time_interval)
                debug_print(SleeperClass.c_max_time_interval)
                debug_print(SleeperClass.c_min_time_step)
            if key == "CrawlerSites":
                for each_site in value:
                    crawler_sites.append(each_site)

    except BaseException as err:
        err_msg = "BaseException:{0}".format(str(err))
        raise ConfigParserException(err_msg)


def get_config_yaml(yaml_file):
    config_content = read_data_from_file(yaml_file)
    if config_content is not None:
        try:
            yaml_object = yaml.safe_load(config_content)
            return yaml_object
        except BaseException as err:
            err_msg = "BaseException:{0}-config_file:{1}".format(str(err), yaml_file)
            debug_print(err_msg)
            raise ConfigParserException(err_msg)
    else:
        err_msg = "config_file:{}".format(yaml_file)
        debug_print(err_msg)
        raise ConfigParserException(err_msg)


def read_data_from_file(data_config_file):
    try:
        with open(data_config_file, 'r') as file_stream:
            content_data = file_stream.read()
            return content_data
    except OSError as err:
        raise ConfigParserException("OSError:{0}-config_file:{1}".format(str(err), data_config_file))
    except BaseException as err:
        raise ConfigParserException("BaseException:{0}-config_file:{1}".format(str(err), data_config_file))


# Main test
if __name__ == '__main__':
    config_file = r"D:\DevSpace\02-PyProject\01-WebSpider\01-AUProperty\LightSpider-AUProperty\config\config.yaml"
    search_config = r"D:\DevSpace\02-PyProject\01-WebSpider\01-AUProperty\LightSpider-AUProperty\AUPropertySpider.yaml"
    cls_dict_search = {}
    parse_project_search_file(search_config, cls_dict_search)
