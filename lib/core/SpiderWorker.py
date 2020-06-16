from lib.property.Realestate import *
from lib.property.Domain import *
import time


class SpiderWorkerException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class SpiderWorkerClass:
    def __init__(self, search_location, base_param_obj):
        self._rh = ReportHandlerClass(base_param_obj)
        self._rh.report_location = search_location
        self._rh.report_type = base_param_obj.source_type
        self._re = RealEstateClass(base_param_obj, self._rh)
        self._dn = DomainClass(base_param_obj, self._rh)

    def run_spider_job(self, logger_queue, log_configurer, log_level, crawler_sites):
        spider_logger = log_configurer(logger_queue, log_level)
        current_pid = os.getpid()
        location_name = self._rh.report_location
        spider_logger.info("Started process[{0}]-location[{1}]...".format(current_pid, location_name))
        if self._re.get_crawler_site() in crawler_sites:
            self._re.run_search_task(spider_logger)
        if self._dn.get_crawler_site() in crawler_sites:
            self._dn.run_search_task(spider_logger)
        self._rh.write_to_excel(spider_logger)
        spider_logger.info("Ended process[{0}]-location[{1}]...".format(current_pid, location_name))
