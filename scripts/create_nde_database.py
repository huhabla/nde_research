import os
import json
import gzip
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

    for md_file in tqdm(md_files, desc="Processing files"):
        md_path = os.path.join(input_dir, md_file)
        json_path = os.path.splitext(md_path)[0] + '.json'

        if not os.path.exists(json_path):
            logger.warning(f"JSON file not found for {md_file}. Skipping.")
            continue

        # Read and compress MD content
        with open(md_path, 'rb') as f:
            compressed_content = gzip.compress(f.read())

        # Read JSON data
        with open(json_path, 'r') as f:
            json_data = json.load(f)

        # Insert into database
        insert_data(conn, md_file, json_data, compressed_content)

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
