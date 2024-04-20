from supabase import create_client

from src.printer import print_file
from src.printhubqueue import PrintHubQueue
from src.printhubserver import PrintHubServer

import tempfile
import logging
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('printer.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def check_internet(url):
    try:
        requests.get(url, timeout=5)
        return True
    except requests.ConnectionError:
        return False
    
def print_individual_record(client, location, printer_name, options={}):
    try:
        res = client.storage.from_("files_storage").download(location)
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(res)
            temp_file_location = os.path.abspath(temp_file.name)
            print(temp_file_location)
            print_file(file_path=temp_file_location, print_task=f"PrintHub - {time.strftime('%H:%M:%S')}", options=options, printer_name=printer_name)
    except Exception as e:
        logger.exception("Error while printing")

def printhub_server(client, printer_name):
    def print_record(record):
        total_files = len(record["file_path"])
        logger.debug(f"Printing {record}")
        for i in range(total_files):
            location = record['file_path'][i]
            option = record['options'][i] if i < len(record["options"]) else {}
            print_individual_record(client, location, options=option, printer_name=printer_name)
            client.storage.from_("files_storage").remove(location)
        client.table("file_storage").update({"status": ["COMPLETED"] * total_files}).eq("id", record["id"]).execute()
    return print_record

if __name__ == "__main__":
    SUPABASE_ID=os.environ.get("SUPABASE_ID")
    SUPABASE_API_KEY=os.environ.get("SUPABASE_API_KEY")

    while True:
        try:
            if check_internet(f"https://{SUPABASE_ID}.supabase.co"):
                supabase=create_client(f"https://{SUPABASE_ID}.supabase.co", SUPABASE_API_KEY)
                email = os.environ.get("PRINTER_EMAIL")
                password = os.environ.get("PRINTER_PASSWORD")
                user = supabase.auth.sign_in_with_password({"email": email, "password": password})
                access_token = user.session.access_token

                supabase_websocket = f"wss://{SUPABASE_ID}.supabase.co/realtime/v1/websocket?apikey={SUPABASE_API_KEY}&vsn=1.0.0"
                queue = PrintHubQueue(task=printhub_server(supabase, printer_name=os.environ.get("PRINTER_NAME")))
                ws = PrintHubServer(supabase_websocket, access_token=access_token, queue=queue)
                ws.run_forever()
            else:
                time.sleep(1)
        except Exception as e:
            logger.exception("Exception")