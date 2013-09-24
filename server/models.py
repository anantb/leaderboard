from django.db import models

'''
Leaderboard Models

@author: Anant Bhardwaj
@date: Apr 8, 2013
'''


class User(models.Model):
	id = models.AutoField(primary_key=True)
	timestamp = models.DateTimeField(auto_now=True)
	email = models.CharField(max_length=100, unique = True)
	f_name = models.CharField(max_length=50)
	l_name = models.CharField(max_length=50)
	password = models.CharField(max_length=500)

	def __unicode__(self):
		return self.f_name + ' ' + self.l_name

	class Meta:
		app_label = 'server'
		db_table = "users"


class Score(models.Model):
	id = models.AutoField(primary_key=True)
	timestamp = models.DateTimeField(auto_now=True)
	user = models.ForeignKey('User')
	tries = models.IntegerField()
	precision = models.FloatField()
	recall = models.FloatField()

	def __unicode__(self):
		return self.user_id + '_score'

	class Meta:
		app_label = 'server'
		db_table = "scores"