import os
import sys
from lib.parameter.BaseParam import *
# Writing to an excel
# sheet using Python
import xlsxwriter
from lib.common.Util import *
from datetime import datetime


class ReportHandlerException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class ReportHandlerClass:
    def __init__(self):
        self._excel_book = None
        self._excel_file = None
        # Key - search sub location; Value - PropertyParam list
        self._report_property = {}
        self._report_location = ""
        self._report_type = ""
        self._logger = None

    def insert_property_result(self, sub_location, property_list):
        if sub_location in self._report_property.keys():
            self._report_property[sub_location] += property_list
        else:
            self._report_property[sub_location] = property_list

    def write_to_excel(self, spider_logger):
        # first line
        # first_line = "house address, price, beds, baths, cars, land size, link"
        # Start from the first cell.
        # Rows and columns are zero indexed.
        self._logger = spider_logger
        if not self._report_property:
            self._logger.warning("Reports is empty")
            return None
        self._logger.info("Start to write reports to excel...")
        suburb_result_file = get_real_estate_data_path()
        suburb_result_file += self._report_type + "_" + self._report_location + \
                            "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".xlsx"
        workbook = xlsxwriter.Workbook(suburb_result_file)
        for key, value in self._report_property.items():
            sheet_name = key.replace(',', ' ')
            self._logger.info("Begin to write sub search location[{}]...".format(sheet_name))
            worksheet = workbook.add_worksheet(sheet_name)
            row = 0
            column = 0
            worksheet.write(row, column, G_STR_ADDRESS)
            worksheet.write(row, column + 1, G_STR_PRICE)
            worksheet.write(row, column + 2, G_STR_BEDS)
            worksheet.write(row, column + 3, G_STR_BATHS)
            worksheet.write(row, column + 4, G_STR_CARS)
            worksheet.write(row, column + 5, G_STR_SIZE)
            worksheet.write(row, column + 6, G_STR_LINK)
            row += 1
            for each_property in value:
                worksheet.write(row, column, each_property.result_address)
                worksheet.write(row, column + 1, each_property.result_price)
                worksheet.write(row, column + 2, each_property.result_beds)
                worksheet.write(row, column + 3, each_property.result_baths)
                worksheet.write(row, column + 4, each_property.result_cars)
                worksheet.write(row, column + 5, each_property.result_land_size)
                worksheet.write(row, column + 6, each_property.result_link)
                row += 1
        workbook.close()
        self._logger.info("Write Job completed! ")

    def send_to_emails(self):
        pass

    def upload_to_network_drive(self):
        pass

    @property
    def report_location(self):
        return self._report_location

    @report_location.setter
    def report_location(self, value):
        self._report_location = value

    @property
    def report_type(self):
        return self._report_type

    @report_type.setter
    def report_type(self, value):
        self._report_type = value




# Main test
if __name__ == '__main__':
    dict_test = {}
    dict_test['a1'] = ['aa1','aa2']
    dict_test['b1'] = ['bb1', 'bb2']
    debug_print(dict_test)
    test_a = "a1"
    test_v = ['aa3','aaa4']
    if test_a in dict_test.keys():
        dict_test[test_a] +=test_v
    else:
        dict_test[test_a] = test_v
    debug_print(dict_test)
