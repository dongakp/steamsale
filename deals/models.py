from django.db import models

class Game(models.Model): 
    title = models.CharField(max_length=200)
    original_price = models.IntegerField()
    discount_price = models.IntegerField()
    discount_percent = models.IntegerField()
    steam_link = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.title}: {self.discount_price} (-{self.discount_price}%%)"
    
class Review(models.Model):
    game = models.ForeignKey(Game, related_name = 'reviews', on_delete = models.CASCADE)
    rating = models.CharField(max_length=10)
    content = models.CharField(max_length=1000)
    def __str__(self):
        return f"{self.game}: {self.rating}"