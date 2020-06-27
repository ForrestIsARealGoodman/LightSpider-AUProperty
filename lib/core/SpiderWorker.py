from lib.property.Realestate import *
from lib.property.Domain import *
from lib.core.Logger import *


class SpiderWorkerException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class SpiderWorkerClass:
    def __init__(self, search_location, base_param_obj):
        self._re = RealEstateClass(base_param_obj)
        self._dn = DomainClass(base_param_obj)
        self._cur_loc = search_location

    def run_spider_job(self, logger_queue, log_level, crawler_sites, data_queue):
        spider_logger = LoggerClass.get_worker_logger(logger_queue, log_level)
        current_pid = os.getpid()
        sys.setrecursionlimit(25000)
        spider_logger.info("Started process[{0}]-location[{1}]...".format(current_pid, self._cur_loc))
        if self._re.get_crawler_site() in crawler_sites:
            self._re.run_search_task(spider_logger, data_queue)
        if self._dn.get_crawler_site() in crawler_sites:
            self._dn.run_search_task(spider_logger, data_queue)
        spider_logger.info("Ended process[{0}]-location[{1}]...".format(current_pid, self._cur_loc))
