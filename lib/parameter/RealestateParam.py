from lib.parameter.BaseParam import *
from datetime import datetime
import re

# global variable
G_REALESTATE_URL_DOMAIN = "https://www.realestate.com.au"
G_REALESTATE_URL_BASE = "https://www.realestate.com.au/{0}/{1}?source=refinement&{2}"
G_LOCATION_QUERY_URL = "https://suggest.realestate.com.au/consumer-suggest/suggestions?max=7&"\
                        "type=suburb%2Cprecinct%2Cregion%2Cstate%2Cpostcode&src=homepage&query={}"

G_URL_PROPERTY = "property-{}-"
G_URL_MIN_BED = "with-{}-bedroom-"
G_URL_MAX_BED = "maxBeds={}&"
G_URL_MIN_BATH = "numBaths={}&"
G_URL_PRICE = "between-{0}-{1}-"
G_URL_LAND_SIZE = "size-{}-"
G_URL_LOCATION = "in-{}"
G_URL_PAGE_LIST = "/list-{:d}"
G_URL_PAGE_REGEX = "/list-\d+"


"""Real Estate url
Query: croydon, house
Ex:
https://www.realestate.com.au/buy/property-house-size-300-between-50000-any-in-croydon,+vic+3136/list-1?
numParkingSpaces=2&numBaths=2&maxBeds=3&newOrEstablished=established&
keywords=swimming%20pool%2Cgarage%2Cbalcony%2Coutdoor%20area%2Cundercover%20parking%2Cshed%2Cfully
%20fenced%2Coutdoor%20spa%2Ctennis%20court%2Censuite%2Cdishwasher%2Cstudy%2Cbuilt%20in%20robes%2Calarm
%20system%2Cbroadband%2Cfloorboards%2Cgym%2Crumpus%20room%2Cworkshop%2Cair%20conditioning%2Csolar
%20panels%2Cheating%2Chigh%20energy%20efficiency&checkedFeatures=swimming%20pool%2Cgarage%2Cbalcony%2Coutdoor
%20area%2Cundercover%20parking%2Cshed%2Cfully%20fenced%2Coutdoor%20spa%2Ctennis%20court%2Censuite%2Cdishwasher
%2Cstudy%2Cbuilt%20in%20robes%2Calarm%20system%2Cbroadband%2Cfloorboards%2Cgym%2Crumpus%20room%2Cworkshop%2Cair
%20conditioning%2Csolar%20panels%2Cheating%2Chigh%20energy%20efficiency&source=refinement
https://www.realestate.com.au/{0}/{1}?source=refinement&{2}
"""


class RealEstateParamException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class RealEstateParamClass:

    """
        This class implements some specific parameters that only belong to realestate site
        defined functions and parameters that are specific to the website real estate:
        https://www.realestate.com.au/

        Attributes:
        dict_parameters: dictionary stores all search parameters
    """

    cls_estate_dict = {}
    cls_config_key = "realestate"
    """
                debug_print(G_URL_PROPERTY])
                debug_print(G_URL_MIN_BED])
                debug_print(G_URL_MAX_BED])
                debug_print(G_URL_MIN_BATH])
                debug_print(G_URL_PRICE])
                debug_print(G_URL_LAND_SIZE])
                debug_print(G_URL_LOCATION])
                debug_print(G_URL_PAGE_LIST])
     """

    def __init__(self, instance_base_param):
        """ function summary

        # Given search location parameters like :state_name, region_name, suburb_name,
        # there might have several candidates.
        # For example, suburb location: "Croydon", it would have following candidates
        # "Croydon, VIC 3236", "Croydon South, Wi 3126", "Croydon Hils, VIC 3136",
        # "Croydon North, Vic 2136", "Croydon Park, NSW 2233", "Croydon, NSW 2132",
        # "Concon, QLD 4615"
        # then, according to the state or region name (if provided), select the right candidates.

        _dict_property_candidate_location - key: location; value: url
        ex:
        {"Croydon, VIC 3236" : "url_1" ; "Croydon Park, NSW 2233" : "url_2" ; ...}

        # Query url used to retrieve all the candidate locations , specific to the real estate website.
        # 'https://suggest.realestate.com.au/consumer-suggest/suggestions?'
        # 'max=7&type=suburb%2Cprecinct%2Cregion%2Cstate%2Cpostcode&src=homepage&query='
        # Query priority: suburb > region > state name.
        # Only one value needed to be queried,
        # for example, if suburb, region, state are all set in configuration, only suburb is needed.

        _candidate_location_query_url

        """
        self._bp = instance_base_param
        self._dict_property_candidate_location = {}

    def get_search_location_name(self):
        return self._bp.location_name

    # called by real estate class
    def get_url_candidate_location(self, candidate_location):
        return self._dict_property_candidate_location[candidate_location]

    # check if this location fit the configurations of state name
    def check_if_location_valid(self, candidate_location):
        state_lower = self._bp.state_name.lower()
        state_upper = self._bp.state_name.upper()
        if self._bp.state_config_flag is True:
            return state_lower in candidate_location or state_upper in candidate_location
        return True

    def generate_spider_urls(self, search_location_list):
        """ function summary

        # "https://www.realestate.com.au/{0}/{1}?source=refinement&{2}"
        # {0} - source type : buy, rent, ...
        # {1} - parameters_host : fixed parameters in the host url portion,
        # ex: property-house-with-1-bedroom-size-300-between-75000-100000
        # {2} - parameters_dynamic : filtered parameters after host url portion,
        # ex: ?numParkingSpaces=3&numBaths=1&maxBeds=4&source=refinement

        _base_url = "https://www.realestate.com.au/{0}/{1}?source=refinement&{2}"

        """
        page_index = 1
        debug_print(search_location_list)
        for url_location in search_location_list:
            # handle host parameters in the url
            # property type
            parameters_host = ""
            parameters_dynamic = ""
            if self._bp.property_config_flag is True:
                url_property_type = G_URL_PROPERTY.format(self._bp.property_type)
                parameters_host += url_property_type

            # min beds
            if self._bp.min_bed_config_flag is True:
                url_min_bed = G_URL_MIN_BED.format(self._bp.min_bed)
                parameters_host += url_min_bed

            # land size
            if self._bp.min_land_config_flag is True:
                url_min_land = G_URL_LAND_SIZE.format(self._bp.min_land_size)
                parameters_host += url_min_land

            # min and max price
            if self._bp.min_price_config_flag is True:
                if self._bp.max_price_config_flag is True:
                    url_price = G_URL_PRICE.format(self._bp.min_price, self._bp.max_price)
                    parameters_host += url_price
                else:
                    url_price = G_URL_PRICE.format(self._bp.min_price, G_ANY_CONDITION)
                    parameters_host += url_price
            else:
                if self._bp.max_price_config_flag is True:
                    url_price = G_URL_PRICE.format(1, self._bp.max_price)
                    parameters_host += url_price

            url_search_location = G_URL_LOCATION.format(url_location)
            parameters_host += url_search_location

            url_page_index = G_URL_PAGE_LIST.format(page_index)
            parameters_host += url_page_index

            # handle dynamic parameters in the url
            # max beds
            if self._bp.max_bed_config_flag is True:
                url_max_bed = G_URL_MAX_BED.format(self._bp.max_bed)
                parameters_dynamic += url_max_bed

            # min bath
            if self._bp.min_bath_config_flag is True:
                url_min_bath = G_URL_MIN_BATH.format(self._bp.min_bath)
                parameters_dynamic += url_min_bath

            url_value = G_REALESTATE_URL_BASE.format(self._bp.source_type, parameters_host, parameters_dynamic)
            self._dict_property_candidate_location[url_location] = url_value

    @classmethod
    def generate_url_with_page_index(cls, search_url, index_page):
        str_new_index_page = G_URL_PAGE_LIST.format(index_page)
        pattern_page = re.compile(G_URL_PAGE_REGEX)
        str_old_index_page = (pattern_page.findall(search_url))[0]
        new_search_url = search_url.replace(str_old_index_page, str_new_index_page, 1)
        return new_search_url


# Main test
if __name__ == '__main__':
    dict_test = {}
    dict_test["a1"] = "a1"
    dict_test["a2"] = "a2"
    dict_test["a3"] = "a3"
    debug_print(dict_test)

