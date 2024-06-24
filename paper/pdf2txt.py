import argparse
import logging
import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    return text


def pdf_to_text(pdf_path):
    logging.info(f"Extracting text from {pdf_path}")

    try:
        text = convert_pdf_to_txt(pdf_path)
        return text
    except Exception as e:
        logging.error(f"Error extracting text: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to plain text using PDFMiner")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("-o", "--output", help="Output text file (default: same as input with .txt extension)")
    args = parser.parse_args()

    setup_logging()

    if not os.path.isfile(args.input) or not args.input.lower().endswith('.pdf'):
        logging.error("The provided file does not exist or is not a PDF.")
        return

    output_path = args.output if args.output else os.path.splitext(args.input)[0] + '.txt'

    text_content = pdf_to_text(args.input)

    if text_content is not None:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        logging.info(f"Conversion complete. Text file saved as: {output_path}")
    else:
        logging.error("Conversion failed.")


if __name__ == "__main__":
    main()
