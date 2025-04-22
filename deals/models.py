from django.db import models

class Game(models.Model): 
    title = models.CharField(max_length=200)
    discount_rate = models.IntegerField()
    original_price = models.IntegerField()
    discounted_price = models.IntegerField()
    review_pct = models.IntegerField()
    review_count = models.IntegerField()
    release_date = models.DateField()
    tags = models.TextField()
    link = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.title}: {self.discounted_price} (-{self.discount_rate}%%)"
    
class Review(models.Model):
    game = models.ForeignKey(Game, related_name = 'reviews', on_delete = models.CASCADE)
    rating = models.CharField(max_length=10)
    content = models.CharField(max_length=1000)
    def __str__(self):
        return f"{self.game}: {self.rating}"

class Visualization(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='static/images/')