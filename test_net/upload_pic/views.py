from django.shortcuts import render
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from upload_pic.models import Users,MyFiles,Score,Favorite,MyPictures,Practice
import json
import jwt
import time
import datetime
import random
from api.graph.svg_render import SvgRender, TextFileAna
from api.graph.svg_getter import getSVGStr
from api.hasher.fileHash import GetMD5Code
from api.hasher.fileHash import MD5Check
from api.voice import noteGeter,matcher
from django.db.models.aggregates import Count,Sum

# Create your views here.

secret = 'klsjhfuksagfkhagajdgua'


def upload_picture(request):
    try:
        photo = request.FILES.get('file', '')
        photo.name = str(time.time()) + '.jpg'
        # import os
        # if not os.path.exists('media'):
        #     os.makedirs('media')
        # with open(os.path.join('media', photo.name), 'wb') as fw:
        #
        #     fw.write(photo.read())

        MyPictures.objects.create(purl=photo,purlName=photo.name,pname="我没有名字")
        MyFiles.objects.create(furlName=photo.name,fname="我没有名字",furl=photo,level=5)

        import os
        p_path = os.path.join(os.getcwd(), 'media/imgs', photo.name)
        print(p_path)
        pmd5 = GetMD5Code(p_path)
        print(pmd5)

        pic = MyPictures.objects.get(purlName=photo.name)
        pic.pmd5 = pmd5
        pic.save()

        fi = MyFiles.objects.get(furlName=photo.name)
        fi.fmd5 = pmd5
        fi.save()


        SvgRender('/home/painist/Test_Network/test_net/html/trans1.txt')
        svg_str = getSVGStr('/home/painist/Test_Network/test_net/html/trans1.txt.html')
        # print(svg_str)
        return JsonResponse({"state":"upload_success","svg":svg_str})
    except:
        return JsonResponse({"state":"upload_failed"})

def upload_video(request):
    
    print("in")
    video = request.FILES.get('video','')
    print("here is the file")
    import os
    if not os.path.exists('video'):
        os.makedirs('video')
    with open(os.path.join('video', video.name), 'wb') as fw:
        for chunk in video.chunks():
            fw.write(chunk)
    played_note = noteGeter.AudioAnalysis(os.path.join('video', video.name))
    f_content = TextFileAna(r'/home/painist/Test_Network/test_net/html/trans1.txt')
    m_mw = matcher.MactherMiddleware(f_content['note_lists'])
    m_mw.macth(played_note)
    m_mw.RendResault(r'/home/painist/Test_Network/test_net/html/trans1.txt.html')
    res_svg_str = getSVGStr('/home/painist/Test_Network/test_net/html/trans1.txt.html.res.html')
    print("good")
    return JsonResponse({'state':'success', 'svg' : res_svg_str})
    return JsonResponse({'state':'failed'})


def download_picture(request):
    photo = request.GET.get('photo','')
    print(photo)
    filename = photo[photo.rindex('/')+1:]

    import os
    photo_path = os.path.join(os.getcwd(),'media',photo)
    print(photo_path)
    with open(photo_path,'rb') as f:
        response = HttpResponse(f.read())
        response['Content-Type'] = 'image/png'
        response['Content-Disposition'] = 'attachment;filename=' +filename
    return response

def show_history(request):
    my_json = json.loads(request.body)
    history = {}
    try:
        encode_jwt = my_json['token']
        decode_jwt = jwt.decode(encode_jwt,secret,algorithms=['HS256'])
        user_name = decode_jwt['data']
        user_now = Users.objects.get(username=user_name)
        history_list = Score.objects.filter(uid = user_now.id).order_by('-last_time')
        history['state'] = 'success'
        k = 1
        for obj in history_list:
            my_file = MyFiles.objects.get(fid=obj.fid.fid)
            file_url = 'files/' + my_file.furlName
            file_name = my_file.fname
            accuracy = obj.accuracy
            total_score = obj.total_score
            melody = obj.melody
            rhythm = obj.rhythm
            emotion = obj.emotion
            last_time = obj.last_time
            dict = {}
            dict['url'] = file_url
            dict['name'] = file_name
            dict['accuracy'] = accuracy
            dict['total_score'] = total_score
            dict['melody'] = melody
            dict['rhythm'] = rhythm
            dict['emotion'] = emotion
            dict['last_practice'] = last_time
            history[str(k)] = dict
            k += 1
    except:
        history['state'] = 'failed'

    return JsonResponse(history,safe=False)


def my_login(request):
    m = request.method
    content = {}
    dict = {}
    if m == 'POST':
        my_json = json.loads(request.body)
        username = my_json['username']
        #request.session['username'] = username
        password = my_json['password']

        encode_token = ''
        user = Users.objects.filter(username=username,password=password)
        if user:
            user = user[0]
        if user:
            payload = {'data':username}
            encode_token = jwt.encode(payload,secret,algorithm='HS256')
            print(encode_token)
            dict['user_name'] = user.username
            dict['user_intro'] = user.intro
            if user.avatarUrl:
                dict['user_avatar_url'] = user.avatarName
            else:
                dict['user_avatar_url'] = "avatars/11.png"
            content['code'] = 'success'
        else:
            content['code'] = 'failed'
        content['data'] = dict
        content['token'] = encode_token

    return JsonResponse(content, json_dumps_params={'ensure_ascii': False},safe=False)

def my_register(request):
    my_json = json.loads(request.body)
    username = my_json['username']
    password = my_json['password']
    email = my_json['email']
    content = {}
    dict = {}
    m = Users.objects.filter(username=username,password=password).count()
    print(m)
    if m == 0:
        Users.objects.create(username=username,password=password,email=email,avatarName="avatars/11.png")
        user = Users.objects.get(username=username,password=password)
        payload = {'data': username}
        encode_token = jwt.encode(payload, secret, algorithm='HS256')
        dict['user_intro'] = user.intro
        dict['user_avatar_url'] = "avatars/11.png"
        dict['user_name'] = user.username
        content['code'] = 'success'
    else:
        content['code'] = 'failed'
        encode_token = ' '

    content['data'] = dict
    content['token'] = encode_token
    return JsonResponse(content, json_dumps_params={'ensure_ascii': False})

def show_favorite(request):
    my_json = json.loads(request.body)
    dict = {}
    favorite = {}
    try:
        encode_jwt = my_json['token']
        decode_jwt = jwt.decode(encode_jwt, secret, algorithms=['HS256'])
        user_name = decode_jwt['data']
        user = Users.objects.get(username=user_name)

        file = Favorite.objects.filter(uid=user.id).order_by('-last_time')
        favorite['state'] = 'success'
        k = 1
        for obj in file:
            file_obj = MyFiles.objects.get(fid=obj.id)
            file_name = file_obj.fname
            file_url = 'media/' + file_name
            dict['url'] = file_url
            dict['name'] = file_name
            favorite[str(k)] = dict
            k += 1
    except:
        favorite['state'] = 'failed'

    return JsonResponse(favorite,safe=False)

def my_logout(request):
    #request.session.delete()
    return JsonResponse({'content':'success'})

# def progress_bar(request : WSGIRequest):
#     if request.session.get('process_progress',None) == None:
#         request.session.get['process_progress'] = 0
#
#     request.session['process_progress'] += 1
#
#     if request.session['process_progress'] == 95:
#         request.session['process_progress'] = 0
#         return JsonResponse({'progress' : 95})
#
#     return JsonResponse({'progress' : request.session['process_progress']})
def practice_time(request):
    my_json = json.loads(request.body)
    total_time = 0
    dict = {}
    try:
        encode_jwt = my_json['token']
        decode_jwt = jwt.decode(encode_jwt, secret, algorithms=['HS256'])
        user_name = decode_jwt['data']
        user_now = Users.objects.get(username=user_name)

        practice_list = Practice.objects.filter(uid=user_now)

        total_time_list = practice_list

        for obj in total_time_list:
            total_time +=  (obj.endTime.hour - obj.beginTime.hour)*60 + (obj.endTime.minute - obj.beginTime.minute)
            # obj.interval = (obj.endTime.hour - obj.beginTime.hour)*60 + (obj.endTime.minute - obj.beginTime.minute)
            # obj.save()

        max_day_obj = practice_list.values('day').annotate(sum_time=Sum('intervar')).order_by('sum_time').last()
        print(max_day_obj)
        max_day = max_day_obj['day']
        max_time = max_day_obj['sum_time']
        dict['max_day'] = max_day
        dict['max_time'] = max_time
    except:
        pass
    dict['total_time'] = total_time

    return JsonResponse(dict,json_dumps_params={'ensure_ascii': False})

def practice_files(request):
    my_json = json.loads(request.body)
    total_times = 0
    total_files = 0
    max_times_file = ''
    max_times = 0
    dict = {}
    try:
        encode_jwt = my_json['token']
        decode_jwt = jwt.decode(encode_jwt, secret, algorithms=['HS256'])
        user_name = decode_jwt['data']
        user_now = Users.objects.get(username=user_name)

        practice_list = Practice.objects.filter(uid=user_now)
        total_times = practice_list.count()

        file_list = []
        for obj in practice_list:
            file_list.append(obj.fid.fid)

        file_list = list(set(file_list))
        total_files = len(file_list)

        target_file = practice_list.values('fid').annotate(sum_files=Count('day')).order_by('-sum_files').first()
        max_times_file = target_file['fid']
        max_times_file = MyFiles.objects.get(fid=max_times_file).fname
        max_times = target_file['sum_files']

        dict = {'total_times':total_times,
                'total_files':total_files,
                'max_times_file':max_times_file,
                'max_times':max_times}
    except:
        pass

    return JsonResponse(dict,json_dumps_params={'ensure_ascii': False})



def practice_progress(request):
    my_json = json.loads(request.body)
    level_progress = 0
    score_progress = 0
    first_file_name = ''
    last_file_name = ''
    dict = {}
    try:
        encode_jwt = my_json['token']
        decode_jwt = jwt.decode(encode_jwt, secret, algorithms=['HS256'])
        user_name = decode_jwt['data']
        user_now = Users.objects.get(username=user_name)

        practice_list = Practice.objects.filter(uid=user_now)
        file_list = []
        for obj in practice_list:
            file_list.append(obj.fid)
        file_list = list(set(file_list))
        print(file_list)

        l = len(file_list)
        for file in file_list:
            practice = Practice.objects.filter(uid=user_now,fid=file).order_by('last_time')
            score_progress += practice.last().total_score - practice.first().total_score

        score_progress = score_progress/l
        last_file_level = file_list[-1].level
        last_file_name = file_list[-1].fname
        first_file_level = file_list[0].level
        first_file_name = file_list[0].fname
        level_progress = (last_file_level-first_file_level)/first_file_level
    except:
        pass
    dict = {
        'score_progress':score_progress,
        'first_file_name':first_file_name,
        'last_file_name':last_file_name,
        'level_progress':level_progress
    }
    return JsonResponse(dict,json_dumps_params={'ensure_ascii': False})

def practice_max(request):
    my_json = json.loads(request.body)
    practice_score = 0
    most_progress = ''
    hard_practice = ''
    best_practice = ''
    hard_practice_times = 0
    try:
        encode_jwt = my_json['token']
        decode_jwt = jwt.decode(encode_jwt, secret, algorithms=['HS256'])
        user_name = decode_jwt['data']
        user_now = Users.objects.get(username=user_name)
        practice_list = Practice.objects.filter(uid=user_now)

        file_list = []
        for obj in practice_list:
            file_list.append(obj.fid)
        file_list = list(set(file_list))

        print(file_list)
        for file in file_list:
            m = Practice.objects.filter(uid=user_now,fid=file).order_by('last_time')
            obj_score = m.last().total_score - m.first().total_score
            if obj_score > practice_score:
                most_progress = m.first().fid

        # hard_practice = Practice.objects.filter(uid=user_now).order_by('level').last().fid.fname
        hard_practice_level = -1
        hard_practice_file = MyFiles.objects.all().first()
        for file in file_list:
            this_file = MyFiles.objects.get(fid=file.fid)
            if this_file.level > hard_practice_level:
                hard_practice_level = this_file.level
                hard_practice_file = this_file
        hard_practice = hard_practice_file
        # print(hard_practice)
        best_practice = Practice.objects.filter(uid=user_now).order_by('total_score').last().fid.fname

        hard_practice_times = Practice.objects.filter(uid=user_now,fid=hard_practice_file).count()
    except:
        pass

    dict = {
        'best_practice':best_practice,
        'hard_practice':hard_practice.fname,
        'hard_practice_times':hard_practice_times,
        'most_progress':most_progress.fname
    }

    return JsonResponse(dict,json_dumps_params={'ensure_ascii': False})

def practice_month(request):
    my_json = json.loads(request.body)
    practice_time = 0
    practice_times = 0
    before_practice_time = 0
    increase = 0
    dict = {}
    try:
        encode_jwt = my_json['token']
        decode_jwt = jwt.decode(encode_jwt, secret, algorithms=['HS256'])
        user_name = decode_jwt['data']
        user_now = Users.objects.get(username=user_name)
        now_time = Practice.objects.filter(uid=user_now).order_by('last_time').last().last_time
        before_time = now_time -datetime.timedelta(days=30)
        before_before_time = before_time - datetime.timedelta(days=30)
        practice_list = Practice.objects.filter(last_time__gt=before_time)
        before_practice_list = Practice.objects.filter(last_time__range=(before_before_time,before_time))
        practice_times = practice_list.count()

        for obj in practice_list:
            practice_time += obj.intervar
        for obj in before_practice_list:
            before_before_time += obj.intervar

        if before_before_time != 0:
            increase = practice_time/before_before_time
    except:
        pass

    dict = {
        'practice_time': practice_time,
        'practice_times': practice_times,
        'increase': increase
    }
    return JsonResponse(dict,json_dumps_params={'ensure_ascii': False})


def progress_bar(request):
    print("received")
    minTime = 5
    maxTime = 10
    my_json = json.loads(request.body)
    time = my_json['time']

    time = int(time)
    random_number = random.randint(1, maxTime - time + 1)
    if time < minTime:
        state = False
    elif time >= minTime and time <= maxTime:
        state = random_number == 1
    else:
        state = True
    state = "success" if state else "failed"
    print(state)
    return JsonResponse({'status' : state}, json_dumps_params={'ensure_ascii': False})