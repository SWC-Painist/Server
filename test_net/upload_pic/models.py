
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Users(models.Model):
   username = models.CharField(max_length=64,unique=True)
   password = models.CharField(max_length=64)
   email = models.EmailField(blank=True)
   avatarName = models.CharField(max_length=64)
   avatarUrl = models.ImageField(upload_to='avatars',null=True,blank=True)
   intro = models.CharField(max_length=10)
   createTime = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return self.username

class MyPictures(models.Model):
   pid = models.AutoField(primary_key = True)
   pname = models.CharField(max_length=64)
   purlName = models.CharField(max_length=64)
   purl = models.ImageField(upload_to='imgs')
   pmd5 = models.CharField(max_length=64)

   def __str__(self):
      return self.pname



class MyFiles(models.Model):
   fid = models.AutoField(primary_key = True)
   fname = models.CharField(max_length=64,default='')
   furlName = models.CharField(max_length=64)
   furl = models.FileField(upload_to='files')
   fmd5 = models.CharField(max_length=64)
   level = models.FloatField()

   def __str__(self):
      return self.fname

class Score(models.Model):
   uid = models.ForeignKey(Users,on_delete = models.CASCADE)
   fid = models.ForeignKey(MyFiles,on_delete = models.CASCADE)
   accuracy = models.IntegerField()
   total_score = models.IntegerField()
   melody = models.IntegerField()
   rhythm = models.IntegerField()
   emotion = models.IntegerField()
   last_time = models.DateTimeField(auto_now=True)

   def __str__(self):
      return self.uid.username + ' ' + self.fid.fname

   class Meta:
      unique_together = ('uid','fid')

class Favorite(models.Model):
   uid = models.ForeignKey(Users, on_delete=models.CASCADE)
   fid = models.ForeignKey(MyFiles, on_delete=models.CASCADE)
   last_time = models.DateTimeField(auto_now=True)

   def __str__(self):
      return self.uid.username + ' ' + self.fid.fname

class Practice(models.Model):
   uid = models.ForeignKey(Users,on_delete=models.CASCADE)
   fid = models.ForeignKey(MyFiles,on_delete=models.CASCADE)
   day = models.DateField(auto_now_add=True)
   beginTime = models.TimeField(auto_now_add=True)
   endTime = models.TimeField(auto_now=True)
   intervar = models.IntegerField()
   accuracy = models.IntegerField()
   melody = models.IntegerField()
   rhythm = models.IntegerField()
   emotion = models.IntegerField()
   total_score = models.IntegerField()
   last_time = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return self.uid.username + ' ' + self.fid.fname
