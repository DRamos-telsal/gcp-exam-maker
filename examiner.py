import random
import textwrap
import os
import json
import pickle
from datetime import datetime

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_next():
    """Pauses the script until the user presses Enter."""
    input("\nPress Enter to continue to the next question...")

def load_questions(folder_path='/home/user/gcp-exam-maker/pickles'):
    all_questions = {}
    try:
        # Get a list of all items (files and folders) in the directory
        for item_name in os.listdir(folder_path):
            # Construct the full path
            full_path = os.path.join(folder_path, item_name)
            
            # Check if the item is a file
            if os.path.isfile(full_path):
                # Split the filename into the root and the extension
                # os.path.splitext handles cases where there are no extensions 
                # or multiple dots correctly.
                with open(f'{folder_path}/{item_name}', 'rb') as f:
                    name_no_ext = os.path.splitext(item_name)[0]
                    all_questions[name_no_ext] = pickle.load(f)
        
        return all_questions

    except FileNotFoundError:
        print(f"Error: The folder path '{folder_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def certification_questions(all_questions):
    questions = []
    print("Please choose one of the following certifications:")
    for certification, questions in all_questions.items():
        print(certification)
    while True:
        chosen = input("Your choose: ")
        if chosen in all_questions:
            questions = all_questions[chosen]
            break
        else:
            print("The selected certification was not found!")

    return questions


def get_exam_config(total_questions):
    """
    Asks the user how many questions they want and validates the input.
    """
    while True:
        try:
            num_str = input(f"How many questions would you like to attempt? (1-{total_questions}): ")
            num_int = int(num_str)
            
            if 1 <= num_int <= total_questions:
                return num_int
            else:
                print(f"Please enter a number between 1 and {total_questions}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def present_question(question, question_number, total_questions):
    """
    Displays a single question and its options, neatly formatted.
    Returns the user's answer as a set.
    """
    # Use textwrap for readable long questions
    wrapper = textwrap.TextWrapper(width=80, initial_indent="  ", subsequent_indent="  ")
    
    print(f"--- Question {question_number} of {total_questions} ---")
    print("\n" + wrapper.fill(question['statement']))
    print("-" * 80)

    # Sort options so they always appear in A, B, C... order
    for key, value in sorted(question['options'].items()):
        # Wrap option text as well
        option_text = f"  {key}: {value.strip()}"
        print(textwrap.fill(option_text, width=80, subsequent_indent="      "))

    # Check if it's a multiple-answer question
    is_multiple_choice = len(question['answers']) > 1
    
    if is_multiple_choice:
        prompt = "\nEnter your answers (e.g., A B): "
    else:
        prompt = "\nEnter your answer (e.g., A): "

    # Get and standardize answer
    user_input = input(prompt).upper().strip()
    # Split input by spaces and store in a set to handle "A B" or "B A"
    user_answer_set = set(user_input.split())
    
    return user_answer_set

def evaluate_answer(question, user_answer_set):
    """
    Checks the user's answer and prints feedback.
    Returns a dictionary with the result.
    """
    correct_answer_set = question['answers']
    is_correct = (user_answer_set == correct_answer_set)
    
    if is_correct:
        print("\n✅ Correct!")
    else:
        print("\n❌ Incorrect.")
        print(f"  Your answer(s):     {', '.join(sorted(list(user_answer_set)))}")
        print(f"  Correct answer(s):  {', '.join(sorted(list(correct_answer_set)))}")
        
        # Show what the correct options were
        print("\n  Correct Answer Details:")
        for key in sorted(list(correct_answer_set)):
            print(f"    {key}: {question['options'][key].strip()}")
            
    return {
        "statement": question['statement'],
        "options": question['options'],
        "user_answer": list(user_answer_set), # Convert set to list for JSON
        "correct_answer": list(correct_answer_set), # Convert set to list for JSON
        "is_correct": is_correct
    }

def run_exam(questions):
    """
    Main function to run the exam loop.
    """
    clear_screen()
    print("===== Starting the Exam =====")
    
    results = []
    correct_count = 0
    total_count = len(questions)
    
    for i, question in enumerate(questions, 1):
        clear_screen()
        user_answer_set = present_question(question, i, total_count)
        result = evaluate_answer(question, user_answer_set)
        
        results.append(result)
        if result["is_correct"]:
            correct_count += 1
            
        wait_for_next()

    # Calculate and display final score
    clear_screen()
    print("===== Exam Complete =====")
    score = (correct_count / total_count) * 100
    print(f"\nYou answered {correct_count} out of {total_count} questions correctly.")
    print(f"Your final grade: {score:.2f}%")
    
    return results, score

def save_results(results, score):
    """
    Saves the detailed results and final score to a timestamped JSON file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"exam_results_{timestamp}.json"
    
    # Get total correct/questions from the results list
    total_questions = len(results)
    correct_count = sum(1 for r in results if r['is_correct'])
    
    data_to_save = {
        "exam_date": timestamp,
        "final_score_percent": score,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "question_results": results
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"\nResults saved successfully to: {filename}")
    except IOError as e:
        print(f"\nError: Could not save results to file. {e}")

def main():
    """
    Main entry point for the script.
    """
    all_questions = load_questions()
    exam_questions = certification_questions(all_questions)
    if not exam_questions:
        print("No questions loaded. Exiting.")
        return
        
    print("Welcome to the CLI Exam!")
    print(f"There are a total of {len(exam_questions)} questions available.")
    
    num_to_ask = get_exam_config(len(exam_questions))
    
    # Randomly sample the requested number of questions
    selected_questions = random.sample(exam_questions, num_to_ask)
    assert(num_to_ask == len(selected_questions))
    results, score = run_exam(selected_questions)
    
    save_results(results, score)

if __name__ == "__main__":
    main()