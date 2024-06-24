import argparse
import logging
from tqdm import tqdm
import anthropic
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from nde_research.jc_analyzer import process_nde_report, get_txt_files_to_process

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global flag to signal interruption
interrupted = False


def signal_handler(signum, frame):
    global interrupted
    interrupted = True
    logger.info("Interrupt received, stopping processing. Please wait for ongoing requests to finish...")


def process_file(file_name, input_dir, client):
    global interrupted
    if interrupted:
        return f"Skipped due to interruption: {file_name}"

    file_path = os.path.join(input_dir, file_name)
    try:
        process_nde_report(file_path, client, input_dir)
        return f"Processed: {file_path}"
    except Exception as e:
        return f"Error processing {file_path}: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="Process NDE reports using Anthropic's Claude API using Sonnet 3.5 to "
                                                 "analyze encounter with Jesus Christ and past life memories.")
    parser.add_argument("input_file", help="Path to the file containing list of NDE report file names")
    parser.add_argument("--parallel", type=int, default=1, help="Number of parallel requests to make")
    args = parser.parse_args()

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Get the directory of the input file
    input_dir = os.path.dirname(os.path.abspath(args.input_file))

    # Initialize Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not found")
        raise ValueError("ANTHROPIC_API_KEY not found")

    client = anthropic.Anthropic(api_key=api_key)

    # Get files to process
    nde_report_files = get_txt_files_to_process(args.input_file, input_dir)

    total_files = len(nde_report_files)
    logger.info(f"Found {total_files} NDE reports to process")

    # Process NDE reports in parallel
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        futures = [executor.submit(process_file, file_name, input_dir, client) for file_name in nde_report_files]

        completed = 0
        with tqdm(total=total_files, desc="Processing NDE reports") as pbar:
            for future in as_completed(futures):
                result = future.result()
                logger.info(result)
                completed += 1
                pbar.update(1)

                if interrupted:
                    break

        # Cancel any remaining futures
        for future in futures:
            future.cancel()

    if interrupted:
        logger.info("Processing was interrupted. Some files may not have been processed.")
    else:
        logger.info("NDE report processing completed")


if __name__ == "__main__":
    main()
