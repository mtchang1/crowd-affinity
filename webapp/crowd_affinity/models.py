from django.db import models

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    user_ID = models.CharField(max_length=50)
    parent_ID = models.ForeignKey('self')
    rating = models.IntegerField(default=0)
    num_ratings = models.IntegerField(default=0)
    designer = models.BooleanField(default=False)

class Answer(models.Model):
    question_ID = ForeignKey('Question')
    answer_text = models.CharField(max_length=500)
    user_ID = models.CharField(max_length=50)

class Sentence(models.Model):
    answer_ID = ForeignKey('Answer')
    sentence_text = models.CharField(max_length=500)
    user_ID = models.CharField(max_length=50)

class Tag(models.Model):
    sentence_ID = ForeignKey('Sentence') 
    tag = models.CharField(max_length=50)
    user_ID = models.CharField(max_length=50)


