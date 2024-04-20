# Printhub Server

This repository contains code for printhub server.

## Modules

1. src/printer: handles communication with the printer
2. src/printhubqueue: handles queue for printer
3. src/printhubserver: handles communication with the server

## Configuration

```bash
pip install -r ./requirements.txt
```

## Setting Up Printer

1. Go To `http://printer_ip:631/`
2. Go To Administration and add the printer
3. Set environment variable to `PRINTER_NAME=name_of_printer`

## Setting Up Environmental Variable

```env
SUPABASE_ID=""
SUPABASE_API_KEY=""
PRINTER_EMAIL=""
PRINTER_PASSWORD=""
PRINTER_NAME=""
```

## Running Application

```bash
python printhub.py
```

## Checking Log File

```bash
tail -f ./printer.log
```
