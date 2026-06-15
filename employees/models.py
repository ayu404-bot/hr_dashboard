from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    
    # FIXED: DecimalField se max_length hata diya hai, sirf max_digits aur decimal_places zaroori hain
    salary = models.DecimalField(decimal_places=2, max_digits=10)
    
    performance_score = models.FloatField(default=5.0)
    attrition = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # Allows null values in database backends temporarily
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.name