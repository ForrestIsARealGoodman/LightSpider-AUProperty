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
from lib.parameter.DomainParam import *
from lib.property.BetterEducation import *
import unidecode
import time

# define particular url or class element that were defined in real estate
G_URL_CANDIDATE = "https://www.domain.com.au/phoenix/api/locations/autocomplete/v2?prefixText="


class DomainException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class DomainClass:
    """
    This class defines functions and parameters that are specific to the website real estate:
    https://www.domain.com.au/

    Attributes:
    real_estate_param_obj: instance of RealestateParamClass
    """

    cls_class_dict = {}

    def __init__(self, base_param_obj):
        self._dp = DomainParamClass(base_param_obj)
        self._be = BetterEducationClass(base_param_obj)
        self._search_candidates = []
        self._logger = None
        self._data_queue = None
        self._crawler_site = "domain"

    def get_crawler_site(self):
        return self._crawler_site

    def run_search_task(self, spider_logger, data_queue):
        """
        _get_all_suburb_candidates()
        initialize_reports()
        for each candidate location in the list:
            do research task
        :return:
        """
        self._logger = spider_logger
        self._data_queue = data_queue
        self._get_all_candidates()
        self._search_property_task()

    def _get_all_suburb_candidates(self):
        url_candidates = G_URL_CANDIDATE + self._dp.get_search_location_name()
        self._logger.info("Starting to fetch candidates from [{0}]...".format(url_candidates))
        rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_candidates)
        if not rst_flag:
            print(rst_content)
            return
        else:
            """
            Parse the json file

            """
            print(rst_content)
            json_auto_completed_loc = json.loads(rst_content)

            for each_loc_info in json_auto_completed_loc:
                location_value = each_loc_info["value"]
                location_type = each_loc_info["category"]
                if location_type == "Suburb":
                    if self._dp.check_if_location_valid(location_value):
                        self._dp.generate_spider_urls_suburb(location_value)
                        self._logger.info("Candidate_location[{0}]".format(location_value))
                else:
                    self._logger.warning("candidate_location[{0}] is not valid".format(location_value))

    def _get_all_school_candidates(self):
        crawler_school_target_param = self._dp.get_crawler_school_target_name()
        if crawler_school_target_param == G_SCH_TARGET_TOP:
            school_report_type = ReportType.SchoolTop
            school_search_region = self._dp.get_search_state_name()
            self._logger.info("Starting to get schools from state [{0}]...".format(school_search_region))
            school_dict = self._be.get_schools_from_top()
        else:
            school_report_type = ReportType.SchoolDistrict
            school_search_region = self._dp.get_search_location_name()
            self._logger.info("Starting to get schools from location [{0}]...".format(school_search_region))
            school_dict = self._be.get_schools_from_suburb(school_search_region)
        # self._rh.insert_school_list_result(school_dict)
        report_result = ReportData()
        report_result.report_type = school_report_type
        report_result.report_location = school_search_region
        report_result.search_location = school_search_region
        report_result.search_record = dict()
        report_result.search_record = {k: v for k, v in school_dict.items()}
        self._data_queue.put(report_result)

        for each_school in school_dict:
            each_school_name = each_school.split(",")[0]
            url_school_candidates = G_URL_CANDIDATE + each_school_name
            rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_school_candidates)
            if not rst_flag:
                print(rst_content)
                return
            else:
                """
                Parse the json file

                """
                print(rst_content)
                json_auto_completed_loc = json.loads(rst_content)
                for each_sch_info in json_auto_completed_loc:
                    school_value = each_sch_info["value"]
                    school_label = each_sch_info["label"]
                    candidate_type = each_sch_info["category"]
                    if candidate_type == "School" and each_school_name in school_label:
                        self._dp.generate_spider_urls_school(each_school, school_value)
                        self._logger.info("Candidate School[{0}]".format(each_school))

    def _get_all_candidates(self):
        crawler_target_param = self._dp.get_crawler_target_name()
        if crawler_target_param == G_SUB_TARGET:
            self._get_all_suburb_candidates()
        elif crawler_target_param == G_SCH_TARGET:
            self._get_all_school_candidates()
        else:
            self._get_all_suburb_candidates()
            self._get_all_school_candidates()

    def _search_property_task(self):
        for suburb_location in self._dp.get_dict_suburb_locations():
            self._logger.info("Starting to crawl the suburb location[{}]".format(suburb_location))
            self._search_property_suburb_task(suburb_location)

        for school_location in self._dp.get_dict_school_locations():
            self._logger.info("Starting to crawl the school location[{}]".format(school_location))
            self._search_property_school_task(school_location)

    def _search_property_suburb_task(self, candidate_location):
        url_first_page = self._dp.get_url_candidate_suburb_location(candidate_location)
        debug_print(url_first_page)
        index_page = 1
        while True:
            current_page = self._dp.generate_url_suburb_with_page_index(url_first_page, index_page)
            access_flag, property_list = self._search_page_suburb(current_page, candidate_location)
            if access_flag:
                if property_list is None or len(property_list) == 0:
                    break
            # self._rh.insert_suburb_property_result(candidate_location, property_list)
            index_page += 1
            SleeperClass.sleep_random()

    def _search_property_school_task(self, school_location):
        url_first_page = self._dp.get_url_candidate_school_location(school_location)
        debug_print(url_first_page)
        index_page = 1
        while True:
            current_page = self._dp.generate_url_school_with_page_index(url_first_page, index_page)
            access_flag, property_list = self._search_page_school(current_page, school_location)
            if access_flag:
                if property_list is None or len(property_list) == 0:
                    break
            # self._rh.insert_school_property_result(school_location, property_list)
            index_page += 1
            SleeperClass.sleep_random()

    def _search_page_suburb(self, url_suburb_page, candidate_location):
        self._logger.info("start to search page[{}]".format(url_suburb_page))
        result_properties = []
        rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_suburb_page)
        retry_count_search = 0
        retry_times = 3
        while retry_count_search < retry_times:
            retry_count_search += 1
            self._logger.warning("[{0}]th retry to access[{1}]...".format(retry_count_search, url_suburb_page))
            if rst_flag:
                break
            SleeperClass.sleep_random()
            rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_suburb_page)

        if not rst_flag:
            self._logger.error(rst_content)
        else:
            """
            Get all property info
            Each property:
            property address, price, beds, baths, cars, land size, links, type, remarks
            """
            rst_bs4 = BeautifulSoup(rst_content, 'lxml')
            invalid_page_check = rst_bs4.findAll(text='No exact matches')
            oops_page_check = rst_bs4.findAll(text='Oops...')
            if invalid_page_check or oops_page_check:
                return rst_flag, result_properties
            property_list = rst_bs4.find_all('div', class_="css-qrqvvg")
            for each_property in property_list:
                try:
                    report_result = ReportData()
                    info_property = PropertyParams()
                    # check postal code
                    postal_code_tag = each_property.find('span', itemprop="postalCode")
                    postal_code = postal_code_tag.text.strip()
                    if postal_code not in candidate_location:
                        continue

                    # url link
                    residential_details = each_property.find('a', class_="address is-two-lines css-1y2bib4")
                    if residential_details is not None:
                        info_property.result_link = residential_details["href"]
                        # property address
                        property_address = residential_details.find('meta', itemprop="name")
                        if property_address is not None:
                            info_property.result_address = property_address["content"]

                    # property price
                    property_price = each_property.find('p', class_="css-mgq8yx")
                    if property_price is not None:
                        info_property.result_price = property_price.text.strip()
                        if G_PRICE_DOLLAR not in info_property.result_price:
                            SleeperClass.sleep_random()
                            self._get_statement(info_property.result_link, info_property)

                    # property type
                    info_property.result_type = self._dp.get_search_property_type()

                    # beds, baths, car spaces, land size
                    residential_primary = each_property.find_all('span', class_="css-1rzse3v")
                    index_figure = len(residential_primary)

                    # beds
                    if index_figure > 0 and residential_primary[0] is not None:
                        bed_figure = residential_primary[0].contents[0]
                        info_property.result_beds = unidecode.unidecode(bed_figure.string)

                    # baths
                    if index_figure > 1 and residential_primary[1] is not None:
                        bath_figure = residential_primary[1].contents[0]
                        info_property.result_baths = unidecode.unidecode(bath_figure.string)

                    # car spaces
                    if index_figure > 2 and residential_primary[2] is not None:
                        car_figure = residential_primary[2].contents[0]
                        info_property.result_cars = unidecode.unidecode(car_figure.string)

                    # land size
                    if index_figure > 3 and residential_primary[3] is not None:
                        land_figure = residential_primary[3].contents[0]
                        info_property.result_land_size = unidecode.unidecode(land_figure.string)

                    report_result.report_location = self._dp.get_search_location_name()
                    report_result.report_type = ReportType.SuburbProperty
                    report_result.search_location = candidate_location
                    report_result.search_record = info_property
                    self._data_queue.put(report_result)

                except BaseException as err:
                    self._logger.error("BaseException:{0}-url page:{1}".format(str(err), url_suburb_page))

        return rst_flag, result_properties

    def _search_page_school(self, url_school_page, school_location):
        self._logger.info("start to search page[{}]".format(url_school_page))
        result_properties = []
        rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_school_page)
        retry_count_search = 0
        retry_times = 3
        while retry_count_search < retry_times:
            retry_count_search += 1
            self._logger.warning("[{0}]th retry to access[{1}]...".format(retry_count_search, url_school_page))
            if rst_flag:
                break
            SleeperClass.sleep_random()
            rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_school_page)

        if not rst_flag:
            self._logger.error(rst_content)
        else:
            """
            Get all property info
            Each property:
            property address, price, beds, baths, cars, land size, links, type, remarks
            """
            rst_bs4 = BeautifulSoup(rst_content, 'lxml')
            list_properties = rst_bs4.find_all('div',
                                               class_="nearby-properties__property nearby-properties__on-market-property")
            for each_property in list_properties:
                try:
                    report_result = ReportData()
                    info_property = PropertyParams()
                    property_price_info = each_property.find('div',
                                                             class_="nearby-properties__info-block nearby-properties__display-price")

                    property_address_link = property_price_info.find('a', class_="nearby-properties__address-link")
                    property_link = property_address_link["href"]
                    debug_print(property_link)
                    info_property.result_link = property_link

                    property_price = property_price_info.find('div',
                                                              class_="nearby-properties__info-block-title").text.strip()
                    info_property.result_price = property_price
                    debug_print(property_price)
                    if G_PRICE_DOLLAR not in property_price:
                        SleeperClass.sleep_random()
                        self._get_statement(property_link, info_property)

                    property_address_info = property_address_link.find('meta', itemprop="name")
                    property_address = property_address_info["content"]
                    debug_print(property_address)
                    info_property.result_address = property_address

                    property_type_info = each_property.find('div',
                                                            class_="nearby-properties__info-block nearby-properties__property-type")
                    property_type_div = property_type_info.find('div', class_="nearby-properties__info-block-body")
                    property_type = property_type_div.text.strip()
                    debug_print(property_type)
                    info_property.result_type = property_type

                    # beds, baths, car spaces
                    property_feature_info = each_property.find('div', class_="nearby-properties__property-features-wrapper")
                    list_features = property_feature_info.find_all("span",
                                                                   class_="property-feature__feature-text-container")
                    index_figure = len(list_features)

                    # beds
                    if index_figure > 0 and list_features[0] is not None:
                        property_bed = list_features[0].text.strip()
                        debug_print(property_bed)
                        info_property.result_beds = property_bed

                    # baths
                    if index_figure > 1 and list_features[1] is not None:
                        property_baths = list_features[1].text.strip()
                        debug_print(property_baths)
                        info_property.result_baths = property_baths

                    # car spaces
                    if index_figure > 2 and list_features[2] is not None:
                        property_car = list_features[2].text.strip()
                        debug_print(property_car)
                        info_property.result_cars = property_car

                    report_result.report_location = self._dp.get_search_location_name()
                    report_result.report_type = ReportType.SchoolProperty
                    report_result.search_location = school_location
                    report_result.search_record = info_property
                    self._data_queue.put(report_result)
                except BaseException as err:
                    self._logger.error("BaseException:{0}-url page:{1}".format(str(err), url_school_page))

        return rst_flag, result_properties

    def _get_statement(self, url_property_page, info_property):
        self._logger.info("start to search page[{}]".format(url_property_page))
        rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_property_page)
        retry_count_search = 0
        retry_times = 3
        while retry_count_search < retry_times:
            retry_count_search += 1
            self._logger.warning("[{0}]th retry to access[{1}]...".format(retry_count_search, url_property_page))
            if rst_flag:
                break
            SleeperClass.sleep_random()
            rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_property_page)

        if not rst_flag:
            self._logger.error(rst_content)
        else:
            """
            Get all property info
            Each property:
            property address, price, beds, baths, cars, land size, links, type, remarks
            """
            rst_bs4 = BeautifulSoup(rst_content, 'lxml')
            property_details = rst_bs4.find('div', class_="listing-details__root")

            # get land size
            property_info = property_details.find('div', class_="listing-details__listing-summary-features css-er59q5")
            property_features = property_info.find_all('span', attrs={'data-testid': 'property-features-feature'})
            index_figure = len(property_features)
            if index_figure > 3 and property_features[3] is not None:
                land_size_feature = property_features[3]
                property_land_size_info = land_size_feature.find('span',
                                                                 attrs={'data-testid': 'property-features-text-container'})
                property_land_size = property_land_size_info.text.strip()
                info_property.result_land_size = property_land_size

            # get statement pdf link
            property_statement = property_details.find('section', class_="statement-of-information")
            if property_statement is not None:
                property_statement_pdf_info = property_statement.find('a')
                property_statement_pdf_link = property_statement_pdf_info["href"]
                info_property.result_statements = property_statement_pdf_link


# Main test
if __name__ == '__main__':
    pass

