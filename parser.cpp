#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <regex>
#include <sstream>

// --- Data Structure for a Parsed Question ---
struct ParsedQuestion {
    std::string statement;
    std::map<char, std::string> options;
    std::set<char> answers;
    std::string timestamp;

    // Helper function to convert the struct to a displayable string
    std::string toString() const {
        std::stringstream ss;
        ss << "Statement: " << statement << "\n";
        ss << "Options:\n";
        for (const auto& pair : options) {
            ss << "  " << pair.first << ": " << pair.second;
        }
        ss << "Answers: {";
        for (char a : answers) {
            ss << a << " ";
        }
        ss << "}\n";
        ss << "Timestamp: " << timestamp << "\n";
        return ss.str();
    }
};

// --- Global Position Tracker (Equivalent to Python's global pos) ---
// This is generally discouraged in modern C++, but kept for a direct translation of the original logic.
size_t g_pos = 0;

// --- Regex Patterns (Compiled at File Scope) ---
const std::regex OPTION_PATTERN(R"(\*\*([A-Z]):\*\*|\*\*([A-Z]):\*\*[\r\n]?)", std::regex::multiline); // Adjusted for raw string literal in C++
const std::regex ANSWER_PATTERN(R"(\*\*Answer: ([A-Z]*)\*\*|\*\*Answer: ([A-Z]*)\*\*[\r\n]?)", std::regex::multiline);
const std::regex TIMESTAMP_PATTERN(R"(\*\*Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\*\*|\*\*Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\*\*[\r\n]?)");

/**
 * @brief Parses the question statement from a block of lines.
 * @param block_lines The lines of the current question block.
 * @return The extracted statement string.
 */
std::string parse_statement(const std::vector<std::string>& block_lines) {
    std::string statement = "";
    size_t start_pos = g_pos;
    
    // Clear the global position before starting the search
    g_pos = 0;

    for (size_t i = start_pos; i < block_lines.size(); ++i) {
        const std::string& line = block_lines[i];

        if (line.find("## Examtopics") != std::string::npos) {
            continue;
        }
        if (line.find_first_not_of(" \t\n\r") == std::string::npos) {
            continue; // line.strip() equivalent
        }

        statement += line + "\n"; // Append line and newline

        if (std::regex_search(line, OPTION_PATTERN)) {
            g_pos = i + 1; // Set the global position to the line *after* the statement ends (i.e., first option line)
            break;
        }
    }
    return statement;
}

/**
 * @brief Parses the options from a block of lines, starting from g_pos.
 * @param block_lines The lines of the current question block.
 * @return A map of option letters to option text.
 */
std::map<char, std::string> parse_options(const std::vector<std::string>& block_lines) {
    std::map<char, std::string> options;
    std::string current_option = "";
    char letter = '\0';
    size_t start_pos = g_pos;

    // Reset global position before returning
    g_pos = 0; 

    for (size_t i = start_pos; i < block_lines.size(); ++i) {
        const std::string& line = block_lines[i];
        std::smatch match;

        if (std::regex_search(line, match, OPTION_PATTERN)) {
            // Check if a previous option was being built
            if (letter != '\0') {
                options[letter] = current_option;
            }

            // The option letter is in the first or second capture group
            std::string letter_str = (match[1].matched) ? match[1].str() : match[2].str();
            
            // Check if the current line matches the answer/timestamp patterns to stop option parsing
            if (std::regex_search(line, ANSWER_PATTERN) || std::regex_search(line, TIMESTAMP_PATTERN)) {
                break;
            }

            if (!letter_str.empty()) {
                letter = letter_str[0];
                current_option = ""; // Start building the new option text
                
                // Remove the option pattern from the line to get the remaining text
                std::string processed_line = std::regex_replace(line, OPTION_PATTERN, "");
                current_option += processed_line + "\n";
            }
        } else {
            // Line is part of the current option text
            if (std::regex_search(line, ANSWER_PATTERN) || std::regex_search(line, TIMESTAMP_PATTERN)) {
                break; // Stop when the answer/timestamp section is reached
            }
            if (letter != '\0') {
                 current_option += line + "\n";
            }
        }
    }

    // Add the last parsed option
    if (letter != '\0') {
        options[letter] = current_option;
    }

    return options;
}

/**
 * @brief Parses the correct answers from the block string.
 * @param block_content The entire block content as a single string.
 * @return A set of correct answer letters.
 */
std::set<char> parse_answer(const std::string& block_content) {
    std::smatch match;
    std::set<char> answer_set;

    if (std::regex_search(block_content, match, ANSWER_PATTERN) && (match[1].matched || match[2].matched)) {
        // The answer string is in the first or second capture group
        std::string answer_str = (match[1].matched) ? match[1].str() : match[2].str();
        for (char c : answer_str) {
            answer_set.insert(c);
        }
    }

    return answer_set;
}

/**
 * @brief Parses the timestamp from the block string.
 * @param block_content The entire block content as a single string.
 * @return The extracted timestamp string.
 */
std::string parse_timestamp(const std::string& block_content) {
    std::smatch match;
    std::string timestamp = "";

    if (std::regex_search(block_content, match, TIMESTAMP_PATTERN) && (match[1].matched || match[2].matched)) {
        // The timestamp is in the first or second capture group
        timestamp = (match[1].matched) ? match[1].str() : match[2].str();
    }
    
    return timestamp;
}

/**
 * @brief Parses an exam questions text file.
 * @param file_path The path to the text file.
 * @return A vector of ParsedQuestion structs.
 */
std::vector<ParsedQuestion> parse_exam_questions(const std::string& file_path) {
    std::ifstream file(file_path);
    std::vector<ParsedQuestion> parsed_questions;
    std::string content;
    std::string line;

    if (!file.is_open()) {
        std::cerr << "Error: The file '" << file_path << "' was not found." << std::endl;
        return parsed_questions;
    }

    // Read the entire file content into a single string
    std::stringstream buffer;
    buffer << file.rdbuf();
    content = buffer.str();

    // Split content by '----------------------------------------'
    const std::string DELIMITER = "----------------------------------------";
    size_t last = 0;
    size_t next = 0;

    while ((next = content.find(DELIMITER, last)) != std::string::npos) {
        std::string block_content = content.substr(last, next - last);
        last = next + DELIMITER.length();

        if (block_content.find_first_not_of(" \t\n\r") == std::string::npos) {
            continue;
        }

        // Split the block into lines for statement/options parsing
        std::stringstream ss(block_content);
        std::vector<std::string> block_lines;
        std::string block_line;
        while (std::getline(ss, block_line)) {
            // Trim trailing carriage return if present
            if (!block_line.empty() && block_line.back() == '\r') {
                block_line.pop_back();
            }
            block_lines.push_back(block_line);
        }
        
        // Reset global position for each block
        g_pos = 0;

        ParsedQuestion current_q;
        current_q.statement = parse_statement(block_lines);
        current_q.options = parse_options(block_lines);
        current_q.answers = parse_answer(block_content);
        current_q.timestamp = parse_timestamp(block_content);

        parsed_questions.push_back(current_q);
    }
    
    // Process the final block if it wasn't followed by the delimiter
    std::string final_block = content.substr(last);
    if (final_block.find_first_not_of(" \t\n\r") != std::string::npos) {
        std::stringstream ss(final_block);
        std::vector<std::string> block_lines;
        std::string block_line;
        while (std::getline(ss, block_line)) {
            if (!block_line.empty() && block_line.back() == '\r') {
                block_line.pop_back();
            }
            block_lines.push_back(block_line);
        }
        
        g_pos = 0;
        
        ParsedQuestion current_q;
        current_q.statement = parse_statement(block_lines);
        current_q.options = parse_options(block_lines);
        current_q.answers = parse_answer(final_block);
        current_q.timestamp = parse_timestamp(final_block);

        parsed_questions.push_back(current_q);
    }


    return parsed_questions;
}

/**
 * @brief Saves the parsed data to a file in a basic text format (not pickle).
 * @param data The vector of ParsedQuestion structs.
 * @param output_filename The name of the output text file.
 */
void save_to_text_file(const std::vector<ParsedQuestion>& data, const std::string& output_filename) {
    std::ofstream ofs(output_filename);
    if (!ofs.is_open()) {
        std::cerr << "Error: Could not open file '" << output_filename << "' for writing." << std::endl;
        return;
    }

    // Write the data in a simple, readable format
    for (size_t i = 0; i < data.size(); ++i) {
        ofs << "--- Question " << i + 1 << " ---\n";
        ofs << data[i].toString() << "\n";
    }

    std::cout << "Data successfully saved to '" << output_filename << "'" << std::endl;
}


// --- Main Execution ---
int main() {
    // 1. Define the input file path
    const std::string INPUT_FILE = "exams/pca.txt"; // Assumes you have this file structure
    
    // 2. Parse the file
    std::vector<ParsedQuestion> all_questions = parse_exam_questions(INPUT_FILE);

    // 3. Save the result
    if (!all_questions.empty()) {
        const std::string OUTPUT_FILE = "parsed_questions.txt"; // Changed from .pkl to .txt for simplicity
        save_to_text_file(all_questions, OUTPUT_FILE);

        // (Optional) Print the parsed data to verify
        std::cout << "\n--- Verification Printout ---\n";
        for (const auto& q : all_questions) {
            std::cout << q.toString() << "\n";
            std::cout << "----------------------------------------\n";
        }
    } else {
        std::cerr << "No questions were parsed. Nothing to save." << std::endl;
    }

    return 0;
}