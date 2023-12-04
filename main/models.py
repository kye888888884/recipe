from django.db import models

# Create your models here.
class Recipe(models.Model):
    id = models.DecimalField(primary_key=True, decimal_places=0, max_digits=10)
    name = models.CharField(max_length=100)
    context = models.TextField()
    amounts = models.TextField()
    time = models.DecimalField(decimal_places=0, max_digits=10)
    people = models.DecimalField(decimal_places=0, max_digits=10)

    def __str__(self):
        return self.name
    
class Ingredient(models.Model):
    id = models.DecimalField(primary_key=True, decimal_places=0, max_digits=10)
    recipe_id = models.DecimalField(decimal_places=0, max_digits=10)
    food_id = models.DecimalField(decimal_places=0, max_digits=10)

    def __str__(self):
        return str(self.recipe_id) + "-" + str(self.food_id)

class Food(models.Model):
    id = models.DecimalField(primary_key=True, decimal_places=0, max_digits=10)
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name