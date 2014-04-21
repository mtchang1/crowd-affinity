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
            return answerQuestion(request)
        else:
            return render(request, 'phase1rate.html')
    else:
        return render(request, 'phase1start.html')

def answerQuestion(request): 
    w = Worker.objects.get(id=request.user.username)

    if request.method == "POST": 
        q_id = w.current_question
        if request.POST.get('answer'):
            text = request.POST.get('answer')

            answer = Answer(question_id=q_id, answer_text=text, user_id=w_id)
            answer.save()

            return render(request, 'phase1rate.html')
        else:
            q_text = Question.objects.get(id=q_id).question_text
            return render(request, 'phase1answerQuestion.html', {'question':q_text})
    else: 
        #default vars
        q_id = 0;
        q_text = "What color do you like on a chair?"

    if Question.objects.count() > 0:
        random_idx = random.randint(0, Question.objects.count() - 1)
        q = Question.objects.all()[random_idx]
        q_id = q.id
        q_text = q.question_text

        w.current_question = q_id

        return render(request, 'phase1answerQuestion.html', {'question':q_text})

def askQuestion(request):
    if request.POST.get('answer'):
        text = request.POST.get('answer')

        w = Worker.objects.get(id=request.user.username)

        user = w.id
        parent = w.current_question
        answer = Question(question_text=text, parent_id=parent, user_id=user)
        answer.save()

        return checkTasks(request)
    else: 
        return render(request, 'phase1askQuestion.html')

def rate(request):
    w = Worker.objects.get(id=request.user.username)

    if request.POST.get('rateForm'):
        #do something
        if Answer.objects.count() > 0:
            random_idx = random.randint(0, Answer.objects.count() - 1)
            q = Answer.objects.all()[random_idx]
            q_id = q.id
            q_text = q.question_text

        return render(request, 'phase1rate.html')
    else: 
        return render(request, 'phase1rate.html')

def decide(request):
    w = Worker.objects.get(id=request.user.username)
    r = w.tasks
    r = 5;

    template_values = {'remaining':r}
    if r > 0:
        w.tasks = r-1
        return render(request, 'phase1decideWhatsNext.html', template_values)
    else:
        return finish(request)

def linking(request):
    w = Worker.objects.get(id=request.user.username)
    r = w.tasks
    r = 5; 
    
    template_values = {'task_number':r, 'rem_task_number':5-r}
    if r > 0:
        w.tasks = r-1
        return render(request, 'phase1linkingpage.html', template_values)
    else:
        return finish(request)

def finish(request):
    logout();
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
 
