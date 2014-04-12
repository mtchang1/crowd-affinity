from django.db import models

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    question_ID = models.TimeField()


class Answer(models.Model):

