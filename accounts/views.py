import json
import uuid
from .models import User
from django.conf import settings
from rest_framework import status
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .auth_utils import generate_jwt_token, decode_jwt_token
from django.contrib.auth.hashers import make_password, check_password
from utils.emails import send_verification_email, send_reset_password_email
 





 
@api_view(['POST'])
def signup(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        

        print(data)
        # Validate required fields
        if not email or not password or not name:
            return JsonResponse({"error": "Missing required fields."}, status=400)
        
        # Check for duplicates
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists."}, status=400)

        base_username = ''.join(name.lower().split())
        # Use first 4 characters of UUID4 for brevity
        unique_suffix = str(uuid.uuid4())[:4]
        username = f"{base_username}{unique_suffix}"
        
        hashed_password = make_password(password)
        user = User.objects.create(
            email=email,
            password=hashed_password,
            name=name,
            active_status=False,
            email_verified=True
        )
        
        # Send verification email
        # send_verification_email(username, email, generate_jwt_token(user))
        return JsonResponse({"message": "Varification Link is sent, Please verify your email."}, status=201)
    
    except Exception as e:
        print(str(e))
        return JsonResponse({"error": str(e)}, status=500)



@api_view(['POST'])
def login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid HTTP method."}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return JsonResponse({"error": "Email and password required."}, status=400)
        
        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"error": "Invalid credentials."}, status=401)
        
        if not check_password(password, user.password):
            return JsonResponse({"error": "Invalid credentials."}, status=401)
        

        userData = {
            "id": user.id,
            "email": user.email,
            "createdAt": user.created_at.strftime("%-d %b %Y"),
        }

        token = generate_jwt_token(user)
        
        return JsonResponse({"token": token, 'user': userData}, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@api_view(['POST'])
def search_email(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid HTTP method."}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get("email")
        if not email:
            return JsonResponse({"error": "Email is required."}, status=400)
        
        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"error": "User not found."}, status=404)
        print('sending email')
        send_reset_password_email(user.name, user.email, generate_jwt_token(user))
        print('sent email')
        return JsonResponse({"message": "Reset password email sent."})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
def set_new_password(request):
    """
    API endpoint to set a new password.
    Expects POST JSON with token (from password reset email) and new_password.
    """
    
    try:
        token = request.data.get('token')
        try:
            decodedToken = decode_jwt_token(token)
            user_id = decodedToken['user_id']
        except:
            return JsonResponse({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_password = request.data.get("password")
        if not new_password:
            return JsonResponse({"error": "New_password are required."}, status=400)
        
        
        user.password = make_password(new_password)
        user.save(update_fields=["password"])
        return JsonResponse({"message": "Password updated successfully."})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)



