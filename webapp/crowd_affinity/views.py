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

def start1(request):
    logout(request)
    if request.method == "POST":
        w = Worker(current_question_id=0)
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

    if Question.objects.count() > 0:
        random_idx = random.randint(0, Question.objects.count() - 1)
        q = Question.objects.all()[random_idx]
        q_id = q.id
        q_text = q.question_text

        w.current_question_id = q_id 
        w.save()

    return render(request, 'phase1answerQuestion.html', {'question':q_text, 'user_id':user})

def rate(request):
    user = request.user
    w = Worker.objects.get(id=user.username)

    if request.POST.get('rateForm'):
        #TODO:get rating, add to db
        
        return HttpResponseRedirect('/decide')
    else: 
        q_id = w.current_question_id
        if q_id == 0:
            text = "default question"
        else:
            q = Question.objects.get(id=q_id)
            text = q.question_text
        #TODO: implement
        a1 = ""
        a2 = ""
        a3 = ""

        template_values = {'user_id':user, 'question':text, 'answer1':a1, 'answer2':a2, 'answer3':a3}
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
        question = Question(question_text=text, parent_id=parent, user_id=w.id)
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
 
