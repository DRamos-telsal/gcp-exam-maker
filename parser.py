import re
import pickle

option_pattern = re.compile(r'\*\*([A-Z]):\*\*', re.MULTILINE)

answer_pattern = re.compile(r'\*\*Answer: ([A-Z]*)\*\*', re.MULTILINE)

timestamp_pattern = re.compile(r'\*\*Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\*\*')

pos = 0

def parse_statement(block_lines):
    statement = ''
    global pos
    for i, line in enumerate(block_lines):
        if '## Examtopics' in line:
            continue
        if not line.strip():
            continue
        if re.match(option_pattern, line):
            pos = i
            break
        statement += line


    return statement
    

def parse_options(block):
    # Find the start of the options to separate the question text
    options = {}
    current_option = ''
    letter = ''
    global pos
    for i, line in enumerate(block[pos:]):
        if re.search(answer_pattern, line):
            options[letter] = current_option
            break
        letter_match = re.search(option_pattern, line)
        if letter_match:
            if letter:
                options[letter] = current_option
            letter = letter_match.group(1)
            line = re.sub(option_pattern, '', line)
            current_option = ''
        if(line.strip()):
            current_option += line + '\n'

        
    
    return options
    

def parse_answer(block):
    answer_match = re.search(answer_pattern, block)
    
    answer_set = set(answer_match.group(1))

    return answer_set

def parse_timestamp(block):
    timestamp = re.search(timestamp_pattern, block).group(1)
    return timestamp


def parse_exam_questions(file_path):
    """
    Parses an exam questions text file and extracts questions, options,
    answers, and timestamps.

    Args:
        file_path (str): The path to the text file containing the questions.

    Returns:
        list: A list of dictionaries, where each dictionary represents a
              parsed question. Returns an empty list if the file is not found.
    """
    try:
        with open(f'exams/{file_path}', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []

    # Each question is separated by a horizontal rule
    question_blocks = content.strip().split('----------------------------------------')
    
    parsed_questions = []

    # Regex patterns to find the different parts of each question
    # This pattern finds options like "A: Some text"

    for block in question_blocks:
        if not block.strip():
            continue

        block = block.splitlines()
        
        statement = parse_statement(block)

        current_options = parse_options(block)
        
        block = '\n'.join(block)

        current_answers = parse_answer(block)

        current_timestamp = parse_timestamp(block)
        
        if not statement:
            print(block)

        parsed_questions.append({
            'statement': statement,
            'options': current_options,
            'answers': current_answers,
            'timestamp': current_timestamp
        })

    parsed_questions.sort(key=lambda question: question['timestamp'])
    
    return parsed_questions

def save_as_pickle(data, output_filename):
    """
    Serializes a Python object into a .pkl file.

    Args:
        data (any): The Python object to serialize.
        output_filename (str): The name of the output .pkl file.
    """
    with open(output_filename, 'wb') as f:
        pickle.dump(data, f)
    print(f"Data successfully saved to '{output_filename}'")


def parse_questions(input_file_no_ext):
    input_file = input_file_no_ext + '.txt'
    all_questions = parse_exam_questions(input_file)

    if all_questions:
        output_file = 'pickles/'+input_file_no_ext + '.pkl'
        save_as_pickle(all_questions, output_file)
        print(f'{output_file} saved')


# --- Main execution ---
if __name__ == "__main__":
    input_file = "pca.txt"
    
    # 2. Parse the file
    all_questions = parse_exam_questions(input_file)

    # 3. Save the result to a .pkl file
    if all_questions:
        output_file = "parsed_questions.pkl"
        save_as_pickle(all_questions, output_file)

        # (Optional) Print the parsed data to verify
        import pprint
        pprint.pprint(all_questions)