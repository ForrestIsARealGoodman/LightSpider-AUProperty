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
from lib.parameter.BaseParam import *
import urllib.parse
import time

# define particular url or class element that were defined in real estate
G_EDU_COMPLETION = "https://bettereducation.com.au/school/Primary/vic/vic_primary_school_rating.aspx/GetCompletionListLocality"
G_EDU_SCHOOL = "https://bettereducation.com.au/school/Primary/vic/vic_primary_school_rating.aspx"
G_RAW_DATA_SCHOOL = 'ctl00%24ContentPlaceHolder1%24ToolkitScriptManager2=ctl00%24ContentPlaceHolder1%24UpdatePanel3%7Cctl00%24ContentPlaceHolder1%24TextBoxLocality&__PREVIOUSPAGE=BPuP9uKzo4XlP9V40uRnjPu4wNB5CHd9aCJA8XsDEzDH_6LhAnEqwwv_t2Ia5vymxAenV_uGPGtj8A0duXdrdoHexzelJN3mK1eYlKC6fSNGUtatOq26oYEY_1fWIs9fJRLvmaJsHbKgKe0GjElYRxWmCKM1&ctl00%24ContentPlaceHolder1%24TextBoxSchool=&ctl00%24ContentPlaceHolder1%24TextBoxLocality={0}&ctl00%24ContentPlaceHolder1%24TextBoxRadius=&hiddenInputToUpdateATBuffer_CommonToolkitScripts=1&__EVENTTARGET=ctl00%24ContentPlaceHolder1%24TextBoxLocality&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%2FwEPDwUKMTIwMjU3ODMwMWQYAgUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgIFI2N0bDAwJExvZ2luVmlldzEkTG9naW5TdGF0dXMxJGN0bDAxBSNjdGwwMCRMb2dpblZpZXcxJExvZ2luU3RhdHVzMSRjdGwwMwUjY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSRHcmlkVmlldzEPPCsADAEIZmRJji5QFtzlyXDVdUnh7mtgaKbCbA%3D%3D&__VIEWSTATEGENERATOR=6E03D851&__ASYNCPOST=true&'
G_BETTER_EDUCATION_BASE_URL = "https://bettereducation.com.au/"
G_TOP_PRIMARY_SCHOOL = "https://bettereducation.com.au/school/Primary/{0}/{1}_top_primary_schools.aspx"

header_completion = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Content-Length': '50',
        'Content-Type': 'application/json; charset=UTF-8'
}

header_school = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '941',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
}

header_top_school = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'bettereducation.com.au',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
}

payload_suburbs = {
        "count": '10',
        "contextKey": "null"
}

school_type_list = ['Any', 'Government', 'Non-government']
G_ANY_SCHOOL = "Any"


class BetterEducationException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class BetterEducationClass:
    """
    This class defines functions and parameters that are specific to the website better education:
    https://bettereducation.com.au/

    """

    def __init__(self, instance_base_param):
        self._bp = instance_base_param
        # Any, Government, Non-government
        self._all_flag = True
        if self._bp.school_gov_flag != G_ANY_SCHOOL and self._bp.school_gov_flag in school_type_list:
            self._gov_flag = self._bp.school_gov_flag
            self._all_flag = False

        if 0 <= int(self._bp.school_scores) <= 100:
            self._scores = self._bp.school_scores
        else:
            self._scores = 0

        self._school_dict = dict()

    def get_schools_from_top(self):
        url_top_primary = G_TOP_PRIMARY_SCHOOL.format(self._bp.state_name, self._bp.state_name)
        rst_content, rst_flag = URLHandlerClass.get_content_from_html(url_top_primary, header_top_school)
        if not rst_flag:
            print(rst_content)
            return
        else:
            """
            Parse the json file

            """
            print(rst_content)
            rst_bs4 = BeautifulSoup(rst_content, 'lxml')
            try:
                table_schools = rst_bs4.find('table', class_="table table-striped table-bordered table-hover")
                tbody_schools = table_schools.find('tbody')
                all_schools = tbody_schools.find_all('tr')
                for each_school in all_schools:
                    # key - school address; Value = ["school address", "scores", "school type", "Enrollments", "edu link", "my school link"]
                    info_school = SchoolParams()
                    school_properties = each_school.find_all('td')
                    school_address_info = school_properties[0].find('a')
                    school_address = school_address_info.text.strip()
                    if school_address in self._school_dict:
                        continue

                    school_score = school_properties[2].text.strip()
                    info_school.result_scores = school_score
                    debug_print(school_score)
                    if int(school_score) < int(self._scores):
                        continue

                    school_type_info = school_properties[7].text.strip()
                    info_school.result_school_type = school_type_info
                    debug_print(school_type_info)
                    if not self._all_flag and self._gov_flag != school_type_info:
                        continue

                    school_real_link = G_BETTER_EDUCATION_BASE_URL + school_address_info["href"]
                    info_school.result_school_address = school_address
                    info_school.result_better_education_link = school_real_link
                    debug_print(school_real_link)
                    debug_print(school_address)

                    school_enrollment_num = school_properties[5].text.strip()
                    info_school.result_enrollments = school_enrollment_num
                    debug_print(school_enrollment_num)

                    self._school_dict[school_address] = info_school

            except BaseException as err:
                print("BaseException:{0}-url page:{1}".format(str(err), G_EDU_SCHOOL))
        return self._school_dict

    def get_schools_from_suburb(self, location_name):
        # suburb payload
        # payload_suburb = {"prefixText": "suburb_name", "count": '10', "contextKey": "null"}
        # data_suburbs = json.dumps(payload_suburb)
        payload_suburbs["prefixText"] = location_name
        data_suburbs = json.dumps(payload_suburbs)

        rst_content, rst_flag = URLHandlerClass.post_content_from_html(G_EDU_COMPLETION, data_suburbs, header_completion)
        if not rst_flag:
            print(rst_content)
            return
        else:
            """
            Parse the json file

            """
            print(rst_content)
            data_response = json.loads(rst_content)
            debug_print(data_response)
            data_response_list = data_response["d"]
            debug_print(data_response_list)
            for each_candidate in data_response_list:
                debug_print(each_candidate)
                data_candidate = json.loads(each_candidate)
                for key, value in data_candidate.items():
                    if key == "First":
                        each_candidate_suburb = value
                        self._search_page_school(each_candidate_suburb)
        return self._school_dict

    def _search_page_school(self, each_candidate_suburb):
        url_encode_suburb = urllib.parse.quote(each_candidate_suburb)
        data_post = G_RAW_DATA_SCHOOL.format(url_encode_suburb)
        rst_content, rst_flag = URLHandlerClass.post_content_from_html(G_EDU_SCHOOL, data_post, header_school)
        if not rst_flag:
            print(rst_content)
            return
        else:
            """
            Parse the json file

            """
            print(rst_content)
            rst_bs4 = BeautifulSoup(rst_content, 'lxml')
            try:
                table_schools = rst_bs4.find('table', class_="table table-striped table-bordered table-hover")
                all_schools = table_schools.find_all('tr')
                for each_school in all_schools:
                    if each_school["style"] == "color:White;background-color:#5D7B9D;font-weight:bold;":
                        # skip first line
                        continue
                    else:
                        # key - school address; Value = ["school address", "scores", "school type", "Enrollments", "edu link", "my school link"]
                        info_school = SchoolParams()
                        school_properties = each_school.find_all('td')
                        school_address_info = school_properties[0].find('a')
                        school_address = school_address_info.text.strip()
                        if school_address in self._school_dict:
                            continue

                        school_score = school_properties[2].text.strip()
                        info_school.result_scores = school_score
                        debug_print(school_score)
                        if int(school_score) < int(self._scores):
                            continue

                        school_type_info = school_properties[7].text.strip()
                        info_school.result_school_type = school_type_info
                        debug_print(school_type_info)
                        if not self._all_flag and self._gov_flag != school_type_info:
                            continue

                        school_real_link = G_BETTER_EDUCATION_BASE_URL + school_address_info["href"]
                        info_school.result_school_address = school_address
                        info_school.result_better_education_link = school_real_link
                        debug_print(school_real_link)
                        debug_print(school_address)

                        school_enrollment_num = school_properties[6].text.strip()
                        info_school.result_enrollments = school_enrollment_num
                        debug_print(school_enrollment_num)

                        self._school_dict[school_address] = info_school
            except BaseException as err:
                print("BaseException:{0}-url page:{1}".format(str(err), G_EDU_SCHOOL))


# Main test
if __name__ == '__main__':
    pass

