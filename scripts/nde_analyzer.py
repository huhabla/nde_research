import argparse
import logging
from tqdm import tqdm
import anthropic
import os
from nde_research.analyzer import process_nde_report, get_files_to_process

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Process NDE reports using Anthropic's Claude API using Sonnet 3.5")
    parser.add_argument("input_file", help="Path to the file containing list of NDE report file names")
    args = parser.parse_args()

    # Get the directory of the input file
    input_dir = os.path.dirname(os.path.abspath(args.input_file))

    # Initialize Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not found")
        raise ValueError("ANTHROPIC_API_KEY not found")

    client = anthropic.Anthropic(api_key=api_key)

    # Get files to process
    nde_report_files = get_files_to_process(args.input_file, input_dir)

    total_files = len(nde_report_files)
    logger.info(f"Found {total_files} NDE reports to process")

    # Process each NDE report with progress bar
    for i, file_name in enumerate(tqdm(nde_report_files, desc="Processing NDE reports"), 1):
        file_path = os.path.join(input_dir, file_name)
        logger.info(f"Processing file {i}/{total_files}: {file_path}")
        process_nde_report(file_path, client, input_dir)

    logger.info("NDE report processing completed")


if __name__ == "__main__":
    main()
