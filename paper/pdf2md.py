import argparse
import logging
import os
import pymupdf4llm
import pathlib

__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2024, Sören Gebbert"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@holistech.de"


def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def pdf_to_md(pdf_path):
    logging.info(f"Extracting text from {pdf_path}")

    try:
        md_text = pymupdf4llm.to_markdown(pdf_path)
        return md_text
    except Exception as e:
        logging.error(f"Error extracting text: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to markdown text using pymupdf4llm")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("-o", "--output", help="Output markdown file (default: same as input with .md extension)")
    args = parser.parse_args()

    setup_logging()

    if not os.path.isfile(args.input) or not args.input.lower().endswith('.pdf'):
        logging.error("The provided file does not exist or is not a PDF.")
        return

    output_path = args.output if args.output else os.path.splitext(args.input)[0] + '.md'

    md_text = pdf_to_md(args.input)

    if md_text is not None:
        pathlib.Path(output_path).write_bytes(md_text.encode())
        logging.info(f"Conversion complete. Text file saved as: {output_path}")
    else:
        logging.error("Conversion failed.")


if __name__ == "__main__":
    main()
