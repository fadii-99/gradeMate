import json
import random
import clang.cindex
from Levenshtein import distance as levenshtein_distance  # type: ignore

clang.cindex.Config.set_library_file("C:/Program Files/LLVM/bin/libclang.dll")

def levenshtein_similarity(expected, detected):
    """Calculate Levenshtein similarity (Balanced Buff: Min 20%, realistic scaling)."""
    if len(expected) == 0 or len(detected) == 0:
        return 0  # Avoid division by zero

    base_similarity = 1 - (levenshtein_distance(expected, detected) / max(len(expected), len(detected)))

    # Adjusted scaling: Increased lower bound & natural scaling
    return max(0, min(100, 30 + base_similarity * 80))  # Ranges from 20% to 100%

def parse_cpp_code_ast(code):
    """Parse C++ code into an AST representation using Clang."""
    index = clang.cindex.Index.create()
    tu = index.parse('tmp.cpp', args=['-std=c++17'], unsaved_files=[('tmp.cpp', code)], options=0)
    return ast_to_string(tu.cursor)

def ast_to_string(node, level=0):
    """Convert AST into a string representation."""
    result = []
    for child in node.get_children():
        result.append("  " * level + child.kind.name)
        result.extend(ast_to_string(child, level + 1))
    return "\n".join(result)

def evaluate_quiz(teacher_text, student_text):
    """Evaluate the similarity between teacher and student quizzes using AST & Levenshtein."""
    teacher_lines = teacher_text.split("\n")
    student_lines = student_text.split("\n")

    ast_scores = []
    text_scores = []

    for t_line, s_line in zip(teacher_lines, student_lines):
        if "{" in t_line or ";" in t_line:  # C++ code detected
            try:
                teacher_ast = parse_cpp_code_ast(t_line)
                student_ast = parse_cpp_code_ast(s_line)
                ast_scores.append(levenshtein_similarity(teacher_ast, student_ast))
            except Exception as e:
                print(f"AST Parsing Error: {e}")
                ast_scores.append(random.uniform(25, 30))  # Random value between 25% and 30%

                # ast_scores.append(30)  # Increased Minimum AST credit from 20 → 40%
        else:
            text_scores.append(levenshtein_similarity(t_line, s_line))

    avg_text_score = sum(text_scores) / len(text_scores) if text_scores else 0
    avg_ast_score = sum(ast_scores) / len(ast_scores) if ast_scores else 0

    return min(100, avg_text_score), min(100, avg_ast_score)  # Cap at 100%

def process_quiz(teacher_text, student_text, weights):
    """Process the given quiz texts and return evaluation results."""
    lev_score, ast_score = evaluate_quiz(teacher_text, student_text)

    logic_weight = weights.get("logic_weight", 0)
    levenshtein_weight = weights.get("levenshtein_weight", 0)

    # Cap scores before applying weightage
    lev_score = min(100, lev_score)
    ast_score = min(100, ast_score)

    final_score = ((lev_score * levenshtein_weight) + (ast_score * logic_weight)) / 100

    # Apply a slight boost to prevent scores from being too low
    if final_score < 50:
        final_score += 10  # Boost low scores slightly

    # Ensure final_score is capped at 100%
    final_score = min(100, final_score)

    grade = "A" if final_score >= 80 else "B" if final_score >= 70 else "C" if final_score >= 60 else "D"

    return {
        "levenshtein_score": round(lev_score, 2),
        "ast_score": round(ast_score, 2),
        "final_score": round(final_score, 2),
        "grade": grade
    }






# import json
# import random
# import clang.cindex
# from Levenshtein import distance as levenshtein_distance  # type: ignore

# clang.cindex.Config.set_library_file("C:/Program Files/LLVM/bin/libclang.dll")

# def levenshtein_similarity(expected, detected):
#     """Calculate Levenshtein similarity (Balanced Buff: Min 20%, realistic scaling)."""
#     if len(expected) == 0 or len(detected) == 0:
#         return 0  # Avoid division by zero

#     base_similarity = 1 - (levenshtein_distance(expected, detected) / max(len(expected), len(detected)))

#     # Adjusted scaling: Increased lower bound & natural scaling
#     return max(0, min(100, 30 + base_similarity * 80))  # Ranges from 20% to 100%

# def parse_cpp_code_ast(code):
#     """Parse C++ code into an AST representation using Clang."""
#     index = clang.cindex.Index.create()
#     tu = index.parse('tmp.cpp', args=['-std=c++17'], unsaved_files=[('tmp.cpp', code)], options=0)
#     return ast_to_string(tu.cursor)

# def ast_to_string(node, level=0):
#     """Convert AST into a string representation."""
#     result = []
#     for child in node.get_children():
#         result.append("  " * level + child.kind.name)
#         result.extend(ast_to_string(child, level + 1))
#     return "\n".join(result)

# def evaluate_quiz(teacher_text, student_text):
#     """Evaluate the similarity between teacher and student quizzes using AST & Levenshtein."""
#     teacher_lines = teacher_text.split("\n")
#     student_lines = student_text.split("\n")

#     ast_scores = []
#     text_scores = []

#     for t_line, s_line in zip(teacher_lines, student_lines):
#         if "{" in t_line or ";" in t_line:  # C++ code detected
#             try:
#                 teacher_ast = parse_cpp_code_ast(t_line)
#                 student_ast = parse_cpp_code_ast(s_line)
#                 ast_scores.append(levenshtein_similarity(teacher_ast, student_ast))
#             except Exception as e:
#                 print(f"AST Parsing Error: {e}")
#                 ast_scores.append(30)  # Increased Minimum AST credit from 20 → 40%
#         else:
#             text_scores.append(levenshtein_similarity(t_line, s_line))

#     avg_text_score = sum(text_scores) / len(text_scores) if text_scores else 0
#     avg_ast_score = sum(ast_scores) / len(ast_scores) if ast_scores else 0

#     return min(100, avg_text_score), min(100, avg_ast_score)  # Cap at 100%

# def process_quiz(teacher_text, student_text, weights):
#     """Process the given quiz texts and return evaluation results."""
#     lev_score, ast_score = evaluate_quiz(teacher_text, student_text)

#     logic_weight = weights.get("logic_weight", 0)
#     levenshtein_weight = weights.get("levenshtein_weight", 0)

#     # Cap scores before applying weightage
#     lev_score = min(100, lev_score)
#     ast_score = min(100, ast_score)

#     final_score = ((lev_score * levenshtein_weight) + (ast_score * logic_weight)) / 100

#     # Apply a slight boost to prevent scores from being too low
#     if final_score < 50:
#         final_score += 10  # Boost low scores slightly

#     # Ensure final_score is capped at 100%
#     final_score = min(100, final_score)

#     grade = "A" if final_score >= 80 else "B" if final_score >= 70 else "C" if final_score >= 60 else "D"

#     return {
#         "levenshtein_score": round(lev_score, 2),
#         "ast_score": round(ast_score, 2),
#         "final_score": round(final_score, 2),
#         "grade": grade
#     }














# original code
# import json
# import random
# import clang.cindex
# from Levenshtein import distance as levenshtein_distance  # type: ignore

# clang.cindex.Config.set_library_file("C:/Program Files/LLVM/bin/libclang.dll")

# def levenshtein_similarity(expected, detected):
#     """Calculate Levenshtein similarity between expected and detected text."""
#     return 1 - (levenshtein_distance(expected, detected) / max(len(expected), len(detected)))

# def parse_cpp_code_ast(code):
#     """Parse C++ code into an AST representation using Clang."""
#     index = clang.cindex.Index.create()
#     tu = index.parse('tmp.cpp', args=['-std=c++17'], unsaved_files=[('tmp.cpp', code)], options=0)
#     return ast_to_string(tu.cursor)

# def ast_to_string(node, level=0):
#     """Convert AST into a string representation."""
#     result = []
#     for child in node.get_children():
#         result.append("  " * level + child.kind.name)
#         result.extend(ast_to_string(child, level + 1))
#     return "\n".join(result)

# def evaluate_quiz(teacher_text, student_text):
#     """Evaluate the similarity between the teacher's and student's quizzes using AST & Levenshtein."""
#     teacher_lines = teacher_text.split("\n")
#     student_lines = student_text.split("\n")

#     ast_score = 0
#     text_score = 0

#     for t_line, s_line in zip(teacher_lines, student_lines):
#         if "{" in t_line or ";" in t_line:  # C++ code detected
#             try:
#                 teacher_ast = parse_cpp_code_ast(t_line)
#                 student_ast = parse_cpp_code_ast(s_line)
#                 ast_score += 100 if teacher_ast == student_ast else 0  # AST comparison
#             except Exception as e:
#                 print(f"AST Parsing Error: {e}")
#                 ast_score += 0
#         else:
#             text_score += levenshtein_similarity(t_line, s_line) * 100  

#     avg_text_score = text_score / max(len(teacher_lines), len(student_lines))
#     avg_ast_score = ast_score / max(len(teacher_lines), len(student_lines))

#     return avg_text_score, avg_ast_score  

# import random

# def calculate_grade():
#     """Define the grading rubric based on user input and assign a grade."""
#     print("\nDefine the grading rubric:")

#     try:
#         # Get input as integers directly (to avoid floating point nonsense)
#         logic_weight = int(input("Enter weightage for logic (AST) [%]: ").strip())
#         syntax_weight = int(input("Enter weightage for syntax [%]: ").strip())
#         levenshtein_weight = int(input("Enter weightage for text similarity [%]: ").strip())
#         other_weight = int(input("Enter weightage for other factors [%]: ").strip())
#     except ValueError:
#         print("❌ Invalid input! Please enter only whole numbers (e.g., 40, 30, 20, 10).")
#         return None  

#     # Compute total weight as an integer (no float nonsense)
#     total_weight = logic_weight + syntax_weight + levenshtein_weight + other_weight

#     # Check if total weight is exactly 100
#     if total_weight != 100:
#         print(f"❌ Error: Total weightage must be exactly 100%. You entered {total_weight}%. Adjust the values.")
#         return None  

#     final_score = round(random.uniform(60, 89), 2)  # Simulated grading
#     grade = "B" if final_score >= 75 else "C"

#     print(f"✅ Grade calculated successfully! Score: {final_score}, Grade: {grade}")
#     return final_score, grade



# def process_quiz(teacher_text, student_text):
#     """Process the given quiz texts and return evaluation results."""
#     lev_score, ast_score = evaluate_quiz(teacher_text, student_text)
#     grading_result = calculate_grade()

#     if grading_result is None:
#         return {"error": "Invalid grading weights. Please retry!"}

#     final_score, grade = grading_result

#     return {
#         "levenshtein_score": lev_score,
#         "ast_score": ast_score,
#         "final_score": final_score,
#         "grade": grade
#     }




# import json
# import random
# import clang.cindex
# from Levenshtein import distance as levenshtein_distance  # type: ignore

# clang.cindex.Config.set_library_file("C:/Program Files/LLVM/bin/libclang.dll")

# def levenshtein_similarity(expected, detected):
#     """Calculate Levenshtein similarity and highlight differences."""
#     min_len = min(len(expected), len(detected))
#     highlight = ""

#     for i in range(min_len):
#         if expected[i] == detected[i]:
#             highlight += f"\033[92m{expected[i]}\033[0m"  # Green for correct
#         else:
#             highlight += f"\033[91m{detected[i]}\033[0m"  # Red for incorrect

#     highlight += f"\033[91m{detected[min_len:]}\033[0m"  # Mark extra incorrect characters in red

#     return 1 - (levenshtein_distance(expected, detected) / max(len(expected), 1)), highlight

# def parse_cpp_code_ast(code):
#     """Parse C++ code into an AST representation using Clang."""
#     index = clang.cindex.Index.create()
#     tu = index.parse('tmp.cpp', args=['-std=c++17'], unsaved_files=[('tmp.cpp', code)], options=0)
#     return ast_to_string(tu.cursor)

# def ast_to_string(node, level=0):
#     """Convert AST into a string representation."""
#     result = []
#     for child in node.get_children():
#         result.append("  " * level + child.kind.name)
#         result.extend(ast_to_string(child, level + 1))
#     return "\n".join(result)

# def evaluate_quiz(teacher_text, student_text):
#     """Evaluate similarity between teacher and student quizzes using AST & Levenshtein."""
#     teacher_lines = teacher_text.split("\n")
#     student_lines = student_text.split("\n")

#     ast_score = 0
#     text_score = 0
#     lev_highlight = []
#     ast_highlight = []

#     for t_line, s_line in zip(teacher_lines, student_lines):
#         if "{" in t_line or ";" in t_line:  # C++ code detected
#             try:
#                 teacher_ast = parse_cpp_code_ast(t_line)
#                 student_ast = parse_cpp_code_ast(s_line)
#                 if teacher_ast == student_ast:
#                     ast_score += 100
#                     ast_highlight.append(f"\033[92m{s_line}\033[0m")  # Correct AST match
#                 else:
#                     ast_highlight.append(f"\033[91m{s_line}\033[0m")  # Incorrect AST
#             except Exception as e:
#                 print(f"AST Parsing Error: {e}")
#                 ast_score += 0
#                 ast_highlight.append(f"\033[91m{s_line}\033[0m")
#         else:
#             similarity, highlight = levenshtein_similarity(t_line, s_line)
#             text_score += similarity * 100
#             lev_highlight.append(highlight)

#     avg_text_score = text_score / max(len(teacher_lines), len(student_lines))
#     avg_ast_score = ast_score / max(len(teacher_lines), len(student_lines))

#     return avg_text_score, avg_ast_score, lev_highlight, ast_highlight

# def calculate_grade():
#     """Define the grading rubric based on user input and assign a grade."""
#     print("\nDefine the grading rubric:")

#     try:
#         # Get input as integers directly (to avoid floating point issues)
#         logic_weight = int(input("Enter weightage for logic (AST) [%]: ").strip())
#         syntax_weight = int(input("Enter weightage for syntax [%]: ").strip())
#         levenshtein_weight = int(input("Enter weightage for text similarity [%]: ").strip())
#         other_weight = int(input("Enter weightage for other factors [%]: ").strip())
#     except ValueError:
#         print("❌ Invalid input! Please enter only whole numbers (e.g., 40, 30, 20, 10).")
#         return None  

#     # Compute total weight as an integer (no float issues)
#     total_weight = logic_weight + syntax_weight + levenshtein_weight + other_weight

#     # Check if total weight is exactly 100
#     if total_weight != 100:
#         print(f"❌ Error: Total weightage must be exactly 100%. You entered {total_weight}%. Adjust the values.")
#         return None  

#     final_score = round(random.uniform(60, 89), 2)  # Simulated grading
#     grade = "B" if final_score >= 75 else "C"

#     print(f"✅ Grade calculated successfully! Score: {final_score}, Grade: {grade}")
#     return final_score, grade

# def process_quiz(teacher_text, student_text):
#     """Process the given quiz texts and return evaluation results."""
#     lev_score, ast_score, lev_highlight, ast_highlight = evaluate_quiz(teacher_text, student_text)
#     grading_result = calculate_grade()

#     if grading_result is None:
#         return {"error": "Invalid grading weights. Please retry!"}

#     final_score, grade = grading_result

#     return {
#         "levenshtein_score": lev_score,
#         "ast_score": ast_score,
#         "final_score": final_score,
#         "grade": grade,
#         "lev_highlight": lev_highlight,
#         "ast_highlight": ast_highlight
#     }