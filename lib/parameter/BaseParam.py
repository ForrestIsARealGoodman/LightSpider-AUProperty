import os
import sys
from lib.common.Util import *
import uuid

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
G_MIN_PRICE = "min_price"
G_MAX_PRICE = "max_price"
G_MIN_LAND_SIZE = "min_land_size"
G_MAX_LAND_SIZE = "max_land_size"
G_PARKING = "parking"

# 1-new, 0-old
G_NEW_OLD = "new_old_flag"

# 1-including contract or offer, 0-excluding them
G_UNDER_CONTRACT_OFFER = "contract_offer_flag"

G_ANY_CONDITION = "any"


'''
Property Params
Each house:
house address, price, beds, baths, cars, land size, link
'''
G_STR_ADDRESS = "house address"
G_STR_PRICE = "price"
G_STR_BEDS = "beds"
G_STR_BATHS = "baths"
G_STR_CARS = "cars"
G_STR_SIZE = "land size"
G_STR_LINK = "link"


class PropertyParams:
    def __init__(self):
        self.result_address = ""
        self.result_price = ""
        self.result_beds = ""
        self.result_baths = ""
        self.result_cars = ""
        self.result_land_size = ""
        self.result_link = ""


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

        self.min_price = "0"
        self.min_price_config_flag = False

        self.max_price = "10000000"
        self.max_price_config_flag = False

        self.min_land_size = "0"
        self.min_land_config_flag = False

        self.max_land_size = "1000000"
        self.max_land_config_flag = False

        self.parking = "1"
        self.parking_config_flag = False

        self.new_old = "0"
        self.new_old_config_flag = False

        self.contract_offer = "0"
        self.contract_offer_config_flag = False

        self.search_sites = [""]

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
                else:
                    self.min_bed_config_flag = True

        if G_MAX_BED in dict_parameters.keys():
            self.max_bed = dict_parameters[G_MAX_BED]
            if self.max_bed != G_ANY_CONDITION:
                if self.min_bed_config_flag and int(self.max_bed) < int(self.min_bed):
                    err_msg = "Configuration error: incorrect max_bed[{}]".format(self.max_bed)
                    raise BaseParamException(err_msg)
                else:
                    self.max_bed_config_flag = True

        if G_MIN_BATH in dict_parameters.keys():
            self.min_bath = dict_parameters[G_MIN_BATH]
            if self.min_bath != G_ANY_CONDITION:
                if int(self.min_bath) < 0:
                    err_msg = "Configuration error: incorrect min bath[{}]".format(self.min_bath)
                    raise BaseParamException(err_msg)
                else:
                    self.min_bath_config_flag = True

        if G_MIN_PRICE in dict_parameters.keys():
            self.min_price = dict_parameters[G_MIN_PRICE].replace(",", "")
            if self.min_price != G_ANY_CONDITION:
                if int(self.min_price) < 0:
                    err_msg = "Configuration error: incorrect min price[{}]".format(self.min_price)
                    raise BaseParamException(err_msg)
                else:
                    self.min_price_config_flag = True

        if G_MAX_PRICE in dict_parameters.keys():
            self.max_price = dict_parameters[G_MAX_PRICE].replace(",", "")
            if self.max_price != G_ANY_CONDITION:
                if int(self.max_price) < int(self.min_price):
                    err_msg = "Configuration error: incorrect max_price[{}]".format(self.max_price)
                    raise BaseParamException(err_msg)
                else:
                    self.max_price_config_flag = True

        if G_MIN_LAND_SIZE in dict_parameters.keys():
            self.min_land_size = dict_parameters[G_MIN_LAND_SIZE]
            if self.min_land_size != G_ANY_CONDITION:
                self.min_land_config_flag = True

        if G_MAX_LAND_SIZE in dict_parameters.keys():
            self.max_land_size = dict_parameters[G_MAX_LAND_SIZE]
            if self.max_land_size != G_ANY_CONDITION:
                self.max_land_config_flag = True

        if G_PARKING in dict_parameters.keys():
            self.parking = dict_parameters[G_PARKING]
            self.parking_config_flag = True

        if G_NEW_OLD in dict_parameters.keys():
            self.new_old = dict_parameters[G_NEW_OLD]
            self.new_old_config_flag = True

        if G_UNDER_CONTRACT_OFFER in dict_parameters.keys():
            self.contract_offer = dict_parameters[G_UNDER_CONTRACT_OFFER]
            self.contract_offer_config_flag = True

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
