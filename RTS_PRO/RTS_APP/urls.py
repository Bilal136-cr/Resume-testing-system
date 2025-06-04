from django.urls import path 
from . import views 
from django.contrib.auth import views as auth_views

urlpatterns = [ 
    path('', views.members, name='members'), 
    path('logIn/', views.logIn_view, name='logIn'),
    path('signUp/', views.signUp_view, name='signUp'),
    path('dashboard-jobseeker/', views.dashboard_jobseeker, name='dashboard_jobseeker'),
    path('dashboard-jobprovider/', views.dashboard_jobprovider, name='dashboard_jobprovider'),
    
    # Job posting and editing
    path('upload-job/', views.upload_job, name='upload_job'),
    path('job/<int:job>/edit/', views.edit_job, name='edit_job'),
    path('job/<int:job>/close/', views.close_job, name='close_job'),
    
    # Resume actions
    path('upload-resume/<int:job>/', views.upload_resume, name='upload_resume'),
    path('my-resumes/', views.view_uploaded_resumes, name='view_my_resumes'),  
    path('delete_resume/<int:resume>/', views.delete_resume, name='delete_resume'),
    
    # Feedback
    path('view-score/', views.view_score, name='view_score'),
    path('feedback/<int:resume>/', views.view_feedback, name='view_feedback'),
    path('download_feedback/<int:resume>/', views.download_feedback_pdf, name='download_feedback'),

    # Job provider reviewing resumes
    path('job/<int:job>/resumes/', views.view_resumes_for_job, name='view_resumes_for_job'),
    path('resume/<int:resume>/status/', views.update_resume_status, name='update_resume_status'),
    path('job/<int:job>/top-resumes/', views.view_top_resumes, name='view_top_resumes'),

    # Authentication
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
