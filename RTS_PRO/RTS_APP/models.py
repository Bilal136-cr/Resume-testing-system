from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('seeker', 'Job Seeker'),
        ('provider', 'Job Provider'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)  # ✅ Ensure uniqueness

    def __str__(self):
        return self.username


class Job(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs', limit_choices_to={'role': 'provider'})
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    postDate = models.DateTimeField(auto_now_add=True)
    seats = models.PositiveIntegerField(default=1)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Rejected', 'Rejected'),
    ('Job Closed', 'Job Closed'),
)    

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes', limit_choices_to={'role': 'seeker'})
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='resumes')
    resume = models.FileField(upload_to='resumes/')
    uploadDate = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.user.username}'s Resume"



class ScoringCriteria(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='scoring_criteria')
    keyword = models.CharField(max_length=50)
    weight = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.job.title} - {self.keyword} ({self.weight})"
    


class Score(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='scores')
    score = models.IntegerField()
    feedback = models.TextField(max_length=1000)

    def __str__(self):
        return f"Score: {self.score} for {self.resume}"
    

class ResumeHistory(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='history')
    viewed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_resumes')
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Viewed_by {self.viewed_by.username} on {self.viewed_at}"


