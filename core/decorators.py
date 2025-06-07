from django.contrib.auth.decorators import login_required
from functools import wraps
from django.http import HttpResponseForbidden

def login_role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            # Check if the user has the required role
            if (required_role == "customer" and not getattr(user, "is_customer", False)) or \
               (required_role == "seller" and not getattr(user, "is_seller", False)):
                # Return a custom 403 Forbidden response with HTML and CSS
                return HttpResponseForbidden("""
                    <html>
                    <head>
                        <title>Access Denied</title>
                        <style>
                            body { 
                                display: flex; 
                                justify-content: center; 
                                align-items: center; 
                                height: 100vh; 
                                margin: 0; 
                                font-family: 'Arial', sans-serif; 
                                background-color: #f4f4f4; 
                                color: #333; 
                            }
                            .error-container {
                                text-align: center;
                                background: white;
                                padding: 20px 50px;
                                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                                border-radius: 8px;
                            }
                            h1 {
                                color: #de4759;
                            }
                            p {
                                color: #555;
                            }
                            .button {
                                display: inline-block;
                                margin-top: 20px;
                                padding: 10px 20px;
                                color: #fff;
                                background-color: #007bff;
                                text-decoration: none;
                                border-radius: 5px;
                                font-weight: bold;
                            }
                            .button:hover {
                                background-color: #0056b3;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="error-container">
                            <h1>403 Forbidden</h1>
                            <p>You are not authorized to access this page.</p>
                            <a href="/" class="button">Back to Home</a>
                        </div>
                    </body>
                    </html>
                """, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator