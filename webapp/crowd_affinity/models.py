from django.db import models

# Create your models here.
class Topic(models.Model):
    topic = models.CharField(max_length=50)

    def __unicode__(self):
        return self.topic

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    user_id = models.CharField(max_length=50)
    parent = models.ForeignKey('self')
    topic = models.ForeignKey('topic')
    rating_rel = models.IntegerField(default=0)
    rating_clear = models.IntegerField(default=0)
    rating_many = models.IntegerField(default=0)
    num_ratings = models.IntegerField(default=0)
    designer = models.BooleanField(default=False)

    def __unicode__(self):
        return '(' + str(self.id) + ', ' + self.question_text + ', ' + str(self.parent_id) + ')'

class Answer(models.Model):
    question = models.ForeignKey('Question')
    answer_text = models.CharField(max_length=500)
    user_id = models.CharField(max_length=50)
    rating = models.IntegerField(default=0)
    num_ratings = models.IntegerField(default=0)

    def __unicode__(self):
        return '(' + str(self.id) + ', ' + self.answer_text + ', ' + str(self.question_id) + ')'

class Sentence(models.Model):
    answer = models.ForeignKey('Answer')
    sentence_text = models.CharField(max_length=500)
    user_id = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.sentence_text

class Tag(models.Model):
    sentence = models.ForeignKey('Sentence') 
    tag = models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)

    def __unicode__(self):
        return self.tag

class Worker(models.Model):
    current_question = models.ForeignKey('Question')
    cur_ans1 = models.ForeignKey('Answer', related_name='answer1')
    cur_ans2 = models.ForeignKey('Answer', related_name='answer2')
    cur_ans3 = models.ForeignKey('Answer', related_name='answer3')
    tasks = models.IntegerField(default=5)

    def __unicode__(self):
        return str(self.id)
