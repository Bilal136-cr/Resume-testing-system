from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Resume, Score, Job, ScoringCriteria,User
from django.db import transaction
from .ai.scorer import score_resume  # AI scoring logic
# from .utils import extract_text_from_file  # assuming you move the function there
from django.conf import settings
import requests,json,openai,re,cohere,fitz
from openai import OpenAIError
from cohere import Client
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from reportlab.pdfgen import canvas
import docx


# def extract_skills(file):

#     headers = {
#         'Authorization': f'Bearer {settings.AFFINDA_API_KEY}'
#     }

#     files = {
#         'file': file
#     }
#     response = requests.post(
#         'https://api.affinda.com/v2/resumes',
#         headers=headers,
#         files=files
#     )

#     print("Status Code:", response.status_code)
#     print("Response:", response.text)

#     if response.status_code != 201:
#         return None

#     data = response.json()
#     return data.get('data', {}).get("rawText","")


def extract_resume_text(file):
    ext = file.name.split('.')[-1].lower()

    try:
        if ext == 'pdf':
            doc = fitz.open(stream=file.read(), filetype='pdf')
            text = ""
            for page in doc:
                text += page.get_text()
            return text.strip()

        elif ext == 'docx':
            text = ""
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text.strip()

        else:
            return None  # Unsupported format

    except Exception as e:
        print("Error parsing file:", str(e))
        return None

co = cohere.Client(settings.OPENAI_API_KEY)

def analyze_resume_with_openai(resume_text,scoring_criteria):
    try:
        
        criteria_str = "\n".join([f"- {k}: {v}%" for k, v in scoring_criteria.items()])
        prompt = f"""
        You are a resume evaluator. Carefully review the following resume content.

        1. Score the resume out of 100 based on skills, clarity, formatting, and relevance.
        2. Give suggestions for improvement.
        3. Mention any strengths you notice.

        Resume:
        {resume_text}
        ### Scoring Criteria (Skills & Weights):
        {criteria_str}
        
        ### Your Response Format:
        Score: <numeric_score_out_of_100>
        Highlights:
        - ...
        Improvements:
        - ...
        Formatting Tips:
        - ...
        """
        response = co.generate(
            model="command",  # "gpt-4o-mini" or "gpt-4" / "gpt-3.5-turbo" depending on your access
            prompt=prompt,
            # messages=[
            #     {"role": "system", "content": "You are a helpful assistant that evaluates resumes."},
            #     {"role": "user", "content": prompt}
            # ],
            # temperature=0.5,
            max_tokens=400,
        )

        # Extract the assistant's reply text
        result_text = response.generations[0].text.strip()  

        return result_text

    except OpenAIError as e:
        # Handle API errors gracefully
        return f"OpenAI API error: {str(e)}"


@login_required

def upload_resume(request, job):
    job_obj = Job.objects.get(id=job) 

    if job_obj.is_closed:
        return HttpResponse("This job is closed.")
    
    # Delete previous resume if exists
    existing_resume = Resume.objects.filter(user=request.user, job=job_obj).first()
    if existing_resume:
        existing_resume.delete()

    if request.method == 'POST' and request.FILES.get('resume'):
        with transaction.atomic():
            uploaded_file = request.FILES['resume']

            if not allowed_file(uploaded_file.name):
                return HttpResponse('Invalid file type. Please upload a PDF or DOCX file.', status=400)

            
        # 1. Save resume in Resume model
        resume = Resume(user=request.user, job=job_obj, resume=uploaded_file, status='Pending')
        resume.save()
        
        # 2. Send file to Affinda for parsing
        # resume_text = extract_skills(uploaded_file)
        resume_text = extract_resume_text(uploaded_file)
        if not resume_text:
            return HttpResponse("Failed to extract text from resume. Please try again or upload a different file.", status=400)
        
        # Prepare scoring criteria dictionary
        criteria = {crit.keyword.lower(): crit.weight for crit in ScoringCriteria.objects.all()}
        # 3. Generate feedback from OpenAI
        analysis_result = analyze_resume_with_openai(resume_text, criteria)
        
        # 4. Calculate score from keywords in ScoringCriteria
        score = 0
        feedback_lines = []

        # for keyword, weight in rules.items():
        #     if re.search(r'\b' + re.escape(keyword) + r'\b', resume_text.lower()):
        #         score += weight
        #         feedback_lines.append(f"✔ {keyword.capitalize()} matched (+{weight}%)")
        #     else:
        #         feedback_lines.append(f"✘ {keyword.capitalize()} missing")

        # score = min(score, 100)
        # full_feedback = "\n".join(feedback_lines) + "\n\n---\n\n" + analysis_result
        # 🔍 Extract score from OpenAI response using regex
        score_match = re.search(r"Score:\s*(\d{1,3})", analysis_result)
        score = int(score_match.group(1)) if score_match else 0 
        
        # 5. Save to Score model
        Score.objects.create(resume=resume, score=score, feedback=analysis_result)

        return redirect('view_my_resumes')

    # ✅ Fixed: pass actual Job object for GET request
    return render(request, 'upload_resume.html', {'job': job_obj})

ALLOWED_EXTENSIONS = ['pdf', 'docx']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




def members(request):
    return render(request, 'home.html', {'show_header': True})




def logIn_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if not username or not password:
            return render(request, 'logIn.html', {'error': 'Both fields are required'})

        if user is not None:
            login(request, user)
            print("User Role:", user.role)  # For debugging

            if user.role == 'Job Seeker':
                return redirect('dashboard_jobseeker')
            elif user.role == 'Job Provider':
                return redirect('dashboard_jobprovider')
            else:
                messages.error(request, "Unknown user role.")
        else:
            messages.error(request, "Invalid credentials")
            return redirect('logIn')
    return render(request, 'logIn.html')



def signUp_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        if not username or not email or not password or not password2 or not role:
            return render(request, 'signUp.html', {'error': 'All fields are required'})
        
         # ✅ Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use. Please use a different one.")
            return redirect('signup')
        
        # ✅ Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already in use. Please use a different one.")
            return redirect('signup')

        if password == password2:
            user = User.objects.create_user(username=username, email=email, password=password, role=role)
            login(request, user)

            if role == 'Job Seeker':
                return redirect('dashboard_jobseeker')
            elif role == 'Job Provider':
                return redirect('dashboard_jobprovider')
        
        else:
            return render(request, 'signUp.html', {'error': 'Passwords do not match'})
    return render(request, 'signUp.html')


@login_required
def dashboard_jobseeker(request):
    if request.user.role != 'Job Seeker':
        return HttpResponse("Unauthorized", status=403)

    jobs = Job.objects.filter(is_closed=False)
    return render(request, 'dashboard_jobseeker.html', {'jobs': jobs, 'show_header': True})


@login_required
def dashboard_jobprovider(request):
    jobs = Job.objects.filter(provider=request.user).order_by('-postDate')
    return render(request, 'dashboard_jobprovider.html', {'jobs': jobs, 'show_header': True})


def upload_job(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        seats = request.POST.get('seats')
        description = request.POST.get('description')
        keywords = request.POST.getlist('keyword[]')
        weights = request.POST.getlist('weight[]')

        if not title or not seats or not description:
            messages.error(request, "All fields are required.")
            return render(request, 'upload_job.html')

        # Ensure seats is a valid number
        try:
            seats = int(seats)
            if seats < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "Number of seats must be a positive integer.")
            return render(request, 'upload_job.html')

        # Save the job
        job=Job.objects.create(
            provider=request.user,
            title=title,
            description=description,
            seats=seats
        )

        # Save ScoringCriteria
        for keyword, weight in zip(keywords, weights):
            if keyword.strip() and weight.isdigit():
                ScoringCriteria.objects.create(
                    job=job,
                    keyword=keyword.strip(),
                    weight=int(weight)
                )

        messages.success(request, "Job created successfully!")
        return redirect('dashboard_jobprovider')  # Or redirect to dashboard, e.g., 'dashboard_jobprovider'

    return render(request, 'upload_job.html')

@login_required
def view_score(request):
    try:
        resume = Resume.objects.filter(user=request.user).latest('uploadDate')
        score = Score.objects.get(resume=resume)
    except (Resume.DoesNotExist, Score.DoesNotExist):
        resume = None
        score = None

    return render(request, 'view_score.html', {'resume': resume, 'score': score})


@login_required
def view_feedback(request, resume):
    try:
        resume = Resume.objects.get(id=resume)
        score = Score.objects.get(resume=resume)
    except Resume.DoesNotExist:
        return HttpResponse("Resume not found", status=404)
    except Score.DoesNotExist:
        return HttpResponse("Score not found", status=404)

    # Only allow access to the user who uploaded it or the job provider who posted the job
    if request.user != resume.user and request.user != resume.job.provider:
        return HttpResponse("Unauthorized", status=403)

    context = {
        'resume': resume,
        'score': score,
        'is_job_provider': request.user.role == 'Job Provider'
    }
    return render(request, 'feedback.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('logIn')


@login_required
def view_resumes_for_job(request, job):
    job_obj = Job.objects.get(id=job, provider=request.user)
    resumes = Resume.objects.filter(job=job_obj)

    return render(request, 'job_resumes.html', {'job': job_obj, 'resumes': resumes})



@require_POST
@login_required
def update_resume_status(request, resume):
    resume_obj = Resume.objects.get(id=resume)
    job = resume_obj.job

    if request.user != job.provider:
        return HttpResponse("Unauthorized", status=403)
    status = request.POST.get('status')

    if status == 'Accepted' and resume_obj.status != 'Accepted':

        if job.seats > 0:
            resume_obj.status = 'Accepted'
            resume_obj.save()

            job.seats -= 1

            if job.seats == 0:
                job.is_closed = True
            job.save()

        else:
            return HttpResponse("No more seats available.")
        
    elif status == 'Rejected':
        resume_obj.status = 'Rejected'
        resume_obj.save()
    return redirect('view_resumes_for_job', job=job.id)


@login_required
def close_job(request, job):
    job = Job.objects.get(id=job, provider=request.user)
    job.is_closed = True
    job.save()
    # Update all related resumes if they are still 'Pending'
    Resume.objects.filter(job=job, status='Pending').update(status='Job Closed')
    return redirect('dashboard_jobprovider')



@login_required
def view_top_resumes(request, job):

    job = Job.objects.get(id=job)

    if request.user != job.provider:
        return HttpResponse("Unauthorized", status=403)

    # Only resumes for this job with Pending status
    resumes = Resume.objects.filter(job=job, status='Pending')
    
    # Get scores for each resume and sort by score (highest first)
    scored_resumes = []
    for resume in resumes:
        try:
            score_obj = Score.objects.get(resume=resume)
            scored_resumes.append({
                'resume': resume,
                'id': resume.id,
                'score': score_obj.score,
            })
        except Score.DoesNotExist:
            continue

    # Sort by score descending
    scored_resumes.sort(key=lambda x: x['score'], reverse=True)

    # Limit to top N resumes based on job.seats
    top_resumes = scored_resumes[:job.seats]

    return render(request, 'top_resumes.html', {
        'job': job,
        'top_resumes': top_resumes
    })


@login_required
def edit_job(request, job):
    job = Job.objects.get(id=job)

    if request.user != job.provider:
        return HttpResponse("Unauthorized", status=403)

    if request.method == 'POST':
        job.description = request.POST.get('description')
        job.seats = int(request.POST.get('seats'))
        job.is_closed = False
        job.save()
        messages.success(request, "Job updated successfully.")
        return redirect('dashboard_jobprovider')

    return render(request, 'edit_job.html', {'job': job, 'show_header': True})


@login_required
def view_uploaded_resumes(request):
    if request.user.role != 'Job Seeker':
        return HttpResponse("Unauthorized", status=403)

    resumes = Resume.objects.filter(user=request.user).select_related('job')
    return render(request, 'view_uploaded_resumes.html', {'resumes': resumes})



@require_POST
@login_required
def delete_resume(request, resume):
    try:
        resume = Resume.objects.get(id=resume, user=request.user)
        resume.delete()
        return redirect('view_my_resumes')
    except Resume.DoesNotExist:
        return HttpResponse("Resume not found or unauthorized", status=404)


@login_required
def download_feedback_pdf(request, resume):
    try:
        resume = Resume.objects.get(id=resume)
        score = Score.objects.get(resume=resume)
    except:
        return HttpResponse("Not Found", status=404)

    # Permissions
    if request.user != resume.user and request.user != resume.job.user and not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="feedback_{resume.id}.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Feedback for Resume ID: {resume.id}")
    p.drawString(100, 780, f"Job: {resume.job.title}")
    p.drawString(100, 760, f"Uploaded By: {resume.user.username}")
    p.drawString(100, 740, f"Score: {score.score}")
    p.drawString(100, 720, "Feedback:{score.feedback}")
    text = p.beginText(100, 700)
    for line in score.feedback.splitlines():
        text.textLine(line)
    p.drawText(text)
    p.showPage()
    p.save()

    return response

