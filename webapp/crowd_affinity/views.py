# Create your views here.
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from crowd_affinity.models import *
import os.path
import random

def designer(request):
    if request.method == "POST":
        t = request.POST.get("topic")
        topic = Topic(topic=t)
        topic.save()

        #for all questions given
        q_text = request.POST.get("question1") #TODO: edit
        q = Question(question_text=q_text, user_id=0, parent_id=0, topic_id=topic.id, designer=True)
        q.save()

    return render(request, 'designer.html')

def start1(request):
    logout(request)
    if request.method == "POST":
        w = Worker(current_question_id=0, cur_ans1_id=0, cur_ans2_id=0, cur_ans3_id=0)
        w.save()
        worker = User.objects.create_user(username=w.id, email=None, password="cp")
        user = authenticate(username=w.id, password="cp")
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/answerQuestion')
            
    return render(request, 'phase1start.html')

def answerQuestion(request): 
    user = request.user
    w = Worker.objects.get(id=user.username)

    if request.method == "POST":
        if request.POST.get('answer'):
            text = request.POST.get('answer')
            q_id = w.current_question_id

            answer = Answer(question_id=q_id, answer_text=text, user_id=w.id)
            answer.save()
            return HttpResponseRedirect('/rate')

        else: #get new question
            return HttpResponseRedirect('/answerQuestion')
    
    #default vars
    q_text = "default question"
    q_topic = "default topic"

    if Question.objects.count() > 0:
        random_idx = random.randint(0, Question.objects.count() - 1)
        q = Question.objects.all()[random_idx]
        q_id = q.id
        q_text = q.question_text
        q_topic = Topic.objects.get(id=q.topic_id).topic

        w.current_question_id = q_id 
        w.save()

    return render(request, 'phase1answerQuestion.html', {'topic':q_topic, 'question':q_text, 'user_id':user})

def update_rating(new_num_ratings, old_rating, new_rating):
    return (old_rating * (new_num_ratings - 1) + new_rating) / new_num_ratings

def rate(request):
    user = request.user
    w = Worker.objects.get(id=user.username)
    q_id = w.current_question_id

    if request.POST.get('rateForm'):
        #get question rating
        if q_id != 0:
            q = Question.objects.get(id=q_id)
            q.num_ratings = q.num_ratings + 1
            q.rating_rel = update_rating(q.num_ratings, q.rating_rel, request.POST['QR1'])
            q.rating_clear = update_rating(q.num_ratings, q.rating_clear, request.POST['QR2'])
            q.rating_many = update_rating(q.num_ratings, q.rating_many, request.POST['QR3'])
            q.save()
            
        #get answer rating
        if w.cur_ans1_id != 0:
            a = Answer.objects.get(id=w.cur_ans1_id)
            a.num_ratings = a.num_ratings + 1
            a.rating = update_rating(a.num_ratings, a.rating, request.POST[w.cur_ans1_id])
            a.save()

        if w.cur_ans2_id != 0:
            a = Answer.objects.get(id=w.cur_ans2_id)
            a.num_ratings = a.num_ratings + 1
            a.rating = update_rating(a.num_ratings, a.rating, request.POST[w.cur_ans2_id])
            a.save()
 
        if w.cur_ans3_id != 0:
            a = Answer.objects.get(id=w.cur_ans3_id)
            a.num_ratings = a.num_ratings + 1
            a.rating = update_rating(a.num_ratings, a.rating, request.POST[w.cur_ans3_id])
            a.save()       
        
        return HttpResponseRedirect('/decide')
    else: 
        if q_id == 0:
            text = "default question"
        else:
            q = Question.objects.get(id=q_id)
            text = q.question_text
        
        answer_list = []
        a = Answer.objects.filter(question_id = q_id) 
        count = a.count()
        if count > 0:
            random_idx = random.randint(0, count - 1)
            a1 = a[random_idx] 
            answer_list.append(a1)
            w.cur_ans1_id = a1.id
        else:
            w.cur_ans1_id = 0;

        if count > 1:
            idx = (random_idx + 1) % count
            a2 = a[idx] 
            answer_list.append(a2)
            w.cur_ans2_id = a2.id
        else:
            w.cur_ans2_id = 0;

        if count > 2:
            idx = (random_idx + 2) % count
            a3 = a[idx]
            answer_list.append(a3)
            w.cur_ans3_id = a3.id
        else:
            w.cur_ans3_id = 0;
 
        w.save()

        template_values = {'user_id':user, 'question':text, 'answers':answer_list}
        return render(request, 'phase1rate.html', template_values)

def decide(request):
    user = request.user
    w = Worker.objects.get(id=user.username)
    r = w.tasks

    if request.POST.get('ask'):
        return HttpResponseRedirect('/askQuestion')
    if request.POST.get('ans'):
        return HttpResponseRedirect('/answerQuestion')
    
    template_values = {'remaining':r-1, 'user_id':user}
    if r > 1:   
        w.tasks = r-1
        w.save()
        return render(request, 'phase1decideWhatsNext.html', template_values)
    else:
        return HttpResponseRedirect('/finish')

def askQuestion(request):
    user = request.user
    w = Worker.objects.get(id=user.username)
    parent = w.current_question_id
    
    if request.POST.get('answer'):
        text = request.POST.get('answer')
        p = Question.objects.get(id=parent)

        question = Question(question_text=text, parent_id=parent, topic=p.topic, user_id=w.id)
        question.save()

        return HttpResponseRedirect('/linking')
    else:
        if Question.objects.count() > 0:
            q = Question.objects.get(id=parent)
            text = q.question_text
        else:
            text = "default question"
        return render(request, 'phase1askQuestion.html', {'user_id':user, 'question':text})

def linking(request):
    user = request.user
    w = Worker.objects.get(id=user.username)
    r = w.tasks

    if request.POST.get('next'):
        return HttpResponseRedirect('/answerQuestion')
   
    template_values = {'task_number':r-1, 'rem_task_number':6-r, 'user_id':user}
    if r > 1:
        w.tasks = r-1
        w.save()
        return render(request, 'phase1linkingpage.html', template_values)
    else:
        return HttpResponseRedirect('/finish')

def finish(request):
    #give worker link:perhaps cookie/session_id?
    logout(request);
    return render(request, 'phase1finish.html')


#phase 2
def start2(request):
    return render(request, 'phase2start.html')

def write(request):
    #ans = Answer.objects.get(question_id=0)
    ans = "hi"
    template_values = {'question':"", 'answer':ans}
    return render(request, 'phase2MakeSentence.html', template_values)

def rateSentence(request):
    #TODO: based on rating, determine whether -> tag or -> rewrite
    return render(request, "phase2rateSentence.html")

def rewrite(request):
    return render(request, 'phase2rewriteSentence.html')

def tag(request):
    return render(request, 'phase2tagSentence.html')
 
