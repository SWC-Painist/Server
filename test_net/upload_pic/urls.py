from django.urls import path,include
from upload_pic import views

urlpatterns = [
   path('upload/picture/',views.upload_picture),
   path('upload/video/',views.upload_video),
   path('download/picture/',views.download_picture),
   path('history/',views.show_history),
   path('login/',views.my_login),
   path('register/',views.my_register),
   path('favorite/',views.show_favorite),
   path('logout/',views.my_logout),
   path('ask_progress/',views.progress_bar),
   path('practice/time/',views.practice_time),
   path('practice/files/',views.practice_files),
   path('practice/month/',views.practice_month),
   path('practice/max/',views.practice_max),
   path('practice/progress/',views.practice_progress),
]



