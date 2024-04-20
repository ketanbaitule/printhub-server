from collections import deque
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('printer.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class PrintHubQueue(deque):
    def __init__(self, task):
        super().__init__()
        self.task = task

    
    def waiting_time(self):
        time.sleep(3)
    
    def execute(self):
        while True:
            if len(self) > 0:
                record = self.popleft()
                print(record)
                try:
                    self.task(record)
                except Exception:
                    logger.exception("Error while executing task")
            self.waiting_time()
    
    def add(self, x):
        # TODO Update this to check if x is a dictionary
        try:
            if "file_path" not in x:
                raise ValueError("Task and Time key is required")
            logger.debug("adding to queue", x)
            return self.append(x)
        except Exception:
            logger.exception("Error while adding to queue")
            return False
