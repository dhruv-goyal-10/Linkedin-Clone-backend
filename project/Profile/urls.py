from django.urls import path
from Profile.views import *

urlpatterns = [
    path('organization/', OrganizationView.as_view()),
    path('myorganization/', MyOrganizationView.as_view()),
    # path('school/', SchoolListView.as_view()),
    # path('company/', CompanyListView.as_view()),
    path('employment/', EmploymentView.as_view()),
    
    path('education/', EducationView.as_view()),
    path('education/<int:pk>/', SingleEducationView.as_view()),
    
    path('experience/', ExperienceView.as_view()),
    path('experience/<int:pk>/', SingleExperienceView.as_view()),
    
    path('course/', CourseView.as_view()),
    path('course/<int:pk>/', SingleCourseView.as_view()),
    
    path('testscore/', TestScoreView.as_view()),
    path('testscore/<int:pk>/', SingleTestScoreView.as_view()),
    
    path('skill/', SkillView.as_view()),
    path('skill/<int:pk>/', SingleSkillView.as_view()),
    
    path('userprofile/', UserProfileView.as_view()),
    path('mainprofile/', MainProfileView.as_view()),
    
    path('viewers/', ProfileViewersView.as_view()),
    
    path('skill/endorse/', EndorsementView.as_view()),
    path('skill/list/', SkillsListView.as_view()),
    
    path('mainpage/', MainPageView.as_view()),
    path('search/', MainProfileSearchView.as_view()),
]
