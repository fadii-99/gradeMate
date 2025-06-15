import json
import uuid
from accounts.models import User
from .models import  Quiz, StudentSubmission, PlagiarismResult, QuizSolution
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from accounts.auth_utils import generate_jwt_token, decode_jwt_token
from django.db.models import Avg, Count
from datetime import datetime
from utils.decorators import jwt_required

from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import api_view, parser_classes
from django.core.files.storage import default_storage
from django.db.models import Avg, Max, Min

from quize.ocr import extract_text, correct_cpp_code
import random
from quize.AST_Levenshtein import evaluate_quiz 
from rapidfuzz import fuzz
import tempfile


@api_view(['POST'])
@jwt_required
def dashboard(request):
    try:
        user_id = request.user_payload.get("user_id")
        user = User.objects.get(id=user_id)

        # Get all quizzes by this user
        quizzes = Quiz.objects.filter(created_by=user)

        total_quizzes = quizzes.count()

        # Get recent 3 quizzes
        recent_quizzes = quizzes.order_by('-created_at')

        recent_data = []
        for quiz in recent_quizzes:
            recent_data.append({
                "id": quiz.id,
                "name": quiz.name,
                "date": quiz.created_at.strftime("%Y-%m-%d"),
                "student_count": quiz.submissions.count(),
                "actions": {
                    "view_url": f"/quiz/{quiz.id}/view",
                    "grade_url": f"/quiz/{quiz.id}/grade",
                    "delete_url": f"/quiz/{quiz.id}/delete"
                }
            })

        return JsonResponse({
            "total_quizzes": total_quizzes,
            "recent_quizzes": recent_data
        }, status=200)

    except Exception as e:
        print("Dashboard Error:", str(e))
        return JsonResponse({"error": str(e)}, status=500)








@api_view(['POST'])
@jwt_required
def upload_quiz(request):
    try:
        print("Request Data:", request.data)
        user_id = request.user_payload.get("user_id")
        user = User.objects.get(id=user_id)

        # Extract form fields
        quiz_name = request.data.get("quizName")
        logic_weight = float(request.data.get("logicWeight", 0.5))
        total_marks = float(request.data.get("total"))
        similarity_threshold = float(request.data.get("similarityThreshold", 0.7))
        solution_image = request.FILES.get("solutionImage")

        total_weight = logic_weight + similarity_threshold 




        # OCR processing for the solution image
        extracted_solution_text = extract_text(solution_image)
        corrected_solution_text = correct_cpp_code(extracted_solution_text)

        # Create Quiz
        quiz = Quiz.objects.create(
            name=quiz_name,
            created_by=user,
            logic_weight=logic_weight,
            similarity_threshold=similarity_threshold
        )

        # Save QuizSolution and get the saved instance to build URL later
        quiz_solution = None
        if solution_image:
            quiz_solution = QuizSolution.objects.create(
                quiz=quiz,
                solution_image=solution_image,
                extracted_solution_text=corrected_solution_text
            )
        solution_image_url = (
            request.build_absolute_uri(quiz_solution.solution_image.url)
            if quiz_solution and solution_image else None
        )
        
        # Handle student submissions from lists of names and images
        student_names = request.data.getlist("studentNames")
        student_images = request.FILES.getlist("studentImages")
        saved_submissions = []   # List to store created StudentSubmission instances

        for i in range(len(student_names)):
            name = student_names[i]
            image = student_images[i] if i < len(student_images) else None

            # Extract and correct text from each student image using OCR
            extracted_text = extract_text(image)
            corrected_text = correct_cpp_code(extracted_text)

            if image:
                submission = StudentSubmission.objects.create(
                    quiz=quiz,
                    student=name,
                    submission_image=image,
                    extracted_text=corrected_text
                )
                saved_submissions.append(submission)

        # Prepare the mock grading results:
        total_students = len(saved_submissions)
        averageScore = 82.5  # Fixed average score for mock grading
        
        lev_score, ast_score = evaluate_quiz(corrected_solution_text, corrected_text)  
        # lev_score, ast_score = 11, 22

        final_score = ((lev_score * (similarity_threshold + 10)) + 
                   (ast_score * (logic_weight + 10))) / 100    
          
        obtained_marks = round((final_score / 100) * total_marks)
        grade = "A" if final_score >= 80 else "B" if final_score >= 70 else "C" if final_score >= 60 else "D"

        # Prepare student grading results using saved submissions
        students_results = []
        for submission in saved_submissions:
            student_result = {
                "id": submission.id,
                "name": submission.student,
                "image": request.build_absolute_uri(submission.submission_image.url) if submission.submission_image else None,
                "levenshtein_score": lev_score,  
                "extractedText": submission.extracted_text,
                'obtained_marks':obtained_marks,
                'final_score':final_score,
                'grade':grade,
                'ast_score':ast_score,
                'total_marks':total_marks,
            }
            students_results.append(student_result)

        # Return the final JSON response
        return JsonResponse({
            "quizName": quiz.name,
            "totalStudents": total_students,
            "averageScore": averageScore,
            "solutionImage": solution_image_url,
            "solutionImageText": corrected_solution_text,  # Or use your OCR result if needed
            "students": students_results
        }, status=201)

    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({"error": str(e)}, status=500)
    



    
@api_view(['POST'])
@jwt_required
def quiz_view(request):
    try:
        user_id = request.user_payload.get("user_id")
        user = User.objects.get(id=user_id)
        quiz_id = request.data.get("quiz_id")

        # Fetch quiz, ensure it's created by current user
        quiz = Quiz.objects.get(id=quiz_id, created_by=user)

        # Solution image (optional, if you still want to include)
        try:
            solution = QuizSolution.objects.get(quiz=quiz)
            solution_url = request.build_absolute_uri(solution.solution_image.url)
        except QuizSolution.DoesNotExist:
            solution_url = None

        submissions_qs = quiz.submissions.all()
        total_students = submissions_qs.count()

        graded_subs = submissions_qs.filter(graded=True, score__isnull=False)

        # Stats
        avg_score = graded_subs.aggregate(avg=Avg('score'))['avg'] or 0
        max_score = graded_subs.aggregate(max=Max('score'))['max'] or 0
        min_score = graded_subs.aggregate(min=Min('score'))['min'] or 0
        passing_count = graded_subs.filter(score__gte=50).count()  # assuming 50 is passing
        passing_rate = f"{round((passing_count / total_students) * 100)}%" if total_students else "0%"

        # Prepare student details
        students_data = []
        for i, sub in enumerate(submissions_qs):
            students_data.append({
                "id": i + 1,
                "name": sub.student,
                "grade": sub.score if sub.graded else None,
                "status": "Passed" if sub.graded and sub.score >= 50 else "Failed" if sub.graded else "Not graded",
                "submissionDate": sub.created_at.strftime("%b %d, %Y"),
                "feedback": "Excellent work" if sub.graded and sub.score >= 90 else
                            "Good effort" if sub.graded and sub.score >= 75 else
                            "Needs improvement" if sub.graded else "Not yet graded"
            })

        return JsonResponse({
            "id": quiz.id,
            "name": quiz.name,
            "date": quiz.created_at.strftime("%b %d, %Y"),
            "totalStudents": total_students,
            "avgScore": round(avg_score, 2),
            "highestScore": max_score,
            "lowestScore": min_score,
            "passingRate": passing_rate,
            "students": students_data,
            "solutionImage": solution_url  # Optional
        }, status=200)

    except Quiz.DoesNotExist:
        return JsonResponse({"error": "Quiz not found."}, status=404)
    except Exception as e:
        print("Quiz View Error:", str(e))
        return JsonResponse({"error": str(e)}, status=500)




@api_view(['POST'])
@jwt_required
def get_all_quizes(request):
    try:
        user_id = request.user_payload.get("user_id")
        user = User.objects.get(id=user_id)
        quizzes = Quiz.objects.filter(created_by=user).order_by('-created_at')

        data = []
        for quiz in quizzes:
            data.append({
                "id": quiz.id,
                "name": quiz.name,
                "date": quiz.created_at.strftime("%b %d, %Y"),
                "student_count": quiz.submissions.count()
            })

        return JsonResponse({"quizes": data}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




@api_view(['POST'])
@jwt_required
def check_plagiarism(request):
    try:
        print("Request Data:", request.data)
        quiz_id = request.data.get("quizId")
        if not quiz_id:
            return JsonResponse({"error": "Quiz ID is required"}, status=400)

        quiz = Quiz.objects.get(id=quiz_id)
        submissions = StudentSubmission.objects.filter(quiz=quiz)
        if not submissions:
            return JsonResponse({"error": "No submissions found for this quiz."}, status=404)

        threshold = 80.0


        plagiarism_results = []

        # Compare every unique pair of submissions.
        for i in range(len(submissions)):
            for j in range(i + 1, len(submissions)):
                sub1 = submissions[i]
                sub2 = submissions[j]
                print(f"Comparing {sub1.student} with {sub2.student}")
                sim_score = fuzz.token_sort_ratio(sub1.extracted_text, sub2.extracted_text)
                print(round(sim_score, 2))

                # Build the result in a structure similar to your mock data.
                result = {
                    "student1": sub1.student,  # In this demo, student is a name string.
                    "student2": sub2.student,
                    "similarity": round(sim_score, 2) / 100,
                    "flag": sim_score >= threshold,
                    "matches": []  # Optionally, you might add details such as common words.
                }
                plagiarism_results.append(result)

        # Optionally, if you want to store results in the PlagiarismResult model, you would need to map
        # the student names from submissions to actual User objects. That step is skipped here since the submissions
        # are stored as simple strings and may not directly reference a User.

        return JsonResponse({
            "quiz_id": quiz.id,
            "quiz_name": quiz.name,
            "plagiarism_results": plagiarism_results
        }, status=200)
    except Quiz.DoesNotExist:
        return JsonResponse({"error": "Quiz not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

