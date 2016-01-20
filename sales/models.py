from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class UserPlan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('admin.AuthUser', db_constraint=False)
    plan = models.CharField(max_length=255, blank=False)
    date_start = models.DateField(blank=False)
    date_end = models.DateField(blank=False)
    target_revenue = models.FloatField(blank=False)
    target_margin = models.FloatField(blank=False)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'users_plan'


class Genre(models.Model):
    id = models.IntegerField(primary_key=True)
    genre_name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'genre'


class Campaign(models.Model):
    campaign_id = models.AutoField(primary_key=True)
    campaign = models.CharField(max_length=255, blank=False)
    advertiser_id = models.IntegerField(null=True, default=None)
    os = models.CharField(max_length=255)
    genre = models.ForeignKey('Genre', to_field='id', db_constraint=False)

    class Meta:
        db_table = 'campaigns'


class StatAdvertiserBase(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=15, default='')
    traffic = models.CharField(max_length=15, default='')
    type = models.CharField(max_length=15, default='')
    campaign = models.ForeignKey('Campaign', db_constraint=False)
    budget = models.IntegerField(blank=False)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'stats_advertiser_base'
        unique_together = ('country', 'traffic', 'type', 'campaign')


class StatAdvertiser(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(blank=False, default=None)
    base = models.ForeignKey('StatAdvertiserBase', to_field='id', db_constraint=False, default=None)
    campaign_status = models.BooleanField(default=True)
    revenue = models.FloatField(blank=False, default=None)
    margin = models.FloatField(blank=False, default=None)

    class Meta:
        db_table = 'stats_advertiser'
        unique_together = ('date', 'base')


class StatPublisherBase(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.IntegerField(default=None)
    #app_name = models.CharField(max_length=255)
    publisher_id = models.IntegerField(default=None)
    country = models.CharField(max_length=15, default='')
    #type = models.CharField(max_length=15, default='')
    #os = models.CharField(max_length=15, default='')
    publisher_genre = models.ForeignKey('Genre', to_field='id', db_constraint=False, default=None,
                                        related_name='publisher_genre')
    advertiser_genre = models.ForeignKey('Genre', to_field='id', db_constraint=False, default=None,
                                         related_name='advertiser_genre')
    impression_avail = models.IntegerField(default=None)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'stats_publisher_base'
        unique_together = ('app_id', 'publisher_id', 'advertiser_genre', 'publisher_genre',
                           'country')


class StatPublisher(models.Model):
    date = models.DateField(blank=False)
    base = models.ForeignKey('StatPublisherBase', to_field='id', db_constraint=False, default=None)
    impression = models.IntegerField()
    revenue = models.FloatField(blank=False, default=None)
    margin = models.FloatField(blank=False, default=None)
    status = models.BooleanField(default=True)
    class Meta:
        db_table = 'stats_publisher'


class App(models.Model):
    app_id = models.AutoField(primary_key=True)
    publisher_id = models.IntegerField()
    app = models.CharField(max_length=255)
    os = models.CharField(max_length=15)
    class Meta:
        db_table = 'app'