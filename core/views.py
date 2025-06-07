from .view_imports import *

# Create your views here.
def home(request):
    return render(request, 'home.html')


def about(request):
    context = {'page' : 'about'} 
    return render(request, "about.html", context)

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        # Save to database
        Contact.objects.create(name=name, email=email, phone=phone, message=message)
        
        errors = []
        if not name:
            errors.append("Name is required.")
        if not email:
            errors.append("Email is required.")
        elif "@" not in email:  # Very basic email check
            errors.append("Enter a valid email address.")
        if not message:
            errors.append("Message is required.")


        if not name or not email or not message:
            messages.error(request, "All fields are required.")
            return redirect('contact_view')
        
        # Send email to owner
        subject = f"New Contact Form Submission from {name}"
        full_message = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage:\n{message}"
        send_mail(
            subject,
            full_message,
            email,  # from email (sender)
            [settings.CONTACT_FORM_RECIPIENT],  # recipient list
            fail_silently=False,
        )

        messages.success(request, "Thank you for contacting us!")
        return redirect('contact_view')

    return render(request, "contact.html", {'page' : 'contact'})

logger = logging.getLogger(__name__)

