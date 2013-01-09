from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=64)

class Option(models.Model):
    title = models.CharField(max_length=128)
    category = models.ForeignKey(Category)

class Ballot(models.Model):
    pass

class BallotOption(models.Model):
    order = models.IntegerField()
    ballot = models.ForeignKey(Ballot)
    option = models.ForeignKey(Option)

class AlreadyVoted(models.Model):
    username = models.CharField(max_length=128)
