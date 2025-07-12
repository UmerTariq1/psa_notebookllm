# python preprocess_whatsapp.py

import re
import itertools

# Path to the WhatsApp chat text file
INPUT_FILE_PATH = '/Users/umer/Desktop/a .nosync/personal projects/psarag/psa_notebookllm/data/input/whatsapp/psa_chat_4jul.txt'
OUTPUT_FILE_PATH = '/Users/umer/Desktop/a .nosync/personal projects/psarag/psa_notebookllm/data/output/whatsapp/'


NUMBERS_TO_REMOVE = ["Abdullah Chaudhry"]
MAKE_ANONYMOUS = True

# Function to generate unique IDs like AAA, AAB, AAC, etc.
def generate_unique_ids():
    for length in range(3, 4):  # Generating three-letter IDs
        for comb in itertools.product('ABCDEFGHIJKLMNOPQRSTUVWXYZ', repeat=length):
            yield ''.join(comb)

# Function to check if the line is a system message
def is_system_message(line):
    system_patterns = [
        r"created group",
        r"added you",
        r"changed the group description",
        r"joined using this group's invite link",
        r"added ",
        r"Messages and calls are end-to-end encrypted",
        r"image omitted",
        r"video omitted",
        r"Missed voice call",
        r"Missed video call",
        r"changed their phone number",
        r"This message was deleted.",
        r"Disappearing messages",
    ]
    
    for pattern in system_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False

# Function to check if a line starts with a timestamp (including lines that might start with LRM)
def starts_with_timestamp(line):
    line = line.lstrip('\u200e')  # Remove LRM if present
    return bool(re.match(r'^\[\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}:\d{2}\]', line))

def remove_mobile_numbers(text):
    # Regular expression pattern to match various mobile number formats
    return re.sub(r'\+?\d{1,4}[-.\s]?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[NUMBER REDACTED]', text)

def remove_special_characters(text):
    # remove the \u200e
    return text.replace('\u200e', '')

def is_remove_sender(sender):

    # check if any of the numbers to remove are in the sender
    for number in NUMBERS_TO_REMOVE:
        if number in sender:
            return True
    return False
    
    
# Function to extract messages and assign unique identifiers
def extract_messages_with_ids(lines, hide_sender_names=True):
    messages = []
    sender_mapping = {}
    id_generator = generate_unique_ids()
    current_message = ""
    current_sender = None
    add_msg = True

    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        
        if starts_with_timestamp(line):
            if current_message:
                # Save the current message before starting a new one
                if add_msg:
                    messages.append(f"{sender_mapping[current_sender]}: {current_message.strip()}")
                add_msg = True

            # Start processing the new message
            line = line.lstrip('\u200e')  # Remove LRM if present
            match = re.match(r'^\[\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}:\d{2}\] ([^:]+): (.+)', line)
            if match:
                current_sender = match.group(1).strip()
                message_text = match.group(2).strip()
                message_text = remove_mobile_numbers(match.group(2).strip())
                message_text = remove_special_characters(message_text)

                    
                if is_remove_sender(current_sender):
                    current_message = ""
                    add_msg = False

                if not is_system_message(message_text):
                    if current_sender not in sender_mapping:
                        if hide_sender_names:
                            sender_mapping[current_sender] = next(id_generator)
                        else:
                            sender_mapping[current_sender] = current_sender
                    current_message = message_text
                else:
                    current_message = ""
        else:
            # Continuation of the previous message
            if current_message:
                current_message += " " + line.strip()

    if current_message:
        # Append the last message after finishing the loop
        if add_msg:
            messages.append(f"{sender_mapping[current_sender]}: {current_message.strip()}")

    return messages

# Function to read chat log from a .txt file
def read_chat_log(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

# Function to write extracted messages to a new .txt file
def write_messages_to_file(output_path, messages):
    with open(output_path, 'w', encoding='utf-8') as file:
        for message in messages:
            file.write(message + '\n')

# Main script execution
def main():
    
    # Read the chat log
    chat_log = read_chat_log(INPUT_FILE_PATH)
    
    # Extract messages with unique IDs
    messages_with_ids = extract_messages_with_ids(chat_log, hide_sender_names=MAKE_ANONYMOUS)
    
    output_filepath_full = OUTPUT_FILE_PATH + INPUT_FILE_PATH.split('/')[-1].replace('.txt', '_processed.txt')
    write_messages_to_file(output_filepath_full, messages_with_ids)


if __name__ == "__main__":
    main()
