from lib.parameter.BaseParam import *
# Writing to an excel
# sheet using Python
import xlsxwriter
from lib.core.Logger import *
from lib.common.SqliteLib import *
import threading

G_MULTIPLE = 'Multiple'
G_SINGLE = 'Single'
G_SCHOOL_ASSEMBLY = 'School Assembly'
G_SCHOOL_DISTRICT = 'School District'


class ReportHandlerException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class ReportHandlerClass:
    def __init__(self, instance_base_param):
        self._bp = instance_base_param
        self._excel_book = None
        self._excel_file = None
        # Key - search sub location; Value - PropertyParam list
        self._report_suburb_property = {}
        self._report_school_property = {}
        self._report_school = {}
        self._report_location = ""
        self._report_type = ""
        self._report_school_type = "school"
        self._logger = None

        # report school sheet
        self._single_flag = True
        if self._bp.school_report_sheet == G_MULTIPLE:
            self._single_flag = False

    def insert_suburb_property_result(self, sub_location, property_list):
        if sub_location in self._report_suburb_property.keys():
            self._report_suburb_property[sub_location] += property_list
        else:
            self._report_suburb_property[sub_location] = property_list

    def insert_suburb_property_record(self, sub_location, property_record):
        if sub_location not in self._report_suburb_property.keys():
            self._report_suburb_property[sub_location] = list()
        self._report_suburb_property[sub_location].append(property_record)

    def insert_school_property_result(self, sch_location, property_list):
        if sch_location in self._report_school_property.keys():
            self._report_school_property[sch_location] += property_list
        else:
            self._report_school_property[sch_location] = property_list

    def insert_school_property_record(self, sch_location, property_record):
        if sch_location not in self._report_school_property.keys():
            self._report_school_property[sch_location] = list()
        self._report_school_property[sch_location].append(property_record)

    def insert_school_list_result(self, school_dict):
        self._report_school = {k: v for k, v in school_dict.items()}

    def insert_school_record(self, school_name, school_record):
        self._report_school[school_name] = school_record

    def write_to_excel(self, spider_logger):
        self._logger = spider_logger
        self._write_suburb_property_to_excel()
        self._write_school_property_to_excel()

    def _write_suburb_property_to_excel(self):
        # first line
        # first_line = "house address, price, beds, baths, cars, land size, link"
        # Start from the first cell.
        # Rows and columns are zero indexed.
        if not self._report_suburb_property:
            self._logger.warning("Suburb property is empty")
            return None
        self._logger.info("Start to write suburb property reports to excel...")
        suburb_result_file = get_data_path_with_date()
        suburb_result_file += self._report_type + "_" + self._report_location + \
                            "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".xlsx"
        workbook = xlsxwriter.Workbook(suburb_result_file)
        for key, value in self._report_suburb_property.items():
            sheet_name = key.replace(',', ' ')
            self._logger.info("Begin to write sub search location[{}]...".format(sheet_name))
            worksheet = workbook.add_worksheet(sheet_name)
            row = 0
            column = 0
            yellow_format = workbook.add_format({'bg_color': '#FFF200'})
            worksheet.set_row(row, cell_format=yellow_format)
            worksheet.write(row, column, G_STR_ADDRESS)
            worksheet.write(row, column + 1, G_STR_PRICE)
            worksheet.write(row, column + 2, G_STR_BEDS)
            worksheet.write(row, column + 3, G_STR_BATHS)
            worksheet.write(row, column + 4, G_STR_CARS)
            worksheet.write(row, column + 5, G_STR_SIZE)
            worksheet.write(row, column + 6, G_STR_LINK)
            worksheet.write(row, column + 7, G_STR_STATEMENT)
            row += 1
            for each_property in value:
                worksheet.write(row, column, each_property.result_address)
                worksheet.write(row, column + 1, each_property.result_price)
                worksheet.write(row, column + 2, each_property.result_beds)
                worksheet.write(row, column + 3, each_property.result_baths)
                worksheet.write(row, column + 4, each_property.result_cars)
                worksheet.write(row, column + 5, each_property.result_land_size)
                worksheet.write(row, column + 6, each_property.result_link)
                worksheet.write(row, column + 7, each_property.result_statements)
                row += 1
        workbook.close()
        self._logger.info("Write Job completed! ")

    def _write_school_property_to_excel(self):
        # first sheet - school list
        # "school address", "scores", "school type", "Enrollments", "edu link", "my school link"
        # left sheets
        # first_line = "house address, price, beds, baths, cars, land size, link, type, remarks"
        # Start from the first cell.
        # Rows and columns are zero indexed.
        suburb_result_file = get_data_path_with_date()
        if self._bp.crawler_school_target == G_SCH_TARGET_TOP:
            suburb_result_file += self._report_school_type \
                                  + "_" + self._bp.school_scores + "+" \
                                  + "_" + self._bp.state_name \
                                  + "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".xlsx"
        else:
            suburb_result_file += self._report_school_type \
                                  + "_" + self._bp.school_scores + "+" \
                                  + "_" + self._report_location \
                                  + "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".xlsx"

        if not self._report_school:
            self._logger.warning("School Reports is empty")
            return None
        if not self._report_school_property:
            self._logger.warning("School property Reports is empty")
            return None
        self._logger.info("Start to write school property reports to excel...")

        workbook = xlsxwriter.Workbook(suburb_result_file)
        self._write_school_list_internal(workbook)
        if self._single_flag:
            self._write_school_property_internal_with_single_sheet(workbook)
        else:
            self._write_school_property_internal_with_multiple_sheets(workbook)
        workbook.close()
        self._logger.info("Write Job completed! ")

    def _write_school_list_internal(self, workbook):
        # Add school list
        # "school address", "scores", "school type", "Enrollments", "edu link", "my school link"
        '''
        G_SCH_ADDRESS = "school_address"
        G_SCH_SCORE = "scores"
        G_SCH_TYPE = "school_type"
        G_SCH_ENROLL = "enrollments"
        G_SCH_EDU = "better_education_link"
        G_SCH_MY = "my_school_link"
        self.result_school_address = "N/A"
        self.result_scores = "N/A"
        self.result_school_type = "N/A"
        self.result_enrollments = "N/A"
        self.result_better_education_link = "N/A"
        self.result_my_school_link = "N/A"
        '''
        worksheet = workbook.add_worksheet(G_SCHOOL_ASSEMBLY)
        self._logger.info("Begin to write location list in suburb[{0}]...".format("school information"))
        row = 0
        column = 0
        yellow_format = workbook.add_format({'bg_color': '#FFF200'})
        worksheet.set_row(row, cell_format=yellow_format)
        worksheet.write(row, column, G_SCH_ADDRESS)
        worksheet.write(row, column + 1, G_SCH_SCORE)
        worksheet.write(row, column + 2, G_SCH_TYPE)
        worksheet.write(row, column + 3, G_SCH_ENROLL)
        worksheet.write(row, column + 4, G_SCH_EDU)
        worksheet.write(row, column + 5, G_SCH_MY)
        row += 1
        for key, value in self._report_school.items():
            worksheet.write(row, column, value.result_school_address)
            worksheet.write(row, column + 1, value.result_scores)
            worksheet.write(row, column + 2, value.result_school_type)
            worksheet.write(row, column + 3, value.result_enrollments)
            worksheet.write(row, column + 4, value.result_better_education_link)
            worksheet.write(row, column + 5, value.result_my_school_link)
            row += 1
        return row

    def _write_school_property_internal_with_multiple_sheets(self, workbook):
        for key, value in self._report_school_property.items():
            sheet_name = key.replace(',', ' ')
            self._logger.info("Begin to write sub search location[{}]...".format(sheet_name))
            worksheet = workbook.add_worksheet(sheet_name)
            row = 0
            column = 0
            yellow_format = workbook.add_format({'bg_color': '#FFF200'})
            worksheet.set_row(row, cell_format=yellow_format)
            worksheet.write(row, column, G_STR_ADDRESS)
            worksheet.write(row, column + 1, G_STR_PRICE)
            worksheet.write(row, column + 2, G_STR_BEDS)
            worksheet.write(row, column + 3, G_STR_BATHS)
            worksheet.write(row, column + 4, G_STR_CARS)
            worksheet.write(row, column + 5, G_STR_SIZE)
            worksheet.write(row, column + 6, G_STR_LINK)
            worksheet.write(row, column + 7, G_STR_TYPE)
            row += 1
            for each_property in value:
                worksheet.write(row, column, each_property.result_address)
                worksheet.write(row, column + 1, each_property.result_price)
                worksheet.write(row, column + 2, each_property.result_beds)
                worksheet.write(row, column + 3, each_property.result_baths)
                worksheet.write(row, column + 4, each_property.result_cars)
                worksheet.write(row, column + 5, each_property.result_land_size)
                worksheet.write(row, column + 6, each_property.result_link)
                worksheet.write(row, column + 7, each_property.result_type)
                row += 1

    def _write_school_property_internal_with_single_sheet(self, workbook):
        last_row = 0
        column = 0
        worksheet = workbook.add_worksheet(G_SCHOOL_DISTRICT)
        yellow_format = workbook.add_format({'bg_color': '#FFF200'})
        worksheet.set_row(last_row, cell_format=yellow_format)
        worksheet.write(last_row, column, G_STR_ADDRESS)
        worksheet.write(last_row, column + 1, G_STR_PRICE)
        worksheet.write(last_row, column + 2, G_STR_BEDS)
        worksheet.write(last_row, column + 3, G_STR_BATHS)
        worksheet.write(last_row, column + 4, G_STR_CARS)
        worksheet.write(last_row, column + 5, G_STR_SIZE)
        worksheet.write(last_row, column + 6, G_STR_LINK)
        worksheet.write(last_row, column + 7, G_STR_TYPE)
        worksheet.write(last_row, column + 8, G_STR_STATEMENT)
        last_row += 1
        for key, value in self._report_school_property.items():
            school_property = self._report_school[key]
            school_scores = school_property.result_scores
            school_sheet_name_c1 = key
            school_scores_c2 = "Scores: {0}".format(school_scores)
            yellow_format = workbook.add_format({'bg_color': '#87CEFA'})
            worksheet.set_row(last_row, cell_format=yellow_format)
            worksheet.write(last_row, column, school_sheet_name_c1)
            worksheet.write(last_row, column + 1, school_scores_c2)
            worksheet.write(last_row, column + 2, G_STRING_NULL)
            worksheet.write(last_row, column + 3, G_STRING_NULL)
            worksheet.write(last_row, column + 4, G_STRING_NULL)
            worksheet.write(last_row, column + 5, G_STRING_NULL)
            worksheet.write(last_row, column + 6, G_STRING_NULL)
            worksheet.write(last_row, column + 7, G_STRING_NULL)
            worksheet.write(last_row, column + 8, G_STRING_NULL)
            self._logger.info("Begin to write school properties[{}]...".format(school_sheet_name_c1))
            last_row += 1
            for each_property in value:
                worksheet.write(last_row, column, each_property.result_address)
                worksheet.write(last_row, column + 1, each_property.result_price)
                worksheet.write(last_row, column + 2, each_property.result_beds)
                worksheet.write(last_row, column + 3, each_property.result_baths)
                worksheet.write(last_row, column + 4, each_property.result_cars)
                worksheet.write(last_row, column + 5, each_property.result_land_size)
                worksheet.write(last_row, column + 6, each_property.result_link)
                worksheet.write(last_row, column + 7, each_property.result_type)
                worksheet.write(last_row, column + 8, each_property.result_statements)
                last_row += 1

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


class ReportManagerClass:
    def __init__(self, db_obj, increment_flag):
        # key - report location;
        # value: report object
        self._report_dict = dict()
        self._db = db_obj
        self._increment_flag = increment_flag

    def initialize_db_connection(self):
        self._db.initialize_db()

    def add_report_object(self, report_location, instance_base_param):
        if report_location not in self._report_dict:
            report_obj = ReportHandlerClass(instance_base_param)
            report_obj.report_location = report_location
            report_obj.report_type = instance_base_param.source_type
            self._report_dict[report_location] = report_obj

    def insert_report_object(self, report_data_obj):
        report_type = report_data_obj.report_type
        report_location = report_data_obj.report_location
        search_location = report_data_obj.search_location
        search_record = report_data_obj.search_record
        if report_location in self._report_dict:
            report_obj = self._report_dict[report_location]
            """
            class ReportType(Enum):
                SuburbProperty = 1
                SchoolProperty = 2
                SchoolInfo = 3
                NullInfo = 4
            """
            if report_type == ReportType.SuburbProperty:
                exists_flag = self._db.query_property_in_suburb(search_location, search_record)
                if exists_flag:
                    if not self._increment_flag:
                        report_obj.insert_suburb_property_record(search_location, search_record)
                else:
                    self._db.insert_property_in_suburb(search_location, search_record)
                    report_obj.insert_suburb_property_record(search_location, search_record)

            elif report_type == ReportType.SchoolProperty:
                exists_flag = self._db.query_property_in_school(search_location, search_record)
                if exists_flag:
                    if not self._increment_flag:
                        report_obj.insert_school_property_record(search_location, search_record)
                else:
                    report_obj.insert_school_property_record(search_location, search_record)
                    self._db.insert_property_in_school(search_location, search_record)
            elif report_type == ReportType.SchoolDistrict:
                report_obj.insert_school_list_result(search_record)
                self._db.insert_school_in_suburb(search_location, search_record)
            elif report_type == ReportType.SchoolTop:
                report_obj.insert_school_list_result(search_record)
                self._db.insert_school_in_suburb(search_location, search_record)

    def dump_reports(self, logger_obj):
        for key in self._report_dict:
            self._report_dict[key].write_to_excel(logger_obj)

    @classmethod
    def get_report_thread(cls, data_queue, report_manager_obj):
        report_manager_obj.initialize_db_connection()
        logger = LoggerClass.get_listener_logger()
        logger.info("get_report_thread started[{}]".format(threading.get_ident()))
        while True:
            try:
                report_data = data_queue.get()
                if report_data is None:  # We send this as a sentinel to tell the listener to quit.
                    break
                report_manager_obj.insert_report_object(report_data)
                # logger = logging.getLogger(record.name)
                logger.info(report_data.search_record)
                time.sleep(0.05)
            except data_queue.Empty:
                continue
            except BaseException:
                print('Whoops! Problem:', file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
        logger.info("get_report_thread finished[{}]".format(threading.get_ident()))


# Main test
if __name__ == '__main__':
    pass
