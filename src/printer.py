import cups
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('printer.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

conn = cups.Connection()
printers = conn.getPrinters()
printer_name = list(printers.keys())[0]

def getPrintersList():
    return list(conn.getPrinters().keys())


def print_file(file_path, print_task="", options={}, printer_name=printer_name):
    logger.info(f"[{print_task}] Printing {file_path} on {printer_name}")
    job_id = conn.printFile(printer_name, file_path, print_task, options)
    try:
        job_attr = conn.getJobAttributes(job_id)
        logger.debug(f"{job_id} - {job_attr}")
        while conn.getJobs().get(job_id, None) is not None:
            job_attr = conn.getJobAttributes(job_id)
            logger.debug(f"{job_id} - {job_attr.get('job-state', None)}")
            if job_attr.get('job-state', None) == 9:
                logger.info("Job completed")
                break
            elif job_attr.get('job-state', None) == 7 or job_attr.get('job-state', None) == 8:
                logger.error("Job failed")
                break
            elif job_attr.get('job-state', None) == 5:
                logger.error("Job stopped")
                logger.error(job_attr.get('job-state-reasons', None))
            time.sleep(1)
        logger.info("Job completed")
    except Exception as e:
        logger.exception("Error while printing")
        logger.critical(e, exc_info=True)
        return False
