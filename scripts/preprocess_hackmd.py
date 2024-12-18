# python preprocess_hackmd.py data/hackmd.md data/output/hackmd_processed.txt

import re
import argparse

def preprocess_md(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    result = []
    current_heading = ''
    current_subheading = ''
    current_body = []
    inside_details = False
    date_pattern = re.compile(r'!\[written-on\]\(https://img\.shields\.io/badge/last_updated_on-([^\-]+)-blue\)')

    for line in lines:
        line = line.strip()

        # Check for date line and format it
        date_match = date_pattern.match(line)
        if date_match:
            date_str = date_match.group(1).replace('_', ' ')
            date_str = "Last updated on : " + date_str
            current_body.append(date_str)
            continue

        # Check for Heading 1
        if line.startswith('### '):
            # Append the previous Heading 1 section
            if current_heading:
                result.append(f'Heading 1: {current_heading}')
                if current_subheading:
                    result.append(f'Heading 2: {current_subheading}')
                    if current_body:
                        result.append('Body:')
                        result.append('\n'.join(current_body))
                result.append('\n')

            # Start a new Heading 1 section
            current_heading = line[4:].strip()
            current_subheading = ''
            current_body = []
            inside_details = False

        # Check for Heading 2
        elif line.startswith('<summary>'):
            summary_match = re.match(r'<summary>(.*?)</summary>', line)
            if summary_match:
                # Store the previous subheading section
                if current_subheading:
                    result.append(f'Heading 1: {current_heading}')
                    result.append(f'Heading 2: {current_subheading}')
                    if current_body:
                        result.append('Body:')
                        result.append('\n'.join(current_body))
                    result.append('\n')

                # Start a new subheading section
                current_subheading = summary_match.group(1).strip()
                current_body = []

        elif line.startswith('<details>'):
            inside_details = True

        elif line.startswith('</details>'):
            inside_details = False

        elif inside_details and not line.startswith('<summary>'):
            current_body.append(re.sub(r'<[^>]+>', '', line).strip())

        elif current_heading and current_subheading:
            current_body.append(line)

    # Append the last section
    if current_heading:
        result.append(f'Heading 1: {current_heading}')
        if current_subheading:
            result.append(f'Heading 2: {current_subheading}')
            if current_body:
                result.append('Body:')
                result.append('\n'.join(current_body))
        result.append('\n')

    with open(output_file, 'w', encoding='utf-8') as output:
        output.write('\n'.join(result))

def main():
    parser = argparse.ArgumentParser(description='Preprocess Markdown file for RAG training')
    parser.add_argument('input_file', type=str, help='Path to the input Markdown file')
    parser.add_argument('output_file', type=str, help='Path to the output file')

    args = parser.parse_args()
    preprocess_md(args.input_file, args.output_file)
    print(f'Processing complete. The output has been saved to {args.output_file}')

if __name__ == '__main__':
    main()
