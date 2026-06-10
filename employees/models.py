from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    salary = models.DecimalField(max_length=10, decimal_places=2, max_digits=10)
    performance_score = models.FloatField(default=5.0)
    attrition = models.BooleanField(default=False)
    is_deleted =models.BooleanField(default=False)
    # ADD THIS FIELD: Allows null values in database backends temporarily
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name