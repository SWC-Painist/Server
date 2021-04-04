from django.contrib import admin

# Register your models here.
from upload_pic.models import Users,Score,MyFiles,MyPictures,Practice

admin.site.register(Users)
admin.site.register(Score)
admin.site.register(MyFiles)
admin.site.register(MyPictures)
admin.site.register(Practice)

