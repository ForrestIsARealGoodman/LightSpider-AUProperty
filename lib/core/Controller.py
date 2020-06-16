from lib.common.ConfigParser import *
from lib.common.Util import *
from lib.core.SpiderWorker import *


class ControllerException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg


class ControllerClass:
    # key - location_name; value - base_param_obj
    def __init__(self, dict_param):
        self._process_list = []
        self._dict_search = {}
        self._logger = None
        self._log_level = None
        self._log_queue = None
        self._listener = None
        self._crawler_sites = []
        self.initialize_params(dict_param)

    def initialize_params(self, dict_param):
        log_level = dict_param.log
        debug_print(log_level)
        if log_level is None:
            self._log_level = logging.INFO
        else:
            self._log_level = get_log_level(log_level)
        self._logger = LoggerClass.get_listener_logger()
        self._log_queue = multiprocessing.Queue(-1)
        self._listener = threading.Thread(target=LoggerClass.listener_thread, args=(self._log_queue,))
        self._listener.start()
        # Parse search config
        parse_project_search_file(get_search_config_path(), self._dict_search, self._crawler_sites)
        debug_print(self._dict_search)
        debug_print(self._crawler_sites)

    def start_job(self):
        self._logger.info("Start spider workers...")
        for key, value in self._dict_search.items():
            spider_worker = SpiderWorkerClass(key, value)
            process_worker = multiprocessing.Process(target=ControllerClass.run_job,
                                                     args=(spider_worker,
                                                           self._log_queue,
                                                           LoggerClass.get_worker_logger,
                                                           self._log_level,
                                                           self._crawler_sites))
            self._process_list.append(process_worker)

        for each_worker in self._process_list:
            each_worker.start()

        for each_worker in self._process_list:
            each_worker.join()

        self._log_queue.put_nowait(None)
        self._listener.join()

        self._logger.info("All spider workers completed - Please check the files under folder 'data'")

    @classmethod
    def run_job(cls, worker_obj, logger_queue, log_configurer, log_level, crawler_sites):
        worker_obj.run_spider_job(logger_queue, log_configurer, log_level, crawler_sites)


# Main test
if __name__ == '__main__':
    ControllerClass().start_job()
