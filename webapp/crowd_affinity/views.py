# Create your views here.
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from crowd_affinity.models import *
import os.path
import random
import string

def designer(request):
    if request.method == "POST":
        t = request.POST.get("topic")
        topic = Topic(topic=t)
        topic.save()

        #for all questions given
        q_text = request.POST.get("question1") 
        q = Question(question_text=q_text, user_id=0, parent_id=0, topic_id=topic.id, designer=True)
        q.save()

        if request.POST.get("question2"):
            q_text = request.POST.get("question2") 
            q = Question(question_text=q_text, user_id=0, parent_id=0, topic_id=topic.id, designer=True)
            q.save()

        if request.POST.get("question3"):
            q_text = request.POST.get("question3") 
            q = Question(question_text=q_text, user_id=0, parent_id=0, topic_id=topic.id, designer=True)
            q.save()

    return render(request, 'designerPage.html')

def generateCode():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(7))

def start1(request):
    logout(request)
    if request.method == "POST":
        w = Worker(current_question_id=0, cur_ans1_id=0, cur_ans2_id=0, cur_ans3_id=0)
        w.save()
        
        user_code = generateCode() + str(w.id)
        w.code = user_code
        w.save()
        worker = User.objects.create_user(username=w.id, email=None, password="cp")
        user = authenticate(username=w.id, password="cp")
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse(answerQuestion))
            
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
            return HttpResponseRedirect(reverse(rate))

        else: #get new question
            return HttpResponseRedirect(reverse(answerQuestion))
    
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

    if request.POST.get('QR1'):
        #get question rating
        if q_id != 0:
            q = Question.objects.get(id=q_id)
            q.num_ratings = q.num_ratings + 1
            q.rating_rel = update_rating(q.num_ratings, q.rating_rel, float(request.POST['QR1']))
            q.rating_clear = update_rating(q.num_ratings, q.rating_clear, float(request.POST['QR2']))
            q.rating_many = update_rating(q.num_ratings, q.rating_many, float(request.POST['QR3']))
            q.save()
            
        #get answer rating
        if w.cur_ans1_id != 0:
            a = Answer.objects.get(id=w.cur_ans1_id)
            a.num_ratings = a.num_ratings + 1
            a.rating = update_rating(a.num_ratings, a.rating, float(request.POST[str(w.cur_ans1_id)]))
            a.save()

        if w.cur_ans2_id != 0:
            a = Answer.objects.get(id=w.cur_ans2_id)
            a.num_ratings = a.num_ratings + 1
            a.rating = update_rating(a.num_ratings, a.rating, float(request.POST[str(w.cur_ans2_id)]))
            a.save()
 
        if w.cur_ans3_id != 0:
            a = Answer.objects.get(id=w.cur_ans3_id)
            a.num_ratings = a.num_ratings + 1
            a.rating = update_rating(a.num_ratings, a.rating, float(request.POST[str(w.cur_ans3_id)]))
            a.save()

        w.tasks -= 1
        w.save()
        
        return HttpResponseRedirect(reverse(decide))
    else: 
        if q_id == 0:
            text = "default question"
            topic = "default topic"
        else:
            q = Question.objects.get(id=q_id)
            text = q.question_text
            topic = Topic.objects.get(id=q.topic_id).topic
        
        answer_list = []
        a = Answer.objects.filter(question_id = q_id).exclude(user_id = user.username) 
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

        template_values = {'user_id':user, 'question':text, 'answers':answer_list, 'topic':topic}
        return render(request, 'phase1rate.html', template_values)

def decide(request):
    user = request.user
    w = Worker.objects.get(id=user.username)
    r = w.tasks

    if request.POST.get('ask'):
        return HttpResponseRedirect(reverse(askQuestion))
    if request.POST.get('ans'):
        return HttpResponseRedirect(reverse(answerQuestion))
    
    template_values = {'remaining':r, 'user_id':user}
    if r > 0:  
        return render(request, 'phase1decideWhatsNext.html', template_values)
    else:
        return HttpResponseRedirect(reverse(finish))

def askQuestion(request):
    user = request.user
    w = Worker.objects.get(id=user.username)
    parent = w.current_question_id
    
    if request.POST.get('answer'):
        text = request.POST.get('answer')
        p = Question.objects.get(id=parent)

        question = Question(question_text=text, parent_id=parent, topic=p.topic, user_id=w.id)
        question.save()

        w.tasks -= 1
        w.save()
        return HttpResponseRedirect(reverse(linking))
    else:
        text = "default question"
        topic = "default topic"
        if Question.objects.count() > 0:
            q = Question.objects.get(id=parent)
            text = q.question_text

            topic = Topic.objects.get(id=q.topic_id).topic
        
        return render(request, 'phase1askQuestion.html', {'user_id':user, 'question':text, 'topic':topic})

def linking(request):
    user = request.user
    w = Worker.objects.get(id=user.username)
    r = w.tasks

    if request.POST.get('next'):
        return HttpResponseRedirect(reverse(answerQuestion))
   
    template_values = {'task_number':r, 'rem_task_number':5-r, 'user_id':user}
    if r > 0:
        return render(request, 'phase1linkingpage.html', template_values)
    else:
        return HttpResponseRedirect(reverse(finish))

def finish(request):
    user = request.user
    w = Worker.objects.get(id=user.username)
    code = w.code
    
    logout(request);
    return render(request, 'phase1finish.html', {'code':code})


#phase 2

#handle duplicate worker IDs for users
def getUID(workerID):
    return "two" + str(workerID)

def getWID(userID):
    return userID[3:]
    
def start2(request):

    logout(request)
    if request.method == "POST":
        w = WorkerTwo(current_answer_id=0, current_sentence_id=0)
        w.save()

        user_code = generateCode() + str(w.id)
        w.code = user_code
        w.save()
        worker = User.objects.create_user(username=getUID(w.id), email=None, password="cp")
        user = authenticate(username=getUID(w.id), password="cp")
        if user is not None:
            login(request, user)
        return HttpResponseRedirect(reverse(write))

    return render(request, 'phase2start.html')

def write(request):
    user = request.user
    w = WorkerTwo.objects.get(id=getWID(user.username))
    
    if request.POST.get('answer'):
        text = request.POST.get('answer')
        a_id = w.current_answer_id

        sentence = Sentence(answer_id=a_id, sentence_text=text, user_id=getUID(w.id))
        sentence.save()
        return HttpResponseRedirect(reverse(rateSentence))
 
    question = "default question"
    ans = "default answer"
    
    count = Answer.objects.count()
    if count > 0:
        random_idx = random.randint(0, count - 1)
        a = Answer.objects.all()[random_idx]
        ans = a.answer_text

        w.current_answer = a
        w.save()
        try:
            q = Question.objects.get(id=a.question_id)
            question = q.question_text
        except ObjectDoesNotExist:
            pass

    template_values = {'question':question, 'answer':ans}
    return render(request, 'phase2makeSentence.html', template_values)

def rateSentence(request):
    user = request.user
    w = WorkerTwo.objects.get(id=getWID(user.username))
    
    if request.POST.get("AR1"): 
        if float(request.POST['AR1']) > 2:
            return HttpResponseRedirect(reverse(tag))
        else:
            return HttpResponseRedirect(reverse(rewrite))
   
    question = "default question"
    ans = "default answer"
    sentence = "default sentence"
    
    count = Sentence.objects.count()
    if count > 0:
        random_idx = random.randint(0, count - 1)
        s = Sentence.objects.all()[random_idx]
        sentence = s.sentence_text
       
        try:
            a = Answer.objects.get(id=s.answer_id)
            ans = a.answer_text
            try:
                q = Question.objects.get(id=a.question_id)
                question = q.question_text
            except ObjectDoesNotExist:
                pass
        except ObjectDoesNotExist:
            pass
       
        w.current_sentence = s;
        w.save()

    template_values = {'question':question, 'answer':ans, 'sentence':sentence}
    return render(request, "phase2rateSentence.html", template_values)

def rewrite(request):
    user = request.user
    w = WorkerTwo.objects.get(id=getWID(user.username))
    s_id = w.current_sentence_id
    s = Sentence.objects.get(id=s_id)
   
    if request.POST.get('answer'):
        text = request.POST.get('answer')
        s.sentence_text = text;
        s.save()

        w.tasks -= 1
        w.save()
        return HttpResponseRedirect(reverse(connect))
    else:
        question = "default question"
        ans = "default answer"
        sentence = s.sentence_text 

        try:
            a = Answer.objects.get(id=s.answer_id)
            ans = a.answer_text
            try:
                q = Question.objects.get(id=a.question_id)
                question = q.question_text
            except ObjectDoesNotExist:
                pass
        except ObjectDoesNotExist:
            pass
 
            template_values = {'question':question, 'answer':ans, 'sentence':sentence}
 
    return render(request, 'phase2rewriteSentence.html', template_values)

def tag(request):
    user = request.user
    w = WorkerTwo.objects.get(id=getWID(user.username))
    s_id = w.current_sentence_id
    s = Sentence.objects.get(id=s_id)
   
    if request.POST.get('tags'):
        tags = request.POST.get('tags')
        t = Tag(sentence_id=s_id, tag=tags, user_id = getUID(w.id))
        t.save()

        w.tasks -= 1
        w.save()
        return HttpResponseRedirect(reverse(connect))
    else: 
        return render(request, 'phase2tagSentence.html', {'sentence': s.sentence_text})

def connect(request):
    user = request.user
    w = WorkerTwo.objects.get(id=getWID(user.username))
    r = w.tasks

    if request.POST.get('next'):
        return HttpResponseRedirect(reverse(write))
   
    template_values = {'task_number':r, 'rem_task_number':5-r, 'user_id':user}
    if r > 0:
        return render(request, 'phase1linkingpage.html', template_values)
    else:
        return HttpResponseRedirect(reverse(finish2))


def finish2(request):
    user = request.user
    w = WorkerTwo.objects.get(id=getWID(user.username))
    code = w.code
    code = "phase 2 complete!"
    
    #logout(request);
    return render(request, 'phase1finish.html', {'code':code})


