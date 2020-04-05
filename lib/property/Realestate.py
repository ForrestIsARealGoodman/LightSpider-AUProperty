# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#
#  Author: Forrest Xiong
#  Email:  forrestisagoodman@gmail.com

import os
import io
import sys
import json
from datetime import datetime
from bs4 import BeautifulSoup
from lib.common.Util import *
from lib.common.URLHandler import *
from lib.common.ReportHandler import *
from lib.parameter.RealestateParam import *
import time

# define particular url or class element that were defined in real estate
G_URL_SUBURBS = ('https://suggest.realestate.com.au/consumer-suggest/suggestions?'
                     'max=7&type=suburb%2Cprecinct%2Cregion%2Cstate%2Cpostcode&src=homepage&query=')
G_CLASS_PROPERTY_LIST = "residential-card__content-wrapper"
G_CLASS_PRICE = "property-price"
G_CLASS_LINK = "details-link residential-card__details-link"
G_CLASS_PROPERTY_PRIMARY = "primary-features residential-card__primary"
G_CLASS_PROPERTY_BED = "general-features__icon general-features__beds"
G_CLASS_PROPERTY_BATH = "general-features__icon general-features__baths"
G_CLASS_PROPERTY_CAR = "general-features__icon general-features__cars"
G_CLASS_PROPERTY_LAND = "property-size__icon property-size__land"


class RealEstateException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class RealEstateClass:
    """
    This class defines functions and parameters that are specific to the website real estate:
    https://www.realestate.com.au/

    Attributes:
    real_estate_param_obj: instance of RealestateParamClass
    """

    cls_class_dict = {}

    def __init__(self, base_param_obj, report_handler_obj):
        self._rp = RealEstateParamClass(base_param_obj)
        self._rh = report_handler_obj
        self._search_candidates = []
        self._logger = None

    def run_search_task(self, spider_logger):
        """
        _get_all_suburb_candidates()
        initialize_reports()
        for each candidate location in the list:
            do research task
        :return:
        """
        self._logger = spider_logger
        self._get_all_suburb_candidates()
        self._rp.generate_spider_urls(self._search_candidates)
        for candidate_location in self._search_candidates:
            self._logger.info("Starting to crawl the region[{}]".format(candidate_location))
            self._search_house_task(candidate_location)

    def _get_all_suburb_candidates(self):
        url_candidates = G_URL_SUBURBS + self._rp.get_search_location_name()
        self._logger.info("Starting to fetch candidates from [{0}]...".format(url_candidates))
        rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_candidates, G_HEADER_REAL_ESTATE)
        if not rst_flag:
            print(rst_content)
            return
        else:
            """
            Parse the json file

            """
            print(rst_content)
            json_suburb = json.loads(rst_content)
            print(type(json_suburb))
            content_embedded = json_suburb["_embedded"]
            content_suggestions = content_embedded["suggestions"]

            for each_content_info in content_suggestions:
                content_display = each_content_info["display"]
                candidate_location = content_display["text"]
                self._logger.info("checking candidate_location[{0}]".format(candidate_location))
                if self._rp.check_if_location_valid(candidate_location):
                    self._search_candidates.append(candidate_location)
                else:
                    self._logger.warning("candidate_location[{0}] is not valid".format(candidate_location))

    def _search_house_task(self, candidate_location):
        url_first_page = self._rp.get_url_candidate_location(candidate_location)
        index_page = 1
        while True:
            current_page = self._rp.generate_url_with_page_index(url_first_page, index_page)
            access_flag, house_list = self._search_page(current_page)
            if access_flag:
                if house_list is None or len(house_list) == 0:
                    break
            self._rh.insert_property_result(candidate_location, house_list)
            index_page += 1
            SleeperClass.sleep_random()

    def _search_page(self, url_page):
        self._logger.info("start to search page[{}]".format(url_page))
        search_houses = []
        # url_test = "https://www.realestate.com.au/buy/property-house-between-500000-900000-in-werribee+south,+vic+3030/list-1?source=refinement"
        rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_page, G_HEADER_REAL_ESTATE)
        retry_count_search = 0
        retry_times = 6
        while retry_count_search < retry_times:
            retry_count_search += 1
            self._logger.warning("[{0}]th retry to access[{1}]...".format(retry_count_search, url_page))
            if rst_flag:
                break
            SleeperClass.sleep_random()
            rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_page, G_HEADER_REAL_ESTATE)

        if not rst_flag:
            self._logger.error(rst_content)
        else:
            """
            Get all house info
            Each house:
            house address, price, beds, baths, cars, land size, link
            """
            rst_bs4 = BeautifulSoup(rst_content, 'lxml')
            invalid_permission_check = rst_bs4.findAll(text='403 - Permission Denied')
            if invalid_permission_check:
                return rst_flag, search_houses
            house_list = rst_bs4.find_all('div', class_="residential-card__content-wrapper", role="presentation")
            for each_house in house_list:
                # print(each_house)
                try:
                    info_house = PropertyParams()
                    house_price = each_house.find('span', class_="property-price")
                    if house_price is not None:
                        info_house.result_price = house_price.text.strip()

                    residential_details = each_house.find('a', class_="details-link residential-card__details-link")
                    info_house.result_link = G_REALESTATE_URL_DOMAIN + residential_details["href"]

                    house_address = residential_details.span
                    if house_address is not None:
                        info_house.result_address = house_address.text

                    residential_primary = each_house.find('div', class_="primary-features residential-card__primary")
                    house_beds = residential_primary.find("span", \
                                    class_="general-features__icon general-features__beds")
                    if house_beds is not None:
                        info_house.result_beds = house_beds.text.strip()

                    house_baths = residential_primary.find("span", \
                                                          class_="general-features__icon general-features__baths")
                    if house_baths is not None:
                        info_house.result_baths = house_baths.text.strip()

                    house_cars = residential_primary.find("span", \
                                                           class_="general-features__icon general-features__cars")
                    if house_cars is not None:
                        info_house.result_cars = house_cars.text.strip()

                    house_land_size = residential_primary.find("span", \
                                                          class_="property-size__icon property-size__land")
                    if house_land_size is not None:
                        info_house.result_land_size = house_land_size.text.strip()

                    search_houses.append(info_house)

                except BaseException as err:
                    self._logger.error("BaseException:{0}-url page:{1}".format(str(err), url_page))

        return rst_flag, search_houses

    def _search_rent_task(self):
        pass

    def _generate_house_url(self):
        pass

    def _generate_apartment_url(self):
        pass

    def _generate_land_url(self):
        pass

    # Get sub properties of buy property
    def _get_buy_property_price(self, bs_obj):
        pass

    def _get_buy_property_link(self, bs_obj):
        pass

    def _get_buy_property_address(self, bs_obj):
        pass

    def _get_buy_property_beds(self, bs_obj):
        pass

    def _get_buy_property_baths(self, bs_obj):
        pass

    def _get_buy_property_lands(self, bs_obj):
        pass

    # Get sub properties of rent property ...


# Main test
if __name__ == '__main__':
    url_page = "https://www.realestate.com.au/buy/property-house-between-500000-900000-in-werribee+south,+vic+3030/list-1?source=refinement"
    rp = RealEstateClass()


