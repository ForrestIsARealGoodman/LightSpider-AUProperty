import sqlite3
from lib.common.Util import *
from enum import Enum
from datetime import datetime

G_SCHOOL_DISTRICT = "tb_school_district_{0}"
G_SCHOOL_PROPERTY = "tb_school_property_{0}"
G_SUBURB_PROPERTY = "tb_suburb_property_{0}"
G_TOP_PRIMARY_SCHOOL = "tb_top_primary_school_{0}"

G_SUB_NAME = "suburb_name"
G_SCH_NAME = "school_address"

# create
C_TABLE_SCH_TEMPLATE = "create table if not exists {0} (" \
                       "suburb_name varchar(30)," \
                       "school_address varchar(30), " \
                       "scores varchar(30), " \
                       "school_type varchar(30), " \
                       "enrollments varchar(30), " \
                       "better_education_link varchar(30), " \
                       "my_school_link varchar(30), " \
                       "update_date text) "

C_TABLE_PROPERTY_TEMPLATE = "create table if not exists {0} (" \
                                "{1} varchar(30)," \
                                "property_address varchar(30)," \
                                "ignore_flag varchar(30)," \
                                "price varchar(30), " \
                                "beds varchar(30), " \
                                "baths varchar(30), " \
                                "cars varchar(30), " \
                                "land_size varchar(30), " \
                                "link varchar(30), " \
                                "property_type varchar(30), " \
                                "statement varchar(30), " \
                                "update_date text)"
# insert
I_TABLE_SCH_TEMPLATE = "INSERT  INTO {0}(" \
                       "suburb_name," \
                       "school_address, " \
                       "scores, " \
                       "school_type, " \
                       "enrollments, " \
                       "better_education_link, " \
                       "my_school_link, " \
                       "update_date) " \
                       "values (?,?,?,?,?,?,?,?)"
# insert
I_TABLE_PROPERTY_TEMPLATE = "INSERT  INTO {0}(" \
                            "{1}," \
                            "property_address," \
                            "ignore_flag," \
                            "price, " \
                            "beds, " \
                            "baths, " \
                            "cars, " \
                            "land_size, " \
                            "link, " \
                            "property_type, " \
                            "statement, " \
                            "update_date) " \
                            "values (?,?,?,?,?,?,?,?,?,?,?,?)"

# select
S_TABLE_PROPERTY_TEMPLATE = "SELECT count(*) FROM {0} WHERE " \
                            "{1} = ? and " \
                            "property_address = ? and " \
                            "price = ? and " \
                            "beds = ? and " \
                            "baths = ? and " \
                            "cars = ? and " \
                            "land_size = ? and " \
                            "link = ? and " \
                            "property_type = ? and " \
                            "statement = ? " \
# delete
D_TABLE_PROPERTY_TEMPLATE = "DELETE FROM {0} WHERE " \
                            "{1} = ? and " \
                            "property_address = ? " \

# delete
D_TABLE_SCH_TEMPLATE = "DELETE FROM {0} WHERE " \
                       "suburb_name = ? and " \
                       "school_address = ? " \


class OperationType(Enum):
    Insert = 1
    Update = 2
    Delete = 3
    RemoveAll = 4


class SqliteLibException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class SqliteLibClass:
    def __init__(self, logger):
        self._conn_db = None
        self._cursor = None
        self._logger = logger
        """
        default table name
        """
        self._tb_school_district = ""
        self._tb_school_property = ""
        self._tb_suburb_property = ""
        self._tb_top_school = ""

    def initialize_db(self):
        db_path = os.path.join(get_db_path(), "AUProperty.db")
        try:
            self._conn_db = sqlite3.connect(db_path)
            self._conn_db.isolation_level = 'EXCLUSIVE'
            self._cursor = self._conn_db.cursor()

            # Create school district
            self._tb_school_district = G_SCHOOL_DISTRICT.format("all")
            table_school_district = C_TABLE_SCH_TEMPLATE.format(self._tb_school_district)
            debug_print(table_school_district)
            self._cursor.execute(table_school_district)

            # Create school property
            self._tb_school_property = G_SCHOOL_PROPERTY.format("all")
            table_school_property = C_TABLE_PROPERTY_TEMPLATE.format(self._tb_school_property, G_SCH_NAME)
            debug_print(table_school_property)
            self._cursor.execute(table_school_property)

            # Create suburb property
            self._tb_suburb_property = G_SUBURB_PROPERTY.format("all")
            table_suburb_property = C_TABLE_PROPERTY_TEMPLATE.format(self._tb_suburb_property, G_SUB_NAME)
            debug_print(table_suburb_property)
            self._cursor.execute(table_suburb_property)
            self._conn_db.commit()
        except sqlite3.Error as e:
            self._logger.info("Database error: {0}".format(e))
        except Exception as e:
            self._logger.info("Exception: {0}".format(e))

    def insert_property_in_suburb(self, suburb_name, property_item):
        """
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
        """
        try:
            # delete if possible
            sql_delete_property = D_TABLE_PROPERTY_TEMPLATE.format(self._tb_suburb_property, G_SUB_NAME)
            data_delete_tuple = (suburb_name, property_item.result_address)
            self._cursor.execute(sql_delete_property, data_delete_tuple)
            # insert record
            sql_suburb_property = I_TABLE_PROPERTY_TEMPLATE.format(self._tb_suburb_property, G_SUB_NAME)
            data_tuple = (suburb_name, property_item.result_address, "0", property_item.result_price
                          , property_item.result_beds, property_item.result_baths, property_item.result_cars
                          , property_item.result_land_size, property_item.result_link, property_item.result_type
                          , property_item.result_statements, str(datetime.now()))
            self._cursor.execute(sql_suburb_property, data_tuple)
            self._conn_db.commit()
        except sqlite3.Error as e:
            self._logger.info("Database error in insert_property_in_suburb: {0}".format(e))
        except Exception as e:
            self._logger.info("Exception in insert_property_in_suburb: {0}".format(e))

    def insert_property_in_school(self, school_name, property_item):
        try:
            # delete if possible
            # sql_delete_property = D_TABLE_PROPERTY_TEMPLATE.format(self._tb_school_property, G_SCH_NAME)
            # data_delete_tuple = (school_name, property_item.result_address)
            # self._cursor.execute(sql_delete_property, data_delete_tuple)
            # insert record
            sql_school_property = I_TABLE_PROPERTY_TEMPLATE.format(self._tb_school_property, G_SCH_NAME)
            data_tuple = (school_name, property_item.result_address, "0", property_item.result_price
                          , property_item.result_beds, property_item.result_baths, property_item.result_cars
                          , property_item.result_land_size, property_item.result_link, property_item.result_type
                          , property_item.result_statements, str(datetime.now()))
            self._cursor.execute(sql_school_property, data_tuple)
            self._conn_db.commit()
        except sqlite3.Error as e:
            self._logger.info("Database error in insert_property_in_school: {0}".format(e))
        except Exception as e:
            self._logger.info("Exception in insert_property_in_school: {0}".format(e))

    def insert_school_in_suburb(self, suburb_name, school_item_dict):
        for key in school_item_dict:
            school_item = school_item_dict[key]
            try:
                """
                "suburb," \
                       "school_address, " \
                       "scores, " \
                       "school_type, " \
                       "enrollments, " \
                       "better_education_link, " \
                       "my_school_link, " \
                       "update_date) " \
                """
                # delete if possible
                sql_delete_district = D_TABLE_SCH_TEMPLATE.format(self._tb_school_district)
                data_delete_tuple = (suburb_name, school_item.result_school_address)
                self._cursor.execute(sql_delete_district, data_delete_tuple)
                # insert record
                sql_school_district = I_TABLE_SCH_TEMPLATE.format(self._tb_school_district)
                data_tuple = (suburb_name, school_item.result_school_address
                              , school_item.result_scores, school_item.result_school_type
                              , school_item.result_enrollments, school_item.result_better_education_link
                              , school_item.result_my_school_link, str(datetime.now()))
                self._cursor.execute(sql_school_district, data_tuple)
                self._conn_db.commit()
            except sqlite3.Error as e:
                self._logger.info("Database error in insert_school_in_suburb: {0}".format(e))
            except Exception as e:
                self._logger.info("Exception in insert_school_in_suburb: {0}".format(e))

    def insert_top_primary_school_in_state(self, state_name, school_item_dict):
        tb_top_school_name = self._create_top_school_table(state_name)
        if tb_top_school_name is None:
            return

        for key in school_item_dict:
            school_item = school_item_dict[key]
            try:
                """
                "suburb," \
                       "school_address, " \
                       "scores, " \
                       "school_type, " \
                       "enrollments, " \
                       "better_education_link, " \
                       "my_school_link, " \
                       "update_date) " \
                """
                # delete if possible
                sql_delete_top = D_TABLE_SCH_TEMPLATE.format(tb_top_school_name)
                data_delete_tuple = ('N/A', school_item.result_school_address)
                self._cursor.execute(sql_delete_top, data_delete_tuple)
                # insert record
                sql_school_top = I_TABLE_SCH_TEMPLATE.format(tb_top_school_name)
                data_tuple = ('N/A', school_item.result_school_address
                              , school_item.result_scores, school_item.result_school_type
                              , school_item.result_enrollments, school_item.result_better_education_link
                              , school_item.result_my_school_link, str(datetime.now()))
                self._cursor.execute(sql_school_top, data_tuple)
                self._conn_db.commit()
            except sqlite3.Error as e:
                self._logger.info("Database error in insert_school_in_suburb: {0}".format(e))
            except Exception as e:
                self._logger.info("Exception in insert_school_in_suburb: {0}".format(e))

    def query_property_in_suburb(self, suburb_name, property_item):
        try:
            # check if row exists
            sql_query_property = S_TABLE_PROPERTY_TEMPLATE.format(self._tb_suburb_property, G_SUB_NAME)
            data_query_tuple = (suburb_name, property_item.result_address, property_item.result_price
                                , property_item.result_beds, property_item.result_baths, property_item.result_cars
                                , property_item.result_land_size, property_item.result_link, property_item.result_type
                                , property_item.result_statements)
            self._cursor.execute(sql_query_property, data_query_tuple)
            record_data = self._cursor.fetchone()[0]
            if record_data != 0:
                return True
        except sqlite3.Error as e:
            self._logger.info("Database error in query_property_in_suburb: {0}".format(e))
        except Exception as e:
            self._logger.info("Exception in query_property_in_suburb: {0}".format(e))
        return False

    def query_property_in_school(self, school_name, property_item):
        try:
            # check if row exists
            sql_query_property = S_TABLE_PROPERTY_TEMPLATE.format(self._tb_school_property, G_SCH_NAME)
            data_query_tuple = (school_name, property_item.result_address, property_item.result_price
                                , property_item.result_beds, property_item.result_baths, property_item.result_cars
                                , property_item.result_land_size, property_item.result_link, property_item.result_type
                                , property_item.result_statements)
            self._cursor.execute(sql_query_property, data_query_tuple)
            record_data = self._cursor.fetchone()[0]
            if record_data != 0:
                return True
        except sqlite3.Error as e:
            self._logger.info("Database error in query_property_in_suburb: {0}".format(e))
        except Exception as e:
            self._logger.info("Exception in query_property_in_suburb: {0}".format(e))
        return False

    def _create_top_school_table(self, state_name):
        tb_top_school = None
        try:
            # Create top school
            tb_top_school = G_TOP_PRIMARY_SCHOOL.format(state_name)
            table_top_school = C_TABLE_SCH_TEMPLATE.format(tb_top_school)
            debug_print(table_top_school)
            self._cursor.execute(table_top_school)
            self._conn_db.commit()
        except sqlite3.Error as e:
            self._logger.info("Creating table error in _create_top_school_table: {0}".format(e))
        except Exception as e:
            self._logger.info("Exception in _create_top_school_table: {0}".format(e))
        return tb_top_school


# Main test
if __name__ == '__main__':
    sl = SqliteLibClass(None)

