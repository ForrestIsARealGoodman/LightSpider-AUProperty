from multiprocessing import Queue
from lib.common.Util import *
import threading


# logger
class LoggerClass:
    worker_logger = None
    listener_logger = None
    cls_queue = Queue(-1)

    def __init__(self):
        pass

    @classmethod
    def get_worker_logger(cls, log_queue, log_level=logging.INFO):
        if cls.worker_logger is None:
            handler_queue = logging.handlers.QueueHandler(log_queue)  # Just the one handler needed
            formatter = logging.Formatter(
                "[%(asctime)s]-[%(processName)s-%(threadName)s-(%(levelname)s)%(filename)s:%(lineno)d]:%(message)s")
            handler_queue.setFormatter(formatter)
            root = logging.getLogger()
            root.addHandler(handler_queue)
            # send all messages, for demo; no other level or filter logic applied.
            root.setLevel(log_level)
            cls.worker_logger = logging.getLogger(str(os.getpid()))

        return cls.worker_logger

    @classmethod
    def get_listener_logger(cls):
        if cls.listener_logger is None:
            # logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S')
            cls.listener_logger = logging.getLogger(__name__)
            cls.listener_logger.setLevel(logging.DEBUG)

            # file handler
            handler_file = logging.handlers.TimedRotatingFileHandler(get_log_path(), "h", 1)
            cls.listener_logger.addHandler(handler_file)

            # Console handler
            console_handler = logging.StreamHandler()
            cls.listener_logger.addHandler(console_handler)

        return cls.listener_logger

    @classmethod
    def listener_thread(cls, logger_queue):
        logger = cls.get_listener_logger()
        logger.info("listener_thread started[{}]".format(threading.get_ident()))
        while True:
            try:
                record = logger_queue.get()
                if record is None:  # We send this as a sentinel to tell the listener to quit.
                    break
                # logger = logging.getLogger(record.name)
                logger.info(record.message)
                time.sleep(0.05)
            except Exception:
                print('Whoops! Problem:', file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
        logger.info("listener_thread finished[{}]".format(threading.get_ident()))


# Main test
if __name__ == '__main__':
    pass
