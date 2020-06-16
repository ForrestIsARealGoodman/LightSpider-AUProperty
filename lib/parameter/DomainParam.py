from lib.parameter.BaseParam import *
from datetime import datetime
import re
from lib.common.URLHandler import *

#https://www.domain.com.au/sale/burwood-east-vic-3151/house/?bedrooms=2-4&bathrooms=1-4&price=50000-1100000&carspaces=1-4&landsize=300-1100

# global variable
G_DOMAIN_URL_DOMAIN = "https://www.domain.com.au"
G_DOMAIN_URL_BASE = "https://www.domain.com.au/{0}/{1}/{2}/?{3}"
G_DOMAIN_URL_SCHOOL_CATCHMENT = "https://www.domain.com.au/school-catchment/{0}"
G_DOMAIN_URL_SCHOOL_S = "https://www.domain.com.au/schools/{0}"
G_DOMAIN_URL_SCHOOL_PAGE = "?listingtype=forSale&pageno={0}&ssubs=0"

G_PARAM_BED = "&bedrooms={0}-{1}"
G_PARAM_BATH = "&bathrooms={0}-{1}"
G_PARAM_PRICE = "&price={0}-{1}"
G_PARAM_LAND_SIZE = "&landsize={0}-{1}"
G_PARAM_CAR_SPACE = "&carspaces={0}-{1}"
G_PARAM_PAGE_INDEX = "&page={0}"


class DomainParamException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class DomainParamClass:

    """
        This class implements some specific parameters that only belong to DOMAIN site
        defined functions and parameters that are specific to the website real estate:
        https://www.domain.com.au/

        Attributes:
        dict_parameters: dictionary stores all search parameters
    """

    cls_estate_dict = {}
    cls_config_key = "domain"

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
        # 'https://suggest.DOMAIN.com.au/consumer-suggest/suggestions?'
        # 'max=7&type=suburb%2Cprecinct%2Cregion%2Cstate%2Cpostcode&src=homepage&query='
        # Query priority: suburb > region > state name.
        # Only one value needed to be queried,
        # for example, if suburb, region, state are all set in configuration, only suburb is needed.

        _candidate_location_query_url

        """
        self._bp = instance_base_param
        self._dict_property_candidate_suburb_location = {}
        self._dict_property_candidate_school_location = {}
        self._crawler_target = G_ANY_TARGET
        if self._bp.crawler_target in G_TARGET_LIST:
            self._crawler_target = self._bp.crawler_target
        self._crawler_school_target = G_SCH_TARGET_DISTRICT
        if self._bp.crawler_school_target in G_SCH_LIST:
            self._crawler_school_target = self._bp.crawler_school_target

    def get_crawler_target_name(self):
        return self._crawler_target

    def get_crawler_school_target_name(self):
        return self._crawler_school_target

    def get_search_location_name(self):
        return self._bp.location_name

    def get_search_state_name(self):
        return self._bp.state_name

    # called by domain process class
    def get_url_candidate_suburb_location(self, candidate_location):
        return self._dict_property_candidate_suburb_location[candidate_location]

    # called by domain process class
    def get_dict_suburb_locations(self):
        return self._dict_property_candidate_suburb_location

    # called by domain process class
    def get_url_candidate_school_location(self, candidate_location):
        return self._dict_property_candidate_school_location[candidate_location]

    # called by domain process class
    def get_dict_school_locations(self):
        return self._dict_property_candidate_school_location

    # check if this location fit the configurations of state name
    def check_if_location_valid(self, candidate_location):
        state_lower = self._bp.state_name.lower()
        state_upper = self._bp.state_name.upper()
        if self._bp.state_config_flag is True:
            return state_lower in candidate_location or state_upper in candidate_location
        return True

    def generate_spider_urls_suburb(self, search_suburb_location):
        """ function summary

        # "https://www.domain.com.au/{0}/{1}/{2}/?{3}"
        # {0} - source type : sale(buy), rent, ...
        # {1} - suburb location
        # ex: burwood-east-vic-3151
        # {2} - property type : house, apartment, town house
        # {3} - filter parameters : bedroom, bathroom, land size, price, car spaces
        $ ex: bedrooms=2-4&bathrooms=1-4&price=50000-1100000&carspaces=1-4&landsize=300-1100

        _base_url = "https://www.domain.com.au/{0}/{1}/{2}/?{3}"

        """
        print("begin to generate url for [{0}]".format(search_suburb_location))
        # source type
        param0_property_source_type = self._bp.source_type

        # property location
        param1_property_location = search_suburb_location

        # property type
        param2_property_type = self._bp.property_type

        # filter parameters
        param3_dynamic = ""

        # bedrooms
        if self._bp.min_bed_config_flag or self._bp.max_bed_config_flag:
            url_param_bed = G_PARAM_BED.format(self._bp.min_bed, self._bp.max_bed)
            param3_dynamic += url_param_bed

        # bathrooms
        if self._bp.min_bath_config_flag or self._bp.max_bath_config_flag:
            url_param_bath = G_PARAM_BATH.format(self._bp.min_bath, self._bp.max_bath)
            param3_dynamic += url_param_bath

        # price
        if self._bp.min_price_config_flag or self._bp.max_price_config_flag:
            url_param_price = G_PARAM_PRICE.format(self._bp.min_price, self._bp.max_price)
            param3_dynamic += url_param_price

        # land size
        if self._bp.min_land_config_flag or self._bp.max_land_config_flag:
            url_param_land = G_PARAM_LAND_SIZE.format(self._bp.min_land_size, self._bp.max_land_size)
            param3_dynamic += url_param_land

        # car space
        if self._bp.min_car_config_flag or self._bp.max_car_config_flag:
            url_param_car = G_PARAM_CAR_SPACE.format(self._bp.min_car_space, self._bp.max_car_space)
            param3_dynamic += url_param_car

        url_value = G_DOMAIN_URL_BASE.format(param0_property_source_type,
                                             param1_property_location,
                                             param2_property_type,
                                             param3_dynamic)

        self._dict_property_candidate_suburb_location[search_suburb_location] = url_value

    def generate_spider_urls_school(self, real_school_name, search_school_name):
        if real_school_name in self._dict_property_candidate_school_location:
            return
        # Two kind of urls
        # figure out which one is correct
        url_search_school_s = G_DOMAIN_URL_SCHOOL_S.format(search_school_name)
        url_search_school_c = G_DOMAIN_URL_SCHOOL_CATCHMENT.format(search_school_name)

        response_redirect, rst_flag = URLHandlerClass.get_response_from_html(url_search_school_c)
        if response_redirect.url == url_search_school_c:
            self._dict_property_candidate_school_location[real_school_name] = url_search_school_c
        else:
            self._dict_property_candidate_school_location[real_school_name] = url_search_school_s

    @classmethod
    def generate_url_suburb_with_page_index(cls, search_url, index_page):
        new_index_page = G_PARAM_PAGE_INDEX.format(index_page)
        new_search_url = str(search_url) + str(new_index_page)
        return new_search_url

    @classmethod
    def generate_url_school_with_page_index(cls, search_url, index_page):
        new_index_page = G_DOMAIN_URL_SCHOOL_PAGE.format(index_page)
        new_search_url = str(search_url) + str(new_index_page)
        return new_search_url


# Main test
if __name__ == '__main__':
    pass
