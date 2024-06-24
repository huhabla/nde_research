import os
import json
import argparse
import logging
from tqdm import tqdm
from nde_research.database import create_connection, create_table, insert_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_files(input_file, db_name):
    conn = create_connection(db_name)
    if conn is None:
        return

    create_table(conn)

    with open(input_file, 'r') as f:
        md_files = f.read().splitlines()

    input_dir = os.path.dirname(os.path.abspath(input_file))

    for txt_file in tqdm(md_files, desc="Processing files"):
        txt_path = os.path.join(input_dir, txt_file)
        basename_path = os.path.splitext(txt_path)[0]
        json_path = basename_path + '.json'
        analysis_path = basename_path + '_analysis.md'
        url = f"https://www.nderf.org/Experiences/{txt_file.replace('.txt', '')}.html"

        if not os.path.exists(json_path):
            logger.warning(f"JSON file not found for {txt_file}. Skipping.")
            continue

        if not os.path.exists(txt_path):
            logger.warning(f"Markdown file not found for {txt_file}. Skipping.")
            continue

        # Read NDE report
        with open(txt_path, 'r', encoding="utf-8") as f:
            nde_report = f.read()

        # Read NDE analysis
        with open(analysis_path, 'r', encoding="utf-8") as f:
            nde_analysis = f.read()

        # Read JSON data
        with open(json_path, 'r', encoding="utf-8") as f:
            json_data = json.load(f)

        # Insert into database
        insert_data(conn, txt_file, url, nde_analysis, nde_report, json_data)

    conn.close()
    logger.info("All data has been processed and inserted into the database.")


def main():
    parser = argparse.ArgumentParser(description="Process NDE reports and store in SQLite database")
    parser.add_argument("input_file", help="Path to the file containing list of NDE report file names")
    parser.add_argument("--db_name", default="nde.db", help="Name of the SQLite database to create/use")
    args = parser.parse_args()

    db_path = os.path.join(os.getcwd(), args.db_name)
    process_files(args.input_file, db_path)


if __name__ == "__main__":
    main()
