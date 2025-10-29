import os
import os.path
import pickle
from parser import parse_questions

def get_files_no_ext(folder_path = '/home/user/gcp-exam-maker/exams'):
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
                filename_without_ext, _ = os.path.splitext(item_name)
                parse_questions(f'{filename_without_ext}')
                print(filename_without_ext)
                
    except FileNotFoundError:
        print(f"Error: The folder path '{folder_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_pickles(folder_path = '/home/user/gcp-exam-maker/pickles'):
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
                    questions = pickle.load(f)
                    
                
    except FileNotFoundError:
        print(f"Error: The folder path '{folder_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    get_files_no_ext()
    get_pickles()