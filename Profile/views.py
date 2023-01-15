from rest_framework import status
from rest_framework.generics import *
from Profile.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
    
class EducationView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = EducationSerializer
    
    def get_queryset(self):
        return Education.objects.filter(user = self.request.user)
    
    def post(self, request, *args, **kwargs):
        
        request.data.update({"user" : request.user.id})
        
        try:
            school = request.data['school']
            if not isinstance(school, int):
                new_school =  Organization.objects.create(name = school, type = 'School')
                request.data['school'] = new_school.id
        except KeyError:
            pass
        
        return super().post(request, *args, **kwargs)
    
    
class SingleEducationView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EducationSerializer
    
    def get_queryset(self):
        return Education.objects.filter(user = self.request.user)
    
    def put(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        try:
            school = request.data['school']
            if not isinstance(school, int):
                new_school =  Organization.objects.create(name = school, type = 'School')
                request.data['school'] = new_school.id
        except KeyError:
            pass
        return super().patch(request, *args, **kwargs)
    
class ExperienceView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ExperienceSerializer
    
    def get_queryset(self):
        return Experience.objects.filter(user = self.request.user)
    
    def post(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        try:
            skills = request.data['skills']
            for i in range(len(skills)):
                if not isinstance(skills[i], int):
                        new_skill =  Skill.objects.create(skill_name = skills[i],user = request.user)
                        skills[i] = new_skill.id
        except KeyError:
            pass
        try:
            company = request.data['company']
            if not isinstance(company, int):
                new_company =  Organization.objects.create(name = company, type = 'Company')
                request.data['company'] = new_company.id
        except KeyError:
            pass
            
        return super().post(request, *args, **kwargs)
    
class SingleExperienceView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExperienceSerializer
    
    def get_queryset(self):
        return Experience.objects.filter(user = self.request.user)
    
    
    def put(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        try:
            skills = request.data['skills']
            for i in range(len(skills)):
                if not isinstance(skills[i], int):
                        new_skill =  Skill.objects.create(skill_name = skills[i],user = request.user)
                        skills[i] = new_skill.id
        except KeyError:
            pass
        try:
            company = request.data['company']
            if not isinstance(company, int):
                new_company =  Organization.objects.create(name = company, type = 'Company')
                request.data['company'] = new_company.id
        except KeyError:
            pass
        return super().patch(request, *args, **kwargs)
    
    
class CourseView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer
    
    def get_queryset(self):
        return Course.objects.filter(user = self.request.user)
    
    def post(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        return super().post(request, *args, **kwargs)
    
class SingleCourseView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer
    
    def get_queryset(self):
        return Course.objects.filter(user = self.request.user)
    
    def patch(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        return super().patch(request, *args, **kwargs)
    
    
class TestScoreView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TestScoreSerializer
    
    def get_queryset(self):
        return TestScore.objects.filter(user = self.request.user)
    
    def post(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        return super().post(request, *args, **kwargs)
    
class SingleTestScoreView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TestScoreSerializer
    
    def get_queryset(self):
        return TestScore.objects.filter(user = self.request.user)
    
    def patch(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        return super().patch(request, *args, **kwargs)
    
    
    
class SkillView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    # permission_classes = [IsAuthenticated]
    serializer_class = SkillSerializer
    
    def get_serializer_context(self):
        return {'owner': self.request.data['owner'], 
                'anonymous': self.request.data['anonymous'],
                'viewer': self.request.user.id}
    
    def get_queryset(self):
        try:
            profile = Profile.objects.get_or_create(user = self.request.user)[0]
            username = self.request.GET.get('username')
            if profile.username == username:
                self.request.data.update({"owner": True, "anonymous": False})
                return Skill.objects.filter(user = profile.user)
            
            else:
                profile = get_object_or_404(Profile, username=username)
                self.request.data.update({"owner": False, "anonymous": False})
                return Skill.objects.filter(user = profile.user)

        except TypeError:
            username = self.request.GET.get('username')
            profile = get_object_or_404(Profile, username=username)
            self.request.data.update({"owner": False, "anonymous": True})
            return Skill.objects.filter(user = profile.user)
    
    def post(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id, "owner": True, "anonymous": False})
        return super().post(request, *args, **kwargs)
    
    
class SingleSkillView(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SingleSkillSerializer
    
    def get_queryset(self):
        return Skill.objects.filter(user = self.request.user)
    
    
class UserProfileView(RetrieveUpdateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    
    def get_object(self):
        try:
            return Profile.objects.get(user = self.request.user)
        except ObjectDoesNotExist :
            return None
            
    def patch(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        return super().patch(request, *args, **kwargs)
    
    
class MainProfileView(RetrieveUpdateAPIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = MainProfileSerializer
    
    
    def get_serializer_context(self):
        return {'owner': self.request.data['owner']}
    

    def get_object(self):
        if self.request.method =="PATCH":
           return MainProfile.objects.get_or_create(profile = self.request.data['profile'])[0]
        
        try:
            profile = Profile.objects.get_or_create(user = self.request.user)[0]
            username = self.request.GET.get('username')
            if profile.username == username:
                self.request.data.update({"owner": True})
                return MainProfile.objects.get_or_create(profile = profile)[0]
            
            else:
                profile = get_object_or_404(Profile, username=username)
                main_profile = MainProfile.objects.get_or_create(profile = profile)[0]
                viewer_profile = Profile.objects.get_or_create(user = self.request.user)[0]
                ProfileView.objects.update_or_create(viewer = viewer_profile,
                                                     viewed_profile = main_profile)
                self.request.data.update({"owner": False})
                return main_profile

        except TypeError:
            username = self.request.GET.get('username')
            profile = get_object_or_404(Profile, username=username)
            self.request.data.update({"owner": False})
            return MainProfile.objects.get_or_create(profile = profile)[0]
        
        

    def patch(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user = self.request.user)
        username = self.request.GET.get('username')
        if profile.username != username:
            return Response({"error": "You are not allowed to perform this action"}, 
                             status=status.HTTP_403_FORBIDDEN)
        request.data.update({"profile": profile })
        return super().patch(request, *args, **kwargs)
        
        
class ProfileViewersView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileViewersSerializer
    
    def get_queryset(self):
        profile = Profile.objects.get(user = self.request.user)
        main_profile = MainProfile.objects.get(profile = profile)
        return ProfileView.objects.filter(viewed_profile = main_profile)


class EndorsementView(CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = EndorsementSerializer
    
    
    def post(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        return super().post(request, *args, **kwargs)
    
        
class OrganizationView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.filter(registered = True)
    
class EmploymentView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = EmploymentSerializer
    queryset = Employment.objects.all()
    
class SchoolListView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.filter(registered = True, type = "School")
    
class CompanyListView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.filter(registered = True, type = "Company")
