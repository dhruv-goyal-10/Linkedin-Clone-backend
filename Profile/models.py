from django.db import models
from Authentication.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models import F, Q
from django.db.models.signals import post_save
import string, random
from Network.models import SecondConnections, FirstConnections

ORGANIZATION_CHOICES = [
        ('Company', 'Company'),
        ('School', 'School'),
        ('None', 'None')
    ]

class Organization(models.Model):
    
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, blank = True, null = True)
    type = models.CharField(max_length=50, choices=ORGANIZATION_CHOICES, default='None')
    registered = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='logo/', default='profolio/logo/default1.jpg')
    
    def __str__(self):
        return f"{self.name} --> {self.type} "
    
    @property
    def get_logo(self):
        return self.logo
    
    # class Meta:
    #     app_label = 'Authentication'
    
@receiver(post_save, sender=Organization)
def set_default_username(sender, instance, created, **kwargs):
    if created: 
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        instance.username = instance.name.lower().replace(" ", "-") + "-" + rand
        instance.save()

class Profile(models.Model):
   
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20, blank = True, null = True)
    avatar = models.ImageField(upload_to='avatar/', default='profolio/avatar/default.jpg')
    headline = models.CharField(max_length=100)
    country = models.CharField(max_length=30)    
    city = models.CharField(max_length=30)
    phone_number = models.BigIntegerField(validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)], blank = True, null = True)
    username = models.CharField(max_length=100, blank = True, null = True, unique=True)
    followers = models.ManyToManyField(User, through='Network.Follow',related_name="following", blank=True)
    first_degrees = models.ManyToManyField(User, through='Network.FirstConnections', related_name="first_degree", blank=True)
    second_degrees = models.ManyToManyField(User, through='Network.SecondConnections', related_name="second_degree", blank=True)
    third_degrees = models.ManyToManyField(User, through='Network.ThirdConnections', related_name="third_degree", blank=True)
    
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.user} --> {self.full_name}"
        
        
@receiver(post_save, sender=Profile)
def set_default_username(sender, instance, created, **kwargs):
    if created: 
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        name = f"{instance.first_name} {instance.last_name}"
        instance.username = name.lower().replace(" ", "-") + "-" + rand
        instance.save()
    
class Education(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "education")
    school = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank = True, null = True,
                               related_name = "education")
    degree = models.CharField(max_length=100, blank = True, null = True)
    field_of_study = models.CharField(max_length=100, blank = True, null = True)
    start_date = models.DateField(blank = True, null = True)
    end_date = models.DateField(blank = True, null = True)
    grade = models.CharField(max_length = 100, blank = True, null = True)
    description = models.TextField(blank = True, null = True)
    tagline = models.CharField(max_length=200, blank = True, null = True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(check = Q(end_date__gte= F('start_date')), 
                                   name = "Correct end date",
                                   violation_error_message= "End date should be greater than starting date"),
        ]
        
        verbose_name_plural = "Education"
        
    def save(self, *args, **kwargs):
        self.tagline = f"Student at {self.school.name} "
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.profile.full_name} -->   ({self.degree})"
        


class Skill(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skill")
    skill_name = models.CharField(max_length=100)
    endorsed_by = models.ManyToManyField(Profile, blank=True, related_name="endorsement")
    
    def __str__(self):
        return f"{self.user.profile.full_name} --> {self.id}"


class Employment(models.Model):
    type = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.type} "

class Experience(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name= "experience")
    role = models.CharField(max_length=100)
    company = models.ForeignKey(Organization,on_delete=models.SET_NULL, blank = True, null = True,
                                related_name = "company")
    
    location = models.CharField(max_length=150)
    currently_working = models.BooleanField(default = False)
    employment_type = models.ForeignKey(Employment, on_delete=models.SET_NULL, blank = True, null = True)
    start_date = models.DateField()
    end_date = models.DateField(blank = True, null = True, default=None)
    industry = models.CharField(max_length=100)
    description = models.TextField(blank=True, null = True)
    skills = models.ManyToManyField(Skill, related_name="experience", blank = True)
    tagline = models.CharField(max_length=200, blank = True, null = True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(check = Q(end_date__gte= F('start_date')), 
                                   name = "correct end date",
                                   violation_error_message= "End date should be greater than starting date"),
        ]
        
    def save(self, *args, **kwargs):
        self.tagline = f"{self.role} at {self.company.name} "
        super().save(*args, **kwargs)
        
    
    def __str__(self):
        return f"{self.user.profile.full_name} --> {self.company.name}  ({self.role})"
    
    
class Course(models.Model):
     
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name= "course")
    course_name = models.CharField(max_length = 50)
    course_number = models.CharField(max_length = 20, blank = True, null = True)     # Subject code types
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank = True, null = True,
                                     related_name = "courses")
    
    def __str__(self):
        return f'{self.user.profile.full_name} --> {self.course_name}'
    
    
class TestScore(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name= "testscore")
    title = models.CharField(max_length = 50)
    score = models.CharField(max_length=50)
    test_date = models.DateField(blank=True, null = True)
    organization = models.ForeignKey(Organization,on_delete=models.SET_NULL, blank = True, null = True,
                                     related_name = "test_score")
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.user.profile.full_name} --> {self.title}  ({self.score})'
    
class MainProfile(models.Model):
    
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="Main_Profile")
    current_school = models.OneToOneField(Education, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    current_company =  models.OneToOneField(Experience, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    background_image = models.ImageField(upload_to='background/', default='profolio/background/default.jpg')
    about = models.TextField(blank = True, null = True, default=None)
    dob = models.DateField(blank = True, null = True, default = None)
    viewers = models.ManyToManyField(Profile, through='ProfileView')
    
    def __str__(self):
        return f'{self.profile.full_name} --> {self.profile.username}'
    
    
class ProfileView(models.Model):
    viewer = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name ='viewed_by')
    viewed_profile = models.ForeignKey(MainProfile, on_delete = models.CASCADE, related_name ='views')
    viewed_time = models.DateTimeField(auto_now = True)
    
    def __str__(self):
        return f'{self.viewer.full_name} --> {self.viewed_profile.profile.full_name}'
    
    
    
class SkillsList(models.Model):
    
    type = models.CharField(max_length=200)
    
    def __str__(self):
        return f'{self.type}'
