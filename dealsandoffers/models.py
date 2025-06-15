from django.utils import timezone
from django.db import models
from store.models import Product  # adjust as needed

class Deal(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)    
    title = models.CharField(max_length=100)
    description = models.TextField()
    discount_percent = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    image = models.ImageField(upload_to='deals/', blank=True, null=True)

    # ✅ Add these if missing:
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} - {self.discount_percent}% OFF"
