from django.db import models
from django.contrib.auth.models import User


class Budget(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    user = models.OneToOneField(User, related_name='budget')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='weekly')

    def __str__(self):
        return "{0}: ${1}/{2}".format(self.user.username, self.amount, self.period)


class Entry(models.Model):
    user = models.ForeignKey(User, related_name='entries')
    date = models.DateField()
    description = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return "{0} | {1} | ${2}".format(self.date, self.description, self.cost)


class Profit(models.Model):
    user = models.ForeignKey(User, related_name='profits')
    date = models.DateField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return "{0} | +${1}".format(self.date, self.amount)
