from rich import print
import logging
from rich.logging import RichHandler
import os
from datetime import datetime
import tarfile
import requests


# load environment variables from .env file for dev
from dotenv import load_dotenv
load_dotenv()

BACKUP_DIR = os.getenv("BACKUP_DIR", default="./data")
TMP_DIR = os.getenv("TMP_DIR", default="./tmp")

FILE_TARGETS = os.getenv("FILE_TARGETS", "").split(";")
PG_TARGETS = os.getenv("PG_TARGETS", "").split(";")
MMS_WEBHOOK = os.getenv("MMS_WEBHOOK", "")

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


def do_backup():
    logging.info("Backuptopus performing backup... 🦑")
    
    # create timestamped backup directory
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    
    tmpdir = f"{TMP_DIR}/backup_{timestamp}"
    os.makedirs(tmpdir, exist_ok=False)
    logging.info(f"Created backup directory: {tmpdir}")

    # copy files to backup directory
    for target in FILE_TARGETS:
        target_path = os.path.expanduser(target)
        if os.path.exists(target_path):
            os.system(f"cp -r {target_path} {tmpdir}/")
            logging.info(f"Copied {target_path} to {tmpdir}")
        else:
            logging.warning(f"Target path does not exist: {target_path}")

    # connect to psql and dump databases
    dump_sizes = {}
    for postgres_connection_string in PG_TARGETS:
        if not postgres_connection_string:
            continue
        db_name = postgres_connection_string.split("/")[-1]
        dump_file = f"{tmpdir}/{db_name}_backup_{timestamp}.sql"
        logging.debug(f"Running command: pg_dump {postgres_connection_string} > {dump_file}")
        os.system(f"pg_dump {postgres_connection_string} > {dump_file}")
        logging.info(f"Dumped database {db_name} to {dump_file}")
        if os.path.exists(dump_file):
            dump_size = os.path.getsize(dump_file)
            human_dump_size = "{:.2f} MB".format(dump_size / (1024 * 1024)) if dump_size > 1024 * 1024 else "{:.2f} KB".format(dump_size / 1024)
            dump_sizes[db_name] = dump_size
            logging.info(f"Dump file size for {db_name}: {human_dump_size}")
        else:
            logging.warning(f"Dump file not found for {db_name}: {dump_file}")

    # create tar.gz archive
    logging.info("Creating tar.gz archive...")
    archive_name = f"{BACKUP_DIR}/backup_{timestamp}.tar.gz"
    os.makedirs(BACKUP_DIR, exist_ok=True)
    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(tmpdir, arcname=os.path.basename(tmpdir))
    logging.info(f"Created archive: {archive_name}")
    archive_size = os.path.getsize(archive_name)
    human_size = "{:.2f} MB".format(archive_size / (1024 * 1024)) if archive_size > 1024 * 1024 else "{:.2f} KB".format(archive_size / 1024)
    logging.info(f"Archive size: {human_size}")

    # clean up temporary directory
    os.system(f"rm -rf {tmpdir}")
    logging.info(f"Cleaned up temporary directory: {tmpdir}")

    # mattermost notification
    if MMS_WEBHOOK:
        payload = {
            "username": "backuptopus",
            "channel": "mms-backups",
            "text": "Backup completed successfully 🦑\n",
            "attachments": [
                {
                    "color": "#36a64f",
                    "fields": [
                        {"title": "Archive Name", "value": os.path.basename(archive_name), "short": True},
                        {"title": "Archive Size", "value": human_size, "short": True},
                        *[
                            {"title": f"DB: {db}", "value": "{:.2f} MB".format(size / (1024 * 1024)) if size > 1024 * 1024 else "{:.2f} KB".format(size / 1024), "short": True}
                            for db, size in dump_sizes.items()
                        ]
                    ],
                }
            ],
            }
        response = requests.post(MMS_WEBHOOK, json=payload)
        if response.status_code == 200:
            logging.info("Sent Mattermost notification.")
        else:
            logging.error(f"Failed to send Mattermost notification. Status code: {response.status_code}")

if __name__ == "__main__":
    do_backup()
