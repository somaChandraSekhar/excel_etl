from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    employees = models.IntegerField()
    country = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Companies'
