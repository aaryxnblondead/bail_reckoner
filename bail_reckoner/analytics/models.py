from django.db import models
from django.contrib.postgres.fields import ArrayField

class AnalyticsData(models.Model):
    date = models.DateField(auto_now_add=True)
    total_applications = models.IntegerField(default=0)
    approved_applications = models.IntegerField(default=0)
    rejected_applications = models.IntegerField(default=0)
    average_processing_time = models.FloatField(default=0)  # in days
    
    def __str__(self):
        return f"Analytics for {self.date}"

class AIPerformanceMetric(models.Model):
    date = models.DateField(auto_now_add=True)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    confusion_matrix = ArrayField(ArrayField(models.IntegerField()))
    
    def __str__(self):
        return f"AI Performance Metrics for {self.date}"