import sys
import os
import argparse
from bs4 import BeautifulSoup
from tqdm import tqdm


def html_to_txt(html_path, css_selector, relevance_hint, check_css):
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    if check_css:
        # Find the specified section
        section = soup.select_one(css_selector)

        if section is None:
            return None  # Section not found

        # Check for relevance hint
        if relevance_hint and relevance_hint not in str(section):
            return None  # Relevance hint not found

        # Remove script and style elements within the section
        for script in section(["script", "style"]):
            script.decompose()

        # Get text from the section
        text = section.get_text()
    else:
        # Process the entire document
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


def main(input_file, css_selector, relevance_hint, check_css):
    directory = os.path.dirname(input_file)

    with open(input_file, 'r') as file:
        html_files = file.read().splitlines()

    total_files = len(html_files)

    print(f"Starting conversion of {total_files} files...")
    print(f"CSS-based extraction: {'Enabled' if check_css else 'Disabled'}")
    if check_css:
        print(f"CSS Selector: {css_selector}")
        print(f"Relevance Hint: {relevance_hint or 'Not specified'}")

    converted_count = 0
    skipped_count = 0

    for i, html_file in enumerate(tqdm(html_files, total=total_files, unit="file")):
        html_path = os.path.join(directory, html_file)
        txt_file = os.path.splitext(html_file)[0] + '.txt'
        txt_path = os.path.join(directory, txt_file)

        markdown_content = html_to_txt(html_path, css_selector, relevance_hint, check_css)

        if markdown_content is None:
            tqdm.write(f"Skipped {i + 1}/{total_files}: {html_file} (Section not found or not relevant)")
            skipped_count += 1
            continue

        with open(txt_path, 'w', encoding='utf-8') as file:
            file.write(markdown_content)

        tqdm.write(f"Converted {i + 1}/{total_files}: {html_file} to {txt_file}")
        converted_count += 1

    print(f"\nConversion complete. Converted: {converted_count}, Skipped: {skipped_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert HTML files to Text")
    parser.add_argument("input_file", help="Path to the text file containing list of HTML files")
    parser.add_argument("--css", default="section.section_offset", help="CSS selector for the main content section")
    parser.add_argument("--hint", help="Relevance hint to search for within the CSS section")
    parser.add_argument("--check-css", action="store_true", help="Enable CSS-based extraction")
    args = parser.parse_args()

    main(args.input_file, args.css, args.hint, args.check_css)
