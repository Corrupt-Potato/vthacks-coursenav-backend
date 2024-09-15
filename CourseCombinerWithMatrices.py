import os
import json
import re
from itertools import product

# Helper function to load a JSON file based on course code
def load_course_data(course_code):
    department = course_code.split()[0].replace("(", "").replace(")", "")  # Clean parentheses if present
    file_name = f"{department}_courses.json"
    file_path = os.path.join("VTCourses", file_name)

    if not os.path.exists(file_path):
        print(f"File for department {department} does not exist: {file_path}")
        return None
    
    with open(file_path, 'r') as file:
        courses = json.load(file)
        for course in courses:
            if course['course_code'].strip() == course_code.strip():
                return course
    return None

# Function to parse prerequisite strings
def parse_course_string(course_str):
    course_str = course_str.strip()

    # Split at the top level based on "or"
    or_parts = [part.strip() for part in re.split(r'\s+or\s+(?=\()', course_str) if part]

    parsed_courses = []
    for or_part in or_parts:
        # Remove any surrounding parentheses
        if or_part.startswith('(') and or_part.endswith(')'):
            or_part = or_part[1:-1]

        # Split the "or_part" further by "and"
        and_parts = [part.strip() for part in re.split(r'\s+and\s+', or_part)]

        sublist = []
        for and_part in and_parts:
            # If the part contains "or", split it further
            if 'or' in and_part:
                or_options = [p.strip() for p in re.split(r'\s+or\s+', and_part)]
                sublist.append(or_options)
            else:
                sublist.append([and_part])

        parsed_courses.append(sublist)

    return parsed_courses

# Function to generate paths from parsed prerequisite structure
def generate_paths(course_structure):
    all_paths = []
    for group in course_structure:
        group_combinations = list(product(*group))
        all_paths.extend(group_combinations)
    
    return all_paths

# Function to clean course codes (remove parentheses)
def clean_course_string(course_str):
    return course_str.replace("(", "").replace(")", "").strip()

# Main function to convert prerequisites to paths
def convert_prereqs_to_paths(course_str):
    parsed_structure = parse_course_string(course_str)
    all_paths = generate_paths(parsed_structure)
    
    # Clean up each course code in the paths
    cleaned_paths = [[clean_course_string(course) for course in path] for path in all_paths]
    
    return cleaned_paths

# Function to flatten any nested lists
def flatten(lst):
    flat_list = []
    for item in lst:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list

# Function to format paths into a matrix
def format_as_matrix(paths):
    matrix = []
    for path in paths:
        # Only include paths with classes (no padding with empty strings)
        padded_path = list(path)
        matrix.append(padded_path)
    return matrix

# Function to print the matrix in a readable format
def print_matrix(matrix):
    for row in matrix:
        print("\t".join(row))

# Function to get prerequisites for a given course code and return the matrix
def get_prerequisite_matrix(course_code):
    course_data = load_course_data(course_code)
    if not course_data:
        return None

    prereqs = course_data.get('prerequisites', None)
    if not prereqs or prereqs.lower() == "not found":
        return {"course_code": course_code, "prerequisite_matrix": []}

    resolved_paths = convert_prereqs_to_paths(prereqs)
    matrix = format_as_matrix(resolved_paths)
    
    return {
        "course_code": course_code,
        "prerequisite_matrix": matrix
    }

# Function to process all JSON files and save results
def process_all_courses():
    folder_path = "VTCourses"
    courses = []

    # Loop through each file in the directory
    for file_name in os.listdir(folder_path):
        if file_name.endswith('_courses.json'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                course_data = json.load(file)
                for course in course_data:
                    course_code = course.get('course_code')
                    course_name = course.get('course_title', 'Unknown Name')  # Adjust based on actual field name for course name
                    if course_code:
                        prereq_matrix = get_prerequisite_matrix(course_code)
                        if prereq_matrix:
                            courses.append({
                                "id": course_code,
                                "name": course_name,  # Use the actual course name from JSON
                                "prereq": prereq_matrix.get('prerequisite_matrix', [])
                            })
    
    result = {"courses": courses}
    
    # Save the result to a new JSON file
    with open("prerequisite_matrices.json", 'w') as outfile:
        json.dump(result, outfile, indent=4)

    print("All courses processed and results saved to 'prerequisite_matrices.json'.")

# Run the process
process_all_courses()
