from django.contrib.auth.models import User
from django.db import models

from grocerylist import UNITS


class Category(models.Model):
    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, verbose_name='User')

    class Meta:
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, verbose_name='User')
    servings = models.IntegerField(default=0, blank=True)

    def __unicode__(self):
        return self.name

    def calories_per_serving(self):
        if self.servings:
            total_calories = 0
            for ingredient in self.recipeingredient_set.all():
                total_calories += ingredient.calories
            return total_calories / self.servings
        return 0


class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, verbose_name='Category', blank=True, null=True)
    user = models.ForeignKey(User, verbose_name='User')

    def __unicode__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, verbose_name='Recipe')
    ingredient = models.ForeignKey(Ingredient, verbose_name='Ingredient')
    amount = models.DecimalField(decimal_places=3, max_digits=6)
    unit = models.CharField(max_length=4, choices=UNITS)
    calories = models.IntegerField(default=0, blank=True)

    def __unicode__(self):
        return "{0} {1}".format(self.display_amount(), self.ingredient.name)

    def display_amount(self):
        from decimal import Decimal
        from fractions import Fraction
        integer_portion = int(self.amount)
        decimal_portion = Decimal(round(self.amount - integer_portion, 3))
        fractional_portion = Fraction(decimal_portion)
        unit = " " + self.unit
        if unit == " unit":
            unit = ""
        elif integer_portion > 1 or (integer_portion == 1 and decimal_portion):
            unit += "s"
        if decimal_portion and fractional_portion:
            if integer_portion:
                return "{0} {1}/{2}{3}".format(
                    integer_portion,
                    fractional_portion.numerator,
                    fractional_portion.denominator,
                    unit
                )
            else:
                return "{0}/{1}{2}".format(
                    fractional_portion.numerator,
                    fractional_portion.denominator,
                    unit
                )
        else:
            return "{0}{1}".format(integer_portion, unit)
