# Create your views here.
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from crowd_affinity.models import *
import os.path
import random

def start1(request):
    return render(request, 'phase1start.html')

def answerQuestion(request):
    
    #TODO: logic error: question displayed != question entered into db
    
    #default vars
    q_id = 0;
    q_text = "What color do you like on a chair?"

    if Question.objects.count() > 0:
        random_idx = random.randint(0, Question.objects.count() - 1)
        q = Question.objects.all()[random_idx]
        q_id = q.id
        q_text = q.question_text
    
    if request.method == "post":
        if request.POST.get('answer'):
            text =request.POST.get('answer')

            #dummy vars
            user = "test user";
            answer = Answer(question_id=q_id, answer_text=text, user_id=user)
            answer.save()

            return render(request, 'phase1rate.html')
        else:
            pass
    else: 
        return render(request, 'phase1answerQuestion.html', {'question':q_text})

def askQuestion(request):
    if request.POST.get('answer'):
        text = request.POST.get('answer')

        #dummy vars
        user = "test user";
        parent = 0; #TODO: need to pass through in request somehow
        answer = Question(question_text=text, parent_id=parent, user_id=user)
        answer.save()

        return render(request, 'phase1answerQuestion.html')
    else: 
        return render(request, 'phase1askQuestion.html')

def rate(request):
    return render(request, 'phase1rate.html')

def decide(request):
    #TODO: find remaining number of tasks for user
    r = 0;
    template_values = {'remaining':r}
    return render(request, 'phase1decideWhatsNext.html', template_values)


def start2(request):
    return render(request, 'phase2start.html')

def write(request):
    #ans = Answer.objects.get(question_id=0)
    ans = "hi"
    template_values = {'question':"", 'answer':ans}
    return render(request, 'phase2MakeSentence.html', template_values)

def rateSentence(request):
    return render(request, "phase2rateSentence.html")

def rewrite(request):
    return render(request, 'phase2rewriteSentence.html')

def tag(request):
    return render(request, 'phase2tagSentence.html')
 
