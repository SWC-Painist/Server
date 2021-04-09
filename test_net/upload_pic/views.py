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
import os
from api.graph.svg_render import SvgRender, TextFileAna
from api.graph.svg_getter import SaveAsPng
from api.hasher.fileHash import GetMD5Code
from api.hasher.fileHash import MD5Check
from api.voice import noteGeter,matcher,noteFilter
from django.db.models.aggregates import Count,Sum
import traceback

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

        import os
        p_path = os.path.join(os.getcwd(), 'media/imgs', photo.name)
        print(p_path)
        pmd5 = GetMD5Code(p_path)
        print(pmd5)

        pic = MyPictures.objects.get(purlName=photo.name)
        pic.pmd5 = pmd5
        pic.save()


        print("Saved")
        #这里调用一个算法生成一个字符串并保存为txt,由于视图算法正在优化，假定为第一条训练
        SvgRender('/home/painist/Test_Network/test_net/html/trans1.txt')
        png_path = SaveAsPng("/home/painist/Test_Network/test_net/html/trans1.txt.html")

        f_path = '/home/painist/Test_Network/test_net/html/' + png_path.split('/')[-1].split('.')[0] + '.' + png_path.split('/')[-1].split('.')[1]

        # InitExe(f_path + '.html')
        # png_path2 = SaveAsPng(f_path + '.html.exe.html')

        temp_url = png_path.split('/')[-1]
        if MyFiles.objects.filter(furlName=temp_url).count() == 0:
            MyFiles.objects.create(furlName=temp_url, fname="我没有名字", furl=photo, level=5)
            fi = MyFiles.objects.get(furlName=temp_url)
            fi.fmd5 = pmd5
            fi.save()
        return JsonResponse({"state":"upload_success","url":png_path,'temp_url': temp_url})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"state":"upload_failed"})
def upload_picture_info(request):
    try:
        my_json = json.loads(request.body)
        score_name = my_json['score_name']
        temp_url = my_json['temp_url']
        # pic = MyPictures.objects.get(purlName=temp_url)
        # print(pic)
        # pic.pname = score_name
        # pic.save()
        print(temp_url)
        fi = MyFiles.objects.get(furlName=temp_url)
        fi.fname = score_name
        fi.save()
        try:
            encode_jwt = my_json['token']
            decode_jwt = jwt.decode(encode_jwt, secret, algorithms=['HS256'])
            user_name = decode_jwt['data']
            user = Users.objects.get(username=user_name)

            score_list = Score.objects.filter(uid=user,fid=fi)
            print(2)
            if score_list:
                pass
            else:
                Score.objects.create(uid=user, fid=fi, accuracy=0, total_score=0, melody=0, rhythm=0, emotion=0)
            Practice.objects.create(uid=user, fid=fi,intervar=0,accuracy=0,melody=0,rhythm=0,emotion=0,total_score=0)
            print(1)
            add_to_favorite = my_json['add_to_favorite']
            if(add_to_favorite):
                Favorite.objects.create(uid=user,fid=fi)

            return JsonResponse({'change':'success','favorite':'success'})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'change':'success','favorite':'failed'})
    except:
        return JsonResponse({'change':'failed','favorite':'failed'})

def upload_video(request):
    try:
        video = request.FILES.get('video','')
        print("here is the file")
        import os
        if not os.path.exists('video'):
            os.makedirs('video')
        with open(os.path.join('video', video.name), 'wb') as fw:
            for chunk in video.chunks():
                fw.write(chunk)

        print(video.name)
        return JsonResponse({'state':'success', 'url' : video.name})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'state':'failed'})

def check_video(request):
    my_json = json.loads(request.body)
    my_return = {}
    print(my_json)
    try:
        audio_url = my_json['audio_url']
        music_url = my_json['music_url']
        print(audio_url)
        played_note = noteGeter.AudioAnalysis(os.path.join('video', audio_url))
        played_note = noteFilter.ShortEventFilter(played_note)

        f_path = '/home/painist/Test_Network/test_net/html/' + music_url.split('/')[-1].split('.')[0] + '.' + music_url.split('/')[-1].split('.')[1]
        print(f_path)
        f_content = TextFileAna(f_path)   #r'/home/painist/Test_Network/test_net/html/trans1.txt'

        m_mw = matcher.MactherMiddleware(f_content['note_lists'])
        m_mw.macth(played_note)
        my_score = m_mw.GetScore()
        right_score = my_score['right']
        left_score = my_score['left']
        chord_score = my_score['chord']
        total_score = my_score['total']
        m_mw.RendResault(f_path + '.html') #r'/home/painist/Test_Network/test_net/html/trans1.txt.html'
        res_png_url = SaveAsPng(f_path + '.html.res.html')  #'/home/painist/Test_Network/test_net/html/trans1.txt.html.res.html'

        furlName = music_url.split('/')[-1]
        print(furlName)
        try:
            encode_jwt = my_json['token']
            decode_jwt = jwt.decode(encode_jwt, secret, algorithms=['HS256'])
            user_name = decode_jwt['data']
            user = Users.objects.get(username=user_name)
            my_file = MyFiles.objects.get(furlName=furlName)
            print(my_file)
            my_sc = Score.objects.get(uid=user,fid=my_file)
            my_pra = Practice.objects.filter(uid=user,fid=my_file).last()
            print(my_pra)
            print(my_pra.beginTime)
            print(my_pra.endTime)
            if my_pra.beginTime.hour == 23 and my_pra.endTime.hour != 23:
                my_pra.intervar = (my_pra.endTime.hour - my_pra.beginTime.hour + 24) * 60 + (my_pra.endTime.minute - my_pra.beginTime.minute)
            else:
                my_pra.intervar = (my_pra.endTime.hour - my_pra.beginTime.hour) * 60 + (my_pra.endTime.minute - my_pra.beginTime.minute)
            my_pra.total_score = total_score
            my_pra.rhythm = chord_score
            my_pra.emotion = right_score
            my_pra.melody = left_score
            my_pra.save()
            if my_sc.total_score != 0:
                progress = (my_pra.total_score - my_sc.total_score) / my_sc.total_score - 1
                if progress < 0:
                    progress = 0
                else:
                    pass
            else:
                progress = 100

            my_sc.total_score = total_score
            my_sc.rhythm = chord_score
            my_sc.emotion = right_score
            my_sc.melody = left_score
            my_sc.save()

            my_return = {
                'state':'success',
                'progress':progress,
                'chord':chord_score,
                'left_score':left_score,
                'right_score':right_score,
                'total_score':total_score,
                'url':res_png_url
            }

        except Exception as e:
            traceback.print_exc()
        return JsonResponse(my_return)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'state':'failed'})

def check_video_only(request):
    my_json = json.loads(request.body)
    audio_url = my_json['audio_url']
    music_url = my_json['music_url']
    play_note = int(my_json['should_play'])
    print(audio_url)

    f_path = '/home/painist/Test_Network/test_net/html/' + music_url.split('/')[-1].split('.')[0] + '.' + music_url.split('/')[-1].split('.')[1]
    print(f_path)
    f_content = TextFileAna(f_path)  # r'/home/painist/Test_Network/test_net/html/trans1.txt'
    m_mw = matcher.pitchOnlyMiddleWare(f_content['note_lists'],0,play_note)
    played_note = noteGeter.AudioAnalysis(os.path.join('video', audio_url))
    m_mw.macth(played_note)

    # InitExe(f_path + '.html')
    # png_path = SaveAsPng(f_path + '.html.exe.html')

    Rend(f_path + '.html.exe.html')
    png_path = SaveAsPng(f_path + '.html.exe.html')

    should_play = m_mw.GetShouldPlayed()
    end = m_mw.End()
    return JsonResponse({'url':png_path,'should_play':should_play,'end':end})


def download_picture(request):
    photo = request.GET.get('photo','')
    print(photo)
    filename = photo[photo.rindex('/')+1:]

    import os
    photo_path = os.path.join(os.getcwd(),'media',photo)
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
            file_url = 'SVG/' + my_file.furlName
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
            dict = {}
            file_obj = obj.fid
            file_name = file_obj.fname
            file_url = 'SVG/' + file_obj.furlName
            dict['url'] = file_url
            dict['name'] = file_name
            dict['last_time'] = obj.last_time
            s = Score.objects.get(uid=user,fid=file_obj).total_score
            dict['total_score'] = s
            favorite[str(k)] = dict
            k += 1
            print(favorite)

    except:
        favorite['state'] = 'failed'

    return JsonResponse(favorite, safe=False)




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
            total_time +=  obj.intervar
            # obj.interval = (obj.endTime.hour - obj.beginTime.hour)*60 + (obj.endTime.minute - obj.beginTime.minute)
            # obj.save()
        max_day_obj = practice_list.values('day').annotate(sum_time=Sum('intervar')).order_by('sum_time').last()
        print(max_day_obj)
        max_day = max_day_obj['day']
        max_time = max_day_obj['sum_time']
        dict['max_day'] = max_day
        dict['max_time'] = max_time
    except Exception as e:
        traceback.print_exc()
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
        print(practice_list)
        file_list = []
        for obj in practice_list:
            if obj.fid not in file_list:
                file_list.append(obj.fid)
        # file_list = list(set(file_list))
        print('***************************************************************************************')
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
        if level_progress < 0:
            level_progress = 0
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
        print('-------------------------------------------------------------------------------------------------')
        print(file_list)
        for file in file_list:
            m = Practice.objects.filter(uid=user_now,fid=file).order_by('last_time')
            print(m)
            obj_score = m.last().total_score - m.first().total_score
            if obj_score < 0:
                obj_score = 0
            print(obj_score)
            if obj_score >= practice_score:
                most_progress = m.first().fid
                practice_score = obj_score

        print(most_progress)
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

def recommend(request):
    my_json = json.loads(request.body)
    try:
        encode_jwt = my_json['token']
        decode_jwt = jwt.decode(encode_jwt, secret, algorithms=['HS256'])
        user_name = decode_jwt['data']
        user_now = Users.objects.get(username=user_name)
        try:
            get_level = my_json['level']
            total_score = my_json['total_score']
            if total_score <= 30:
                level = get_level - 2
                if get_level == 2:
                    level = 1
                else:
                    pass
            elif total_score > 30 and total_score <=50:
                level = get_level - 1
                if get_level == 1:
                    level = 1
                else:
                    pass
            elif total_score >50 and total_score <90:
                level = total_score
            else:
                level = get_level + 1
                if get_level == 10:
                    level = 10
                else:
                    pass
            get_file = MyFiles.filter(level=level).first()
            return_dict = {
                'state':'success',
                'name':get_file.fname,
                'url':get_file.furlName,
                'level':str(int(get_file.level))
            }
            return JsonResponse(return_dict,json_dumps_params={'ensure_ascii': False})
        except:
            obj1 = MyFiles.objects.filter(level=1).first()
            obj2 = MyFiles.objects.filter(level=3).first()
            obj3 = MyFiles.objects.filter(level=5).first()
            obj4 = MyFiles.objects.filter(level=7).first()
            return_dict = {
                'state':'success',
                '1':{
                    'name':obj1.fname,
                    'url':'SVG/' + obj1.furlName,
                    'level':str(int(obj1.level))
                },
                '2':{
                    'name': obj2.fname,
                    'url': 'SVG/' + obj2.furlName,
                    'level': str(int(obj2.level))
                },
                '3':{
                    'name': obj3.fname,
                    'url': 'SVG/' + obj3.furlName,
                    'level': str(int(obj3.level))
                },
                '4':{
                    'name': obj4.fname,
                    'url': 'SVG/' + obj4.furlName,
                    'level': str(int(obj4.level))
                }
            }
            return JsonResponse(return_dict,json_dumps_params={'ensure_ascii': False})
    except:
        return JsonResponse({'state': 'failed'})
