import os
import sys
from lib.common.Util import *
import uuid
from enum import Enum

'''
define all potential conditions to filter properties
'''
# Search Spider WebSites
G_SEARCH_SITES = "spider_sites"
# data source type
# Buy, Rent, Sold, Share, New homes, Find agents, Lifestyle, News, Commercial
G_SOURCE_TYPE = "source_type"

# type of property
# house, apartment, townhouse
G_PROPERTY_TYPE = "property_type"

# used to filter all the candidates when the "suburb_name" is given.
# New South Wales, Victoria, Queensland, Western Australia, South Australia and Tasmania
# nsw, qld, sa, tas, vic, wa
G_STATE_NAME = "state_name"

# higher priority
G_LOCATION_LIST = "location_list"
G_LOCATION_NAME = "location_name"
G_MIN_BED = "min_bed"
G_MAX_BED = "max_bed"
G_MIN_BATH = "min_bath"
G_MAX_BATH = "max_bath"
G_MIN_PRICE = "min_price"
G_MAX_PRICE = "max_price"
G_MIN_LAND_SIZE = "min_land_size"
G_MAX_LAND_SIZE = "max_land_size"
G_MIN_CAR_SPACE = "min_car_space"
G_MAX_CAR_SPACE = "max_car_space"

# school
G_SCHOOL_SCORES = "school_scores"
G_SCHOOL_TYPE = "school_type"
G_SCHOOL_SHEET = "school_report_sheet"

# Common Switches
G_CRAWLER_TARGET = "crawler_target"
G_SCHOOL_TARGET = "crawler_school_target"

# 1-new, 0-old
G_NEW_OLD = "new_old_flag"

# 1-including contract or offer, 0-excluding them
G_UNDER_CONTRACT_OFFER = "contract_offer_flag"

G_ANY_CONDITION = "any"

#school

'''
Property Params
Each house:
house address, price, beds, baths, cars, land size, link
'''
G_STR_ADDRESS = "property address"
G_STR_PRICE = "price"
G_STR_BEDS = "beds"
G_STR_BATHS = "baths"
G_STR_CARS = "cars"
G_STR_SIZE = "land size"
G_STR_LINK = "link"
G_STR_TYPE = "property Type"
G_STR_STATEMENT = "statement"
'''
School Params
Each School:
house address, price, beds, baths, cars, land size, link
'''
G_SCH_ADDRESS = "school address"
G_SCH_SCORE = "scores"
G_SCH_TYPE = "school_type"
G_SCH_ENROLL = "enrollments"
G_SCH_EDU = "better_education_link"
G_SCH_MY = "my_school_link"

# price
G_PRICE_DOLLAR = "$"

G_STRING_NULL = 'N/A'
G_ANY_TARGET = "any"
G_SCH_TARGET = "school"
G_SUB_TARGET = "suburb"
G_TARGET_LIST = [G_ANY_TARGET, G_SCH_TARGET, G_SUB_TARGET]

G_SCH_TARGET_DISTRICT = "district"
G_SCH_TARGET_TOP = "top"
G_SCH_LIST = [G_SCH_TARGET_DISTRICT, G_SCH_TARGET_TOP]


class PropertyParams:
    def __init__(self):
        self.result_address = "N/A"
        self.result_price = "N/A"
        self.result_beds = "N/A"
        self.result_baths = "N/A"
        self.result_cars = "N/A"
        self.result_land_size = "N/A"
        self.result_link = "N/A"
        self.result_type = "N/A"
        self.result_remarks = "N/A"
        self.result_statements = "N/A"


class SchoolParams:
    def __init__(self):
        """
        key - school address;
        Value = ["school address", "scores", "school type", "Enrollments", "edu link", "my school link"]
        """
        self.result_school_address = "N/A"
        self.result_scores = "N/A"
        self.result_school_type = "N/A"
        self.result_enrollments = "N/A"
        self.result_better_education_link = "N/A"
        self.result_my_school_link = "N/A"


class ReportType(Enum):
    SuburbProperty = 1
    SchoolProperty = 2
    SchoolDistrict = 3
    SchoolTop = 4
    NullInfo = 5


class ReportData:
    def __init__(self):
        self.report_type = ReportType.NullInfo
        self.report_location = ""
        self.search_location = ""
        self.search_record = ""


class BaseParamException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class BaseParamClass:

    """
        This class mainly handle the search conditions
        Not only real estate but domain, and any other property website

        Attributes:
        dict_parameters: dictionary stores all search parameters
    """
    # configured in each job
    cls_search_sites = []

    def __init__(self):
        # default value
        self.source_type = "buy"
        self.source_config_flag = False

        self.property_type = "house"
        self.property_config_flag = False

        self.state_name = "vic"
        self.state_config_flag = False

        self.location_name = ""
        self.location_config_flag = False

        self.min_bed = "1"
        self.min_bed_config_flag = False

        self.max_bed = "5"
        self.max_bed_config_flag = False

        self.min_bath = "1"
        self.min_bath_config_flag = False

        self.max_bath = "any"
        self.max_bath_config_flag = False

        self.min_price = "0"
        self.min_price_config_flag = False

        self.max_price = "10000000"
        self.max_price_config_flag = False

        self.min_land_size = "0"
        self.min_land_config_flag = False

        self.max_land_size = "1000000"
        self.max_land_config_flag = False

        self.min_car_space = "any"
        self.min_car_config_flag = False

        self.max_car_space = "any"
        self.max_car_config_flag = False

        self.new_old = "0"
        self.new_old_config_flag = False

        self.contract_offer = "0"
        self.contract_offer_config_flag = False

        # Any, Government, Non-government
        self.school_gov_flag = "Any"
        self.school_scores = "99"

        # "Multiple", "Single"
        self.school_report_sheet = "Single"
        self.search_sites = [""]

        # Common Switches
        # 'Any' - property both school district and suburb;
        # 'school', property per school district in given suburbs provided by "location_list"
        # 'suburb', property per suburb provided by "location_list"
        self.crawler_target = "any"
        # 'district' - property both school district and suburb;
        # 'top', all top schools ranked by scores (param: school_scores) in state (param: state_name)
        self.crawler_school_target = "district"

        # request job
        # in order to generate result file name
        self.request_job = uuid.uuid1()

    def initialize_parameters(self, dict_parameters):
        print("initialize parameters ...")
        if G_SEARCH_SITES in dict_parameters.keys():
            self.search_sites = dict_parameters[G_SEARCH_SITES]
            if len(self.search_sites != 0):
                debug_print(self.search_sites)

        if G_SOURCE_TYPE in dict_parameters.keys():
            self.source_type = dict_parameters[G_SOURCE_TYPE]
            self.source_config_flag = True

        if G_PROPERTY_TYPE in dict_parameters.keys():
            self.property_type = dict_parameters[G_PROPERTY_TYPE]
            self.property_config_flag = True

        if G_STATE_NAME in dict_parameters.keys():
            self.state_name = dict_parameters[G_STATE_NAME]
            self.state_config_flag = True

        if G_MIN_BED in dict_parameters.keys():
            self.min_bed = dict_parameters[G_MIN_BED]
            if self.min_bed != G_ANY_CONDITION:
                if int(self.min_bed) < 0:
                    err_msg = "Configuration error: incorrect min_bed[{}]".format(self.min_bed)
                    raise BaseParamException(err_msg)
                self.min_bed_config_flag = True

        if G_MAX_BED in dict_parameters.keys():
            self.max_bed = dict_parameters[G_MAX_BED]
            if self.max_bed != G_ANY_CONDITION:
                if self.min_bed_config_flag and int(self.max_bed) < int(self.min_bed):
                    err_msg = "Configuration error: incorrect max_bed[{}]".format(self.max_bed)
                    raise BaseParamException(err_msg)
                self.max_bed_config_flag = True

        if G_MIN_BATH in dict_parameters.keys():
            self.min_bath = dict_parameters[G_MIN_BATH]
            if self.min_bath != G_ANY_CONDITION:
                if int(self.min_bath) < 0:
                    err_msg = "Configuration error: incorrect min bath[{}]".format(self.min_bath)
                    raise BaseParamException(err_msg)
                self.min_bath_config_flag = True

        if G_MAX_BATH in dict_parameters.keys():
            self.max_bath = dict_parameters[G_MAX_BATH]
            if self.max_bath != G_ANY_CONDITION:
                if int(self.max_bath) < 0 and int(self.max_bath) < int(self.min_bath):
                    err_msg = "Configuration error: incorrect min bath[{}]".format(self.max_bath)
                    raise BaseParamException(err_msg)
                self.min_bath_config_flag = True

        if G_MIN_PRICE in dict_parameters.keys():
            self.min_price = dict_parameters[G_MIN_PRICE].replace(",", "")
            if self.min_price != G_ANY_CONDITION:
                if int(self.min_price) < 0:
                    err_msg = "Configuration error: incorrect min price[{}]".format(self.min_price)
                    raise BaseParamException(err_msg)
                self.min_price_config_flag = True
            else:
                self.min_price = "0"

        if G_MAX_PRICE in dict_parameters.keys():
            self.max_price = dict_parameters[G_MAX_PRICE].replace(",", "")
            if self.max_price != G_ANY_CONDITION:
                if int(self.max_price) < int(self.min_price):
                    err_msg = "Configuration error: incorrect max_price[{}]".format(self.max_price)
                    raise BaseParamException(err_msg)
                self.max_price_config_flag = True

        if G_MIN_LAND_SIZE in dict_parameters.keys():
            self.min_land_size = dict_parameters[G_MIN_LAND_SIZE]
            if self.min_land_size != G_ANY_CONDITION:
                self.min_land_config_flag = True

        if G_MAX_LAND_SIZE in dict_parameters.keys():
            self.max_land_size = dict_parameters[G_MAX_LAND_SIZE]
            if self.max_land_size != G_ANY_CONDITION:
                self.max_land_config_flag = True

        if G_MIN_CAR_SPACE in dict_parameters.keys():
            self.min_car_space = dict_parameters[G_MIN_CAR_SPACE]
            if self.min_car_space != G_ANY_CONDITION:
                if int(self.min_car_space) < 0:
                    err_msg = "Configuration error: incorrect min car space[{}]".format(self.min_car_space)
                    raise BaseParamException(err_msg)
                self.min_car_config_flag = True
            else:
                self.min_car_space = 0

        if G_MAX_CAR_SPACE in dict_parameters.keys():
            self.max_car_space = dict_parameters[G_MAX_CAR_SPACE].replace(",", "")
            if self.max_car_space != G_ANY_CONDITION:
                if int(self.max_car_space) < int(self.min_car_space):
                    err_msg = "Configuration error: incorrect max car space[{}]".format(self.max_car_space)
                    raise BaseParamException(err_msg)
                self.max_car_config_flag = True

        if G_NEW_OLD in dict_parameters.keys():
            self.new_old = dict_parameters[G_NEW_OLD]
            self.new_old_config_flag = True

        if G_UNDER_CONTRACT_OFFER in dict_parameters.keys():
            self.contract_offer = dict_parameters[G_UNDER_CONTRACT_OFFER]
            self.contract_offer_config_flag = True

        if G_SCHOOL_SCORES in dict_parameters.keys():
            self.school_scores = dict_parameters[G_SCHOOL_SCORES]

        if G_SCHOOL_TYPE in dict_parameters.keys():
            self.school_gov_flag = dict_parameters[G_SCHOOL_TYPE]

        if G_SCHOOL_SHEET in dict_parameters.keys():
            self.school_report_sheet = dict_parameters[G_SCHOOL_SHEET]

        if G_CRAWLER_TARGET in dict_parameters.keys():
            self.crawler_target = dict_parameters[G_CRAWLER_TARGET]

        if G_SCHOOL_TARGET in dict_parameters.keys():
            self.crawler_school_target = dict_parameters[G_SCHOOL_TARGET]

    def set_location_name(self, value):
        self.location_name = value
        self.location_config_flag = True

'''
    @property
    def state_name(self):
        return self.state_name

    @state_name.setter
    def state_name(self, value):
        self.state_name = value
        
                if G_SUBURB_NAME in dict_parameters.keys():
            self.suburb_name = dict_parameters[G_SUBURB_NAME]
            self.suburb_config_flag = True
'''

# Main test
if __name__ == '__main__':
    pass
