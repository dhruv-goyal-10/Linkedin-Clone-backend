from rest_framework import serializers, status
from .models import *
from Network.models import *
from Authentication.utils import CustomValidation
import cloudinary
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError



class MutualConnectionsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = "__all__"
        
    def to_representation(self, instance):
       
        profile = get_object_or_404(Profile, user = instance.id)
        data=ShortProfileSerializer(instance=profile, many = False).data
        
        return data
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"
        
class MyOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"
        
class EmploymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employment
        fields = "__all__"
        
class ShortEducationSerializer(serializers.ModelSerializer):
    school_data = OrganizationSerializer(source = "school", read_only = True)
    
    class Meta:
        model = Education
        fields = ['school_data']
        
class ShortExperienceSerializer(serializers.ModelSerializer):
    company_data = OrganizationSerializer(source = "company", read_only = True)
    
    class Meta:
        model = Experience
        fields = ['company_data']

class EducationSerializer(serializers.ModelSerializer):
    
    school_data = OrganizationSerializer(source = "school", read_only = True)
    owner = serializers.SerializerMethodField()
    anonymous = serializers.SerializerMethodField()
    viewer = serializers.SerializerMethodField()
    class Meta:
        model = Education
        exclude = ['tagline',]
        extra_kwargs = {'school': {'required': True},}

    def to_representation(self, instance):
       data = super().to_representation(instance)
       data.pop('user')
       return data
    
    
    def get_owner(self, instance):
        return self.context['owner']
    
    def get_anonymous(self, instance):
        return self.context['anonymous']
    
    def get_viewer(self, instance):
        return self.context['viewer']
   
    def create(self, validated_data):
        try:
            education = super().create(validated_data)
        except IntegrityError:
            raise CustomValidation(detail="End date should be greater than starting date",
                                    field= "error",
                                    status_code=status.HTTP_406_NOT_ACCEPTABLE)
            
        main_profile = MainProfile.objects.update_or_create(profile = validated_data['user'].profile)
        main_profile[0].current_school = Education.objects.filter(user = validated_data['user']).order_by('-start_date')[0]
        main_profile[0].save()
        return education
    
    
class SingleEducationSerializer(serializers.ModelSerializer):
    
    school_data = OrganizationSerializer(source = "school", read_only = True)
    class Meta:
        model = Education
        exclude = ['tagline',]
        extra_kwargs = {'school': {'required': True},}

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError:
            raise CustomValidation(detail="End date should be greater than starting date",
                                    field= "error",
                                    status_code=status.HTTP_406_NOT_ACCEPTABLE)
            
class ExperienceSerializer(serializers.ModelSerializer):
    
    company_data = OrganizationSerializer(source = "company",read_only = True)
    owner = serializers.SerializerMethodField()
    anonymous = serializers.SerializerMethodField()
    viewer = serializers.SerializerMethodField()
    
    class Meta:
        model = Experience
        exclude = ['tagline']
        extra_kwargs = {'company': {'required': True},
                        'currently_working': {'required': True},}
        
    def get_owner(self, instance):
        return self.context['owner']
    
    def get_anonymous(self, instance):
        return self.context['anonymous']
    
    def get_viewer(self, instance):
        return self.context['viewer']
        
    def validate(self, attrs):
        try:
            if attrs['currently_working'] is True:
                attrs['end_date'] = None
            else:
                try:
                    end_date = attrs['end_date']
                except:
                    raise CustomValidation(detail="If currently_working is False, please provide end date",
                                                field= "error",
                                                status_code=status.HTTP_406_NOT_ACCEPTABLE)
                if attrs[('start_date')] > end_date:
                    raise CustomValidation(detail="End date should be greater than starting date",
                                            field= "error",
                                            status_code=status.HTTP_406_NOT_ACCEPTABLE)
                        
        except KeyError:
            pass
        return super().validate(attrs)
    
    def to_representation(self, instance):
       data = super().to_representation(instance)
       data.pop('user')
       if data['employment_type'] is not None:
          data['employment_type'] = Employment.objects.get(id = data['employment_type']).type
       skills = data['skills']
       for i in range(len(skills)):
            skills[i] = Skill.objects.get(id = skills[i]).skill_name
       data['skills'] = skills
       return data
    
    def create(self, validated_data):
        experience = super().create(validated_data)
        main_profile = MainProfile.objects.update_or_create(profile = validated_data['user'].profile)
        print(Experience.objects.filter(user = validated_data['user']).order_by('-start_date')[0])
        main_profile[0].current_company = Experience.objects.filter(user = validated_data['user']).order_by('-start_date')[0]
        main_profile[0].save()
        return experience
    
    
    
class SingleExperienceSerializer(serializers.ModelSerializer):
    
    company_data = OrganizationSerializer(source = "company",read_only = True)
    class Meta:
        model = Experience
        exclude = ['tagline']
        extra_kwargs = {'company': {'required': True},
                        'currently_working': {'required': True},}
        
    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError:
            raise CustomValidation(detail="End date should be greater than starting date",
                                    field= "error",
                                    status_code=status.HTTP_406_NOT_ACCEPTABLE)
    


class CourseSerializer(serializers.ModelSerializer):
    organization_data = OrganizationSerializer(source = "organization",read_only = True)
    owner = serializers.SerializerMethodField()
    anonymous = serializers.SerializerMethodField()
    viewer = serializers.SerializerMethodField()
        
    def get_owner(self, instance):
        return self.context['owner']
    
    def get_anonymous(self, instance):
        return self.context['anonymous']
    
    def get_viewer(self, instance):
        return self.context['viewer']
    class Meta:
        model = Course
        fields = "__all__"


class SingleCourseSerializer(serializers.ModelSerializer):
    organization_data = OrganizationSerializer(source = "organization",read_only = True)
    
    class Meta:
        model = Course
        fields = "__all__"
    
    
class TestScoreSerializer(serializers.ModelSerializer):
    
    organization_data = OrganizationSerializer(source = "organization",read_only = True)
    owner = serializers.SerializerMethodField()
    anonymous = serializers.SerializerMethodField()
    viewer = serializers.SerializerMethodField()
    
    class Meta:
        model = TestScore
        fields = "__all__"

    def get_owner(self, instance):
        return self.context['owner']
    
    def get_anonymous(self, instance):
        return self.context['anonymous']
    
    def get_viewer(self, instance):
        return self.context['viewer']
    
    
    
class SingleTestScoreSerializer(serializers.ModelSerializer):
    
    organization_data = OrganizationSerializer(source = "organization",read_only = True)
    
    class Meta:
        model = TestScore
        fields = "__all__"

    
class SkillSerializer(serializers.ModelSerializer):
    
    owner = serializers.SerializerMethodField()
    anonymous = serializers.SerializerMethodField()
    viewer = serializers.SerializerMethodField()
    
    class Meta:
        model = Skill
        fields = "__all__"
        
        
    def get_owner(self, instance):
        return self.context['owner']
    
    def get_anonymous(self, instance):
        return self.context['anonymous']
    
    def get_viewer(self, instance):
        return self.context['viewer']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['endorsement_count'] = len(data.pop('endorsed_by'))
        data['endorsed'] = False
        
        if data['anonymous'] is False and data['owner'] is False:
            profile = Profile.objects.get(user__id = data['viewer'])
            skill = Skill.objects.get(id = data['id'])
            if profile.endorsement.filter(id = skill.id).exists():
                data['endorsed'] = True
        
        experience = []
        for i in instance.experience.all():
            dict = {"tagline":i.tagline, 
                    "organization_logo":cloudinary.CloudinaryImage(f"{i.company.logo}").build_url()}
            experience.append(dict)
        data['experience'] = experience
        return data

    
class ShortProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields = ['avatar', 'headline', 'username',]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data ['name'] = instance.full_name
        return data
    
    def create(self, validated_data):
        # self.request.data._mutable = True
        self.request.data._mutable = False
        return super().create(validated_data)
    
    
class SingleSkillSerializer(serializers.ModelSerializer):
    
    endorsed_by = ShortProfileSerializer(many = True, read_only = True)
    
    class Meta:
        model = Skill
        fields = "__all__"
        
    def to_representation(self, instance):
            data = super().to_representation(instance)
            data['endorsement_count'] = len(data['endorsed_by'])
            experience = []
            for i in instance.experience.all():
                dict = {"tagline":i.tagline, 
                        "organization_logo":cloudinary.CloudinaryImage(f"{i.company.logo}").build_url()}
                experience.append(dict)
            data['experience'] = experience
            return data
        

class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        exclude = ['id', 'phone_number', 'second_degrees', 'third_degrees']
        
        
    def update(self, instance, validated_data):
        try:
            username = validated_data['username']
        except KeyError:
            return super().update(instance, validated_data)
        if Profile.objects.filter(username = username).exclude(id = instance.id).exists():
            raise CustomValidation(detail ='This username is taken',
                                   field = 'username',
                                   status_code= status.HTTP_409_CONFLICT)
        valid_username = username.replace(" ", "")
        if username != valid_username:
            raise CustomValidation(detail ='This username has wrong format',
                                   field = 'username',
                                   status_code= status.HTTP_400_BAD_REQUEST)
        validated_data['username']= username.lower()
        return super().update(instance, validated_data)
        
        
class MainProfileSerializer(serializers.ModelSerializer):
    
    profile = ProfileSerializer(read_only = True)
    current_school = ShortEducationSerializer(read_only = True)
    current_company = ShortExperienceSerializer(read_only = True)
    owner = serializers.SerializerMethodField()
    
    class Meta:
        model = MainProfile
        exclude = ['id']
        
    
    def get_owner(self, instance):
        return self.context['request'].data['owner']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile_viewers_count = len(data.pop('viewers'))
        
        data['followers_count'] = len(data['profile'].pop('followers'))
        data['connections_count'] = len(data['profile'].pop('first_degrees'))
        if data['owner'] is True:
           data["profile_viewers_count"] = profile_viewers_count
           following_count = Follow.objects.filter(follower = self.context['request'].user).count()
           data['following_count'] = following_count
        else:
            owner_profile = instance.profile
            viewer_profile = get_object_or_404(Profile,user = self.context['request'].user)
            queryset = owner_profile.first_degrees.all()
            queryset = queryset.intersection(queryset, viewer_profile.first_degrees.all())
            data['mutual_connections_count'] = queryset.count()
            data['some_mutual_connections'] = MutualConnectionsSerializer(instance = queryset[:3], many=True).data
        return data

        
class ProfileViewersSerializer(serializers.ModelSerializer):
    
    viewer = ShortProfileSerializer(many = False, read_only = True)
    
    class Meta:
        model = ProfileView
        exclude = ['id', 'viewed_profile']
        
    def to_representation(self, instance):
        
        data = super().to_representation(instance)
        data['viewed_time'] = instance.viewed_time.strftime("%Y-%m-%d %H:%M:%S")

        return data
        
class EndorsementSerializer(serializers.ModelSerializer):
    
    id = serializers.IntegerField()
    endorsed_by = ShortProfileSerializer(many = True, read_only = True)
    
    class Meta:
        model = Skill
        fields = "__all__"
        extra_kwargs = {'id': {'required': True},
                        'skill_name': {'required': False},}

    def validate(self, attrs):
        data = super().validate(attrs)
        skill = get_object_or_404(Skill,id = data['id'])
        if skill.user == data['user']:
            raise CustomValidation(detail="You can't endorse your own Skill",
                                    field= "error",
                                    status_code=status.HTTP_406_NOT_ACCEPTABLE)
        return data

    def create(self, validated_data):
        profile = Profile.objects.get(user = validated_data['user'])
        skill = Skill.objects.get(id = validated_data['id'])
        
        if profile.endorsement.filter(id = skill.id).exists():
            skill.endorsed_by.remove(profile)
        else:
            skill.endorsed_by.add(profile)
        return skill

    def to_representation(self, instance):
        data =  super().to_representation(instance)
        data['skill_name'] = instance.skill_name
        return data



class MainPageSerializer(serializers.ModelSerializer):
    
    profile = ProfileSerializer(read_only = True)
    current_school = ShortEducationSerializer(read_only = True)
    current_company = ShortExperienceSerializer(read_only = True)
    owner = serializers.SerializerMethodField()
    
    class Meta:
        model = MainProfile
        exclude = ['id']
        
        
    def get_owner(self, instance):
        return self.context['request'].data['owner']


    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        education_data = Education.objects.filter(user=instance.profile.user)[:2]
        experience_data = Experience.objects.filter(user=instance.profile.user)[:2]
        skill_data = Skill.objects.filter(user=instance.profile.user)[:3]
        testscore_data = TestScore.objects.filter(user=instance.profile.user)[:2]
        course_data = Course.objects.filter(user=instance.profile.user)[:2]
        
        data['education_data'] = SingleEducationSerializer(instance=education_data, many=True).data
        data['experience_data'] = SingleExperienceSerializer(instance=experience_data, many=True).data
        data['skill_data'] = SingleSkillSerializer(instance=skill_data, many=True).data
        data['testscore_data'] = SingleTestScoreSerializer(instance=testscore_data, many=True).data
        data['course_data'] = SingleCourseSerializer(instance=course_data, many=True).data
        
        profile_viewers_count = len(data.pop('viewers'))
        
        data['followers_count'] = len(data['profile'].pop('followers'))
        data['connections_count'] = len(data['profile'].pop('first_degrees'))
        
        if data['owner'] is True:
           data["profile_viewers_count"] = profile_viewers_count
           following_count = Follow.objects.filter(follower = self.context['request'].user).count()
           data['following_count'] = following_count
        else:
            owner_profile = instance.profile
            viewer_profile = get_object_or_404(Profile,user = self.context['request'].user)
            queryset = owner_profile.first_degrees.all()
            queryset = queryset.intersection(queryset, viewer_profile.first_degrees.all())
            data['mutual_connections_count'] = queryset.count()
            data['some_mutual_connections'] = MutualConnectionsSerializer(instance = queryset[:3], many=True).data
        return data
    
    
class SkillsListSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = SkillsList
        fields = "__all__"


class ShortEducationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Education
        fields = ['tagline','school']
        
    def to_representation(self, instance):
        data= super().to_representation(instance)
        data['organization'] = data.pop('school')
        return data

class ShortExperienceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Experience
        fields = ['tagline','company']
        
    def to_representation(self, instance):
        data= super().to_representation(instance)
        data['organization'] = data.pop('company')
        return data

    

