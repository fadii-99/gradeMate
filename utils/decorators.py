from functools import wraps
from django.http import JsonResponse
from accounts.auth_utils import decode_jwt_token  # using our custom token decoding function

def jwt_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"error": "Authorization header missing"}, status=401)
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JsonResponse({"error": "Invalid Authorization header format. Expected 'Bearer <token>'."}, status=401)
        
        token = parts[1]
        try:
            payload = decode_jwt_token(token)
            # Attach payload to request so that the view can access it
            request.user_payload = payload
             
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=401)
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view
