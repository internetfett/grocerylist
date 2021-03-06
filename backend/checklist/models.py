from django.contrib.auth.models import User
from django.db import models

from grocerylist import UNITS
from recipes.models import Category, Ingredient


class Checklist(models.Model):
    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, verbose_name='User')

    def __unicode__(self):
        return self.name

    def add_recipes(self, recipes):
        from django.db.models import Sum
        from checklist.models import Checklist, ChecklistIngredient, Exclusion, Repeatable
        from recipes.models import RecipeIngredient
        exclusions = Exclusion.objects.values_list('ingredient', flat=True)
        recipe_ingredients = RecipeIngredient.objects.filter(recipe__in=recipes) \
            .values('ingredient', 'unit').annotate(amount=Sum('amount'))
        for recipe_ingredient in recipe_ingredients:
            if recipe_ingredient['ingredient'] not in exclusions:
                checklist_ingredient = ChecklistIngredient.objects.create(
                    checklist = Checklist.objects.get(id=self.id),
                    amount = recipe_ingredient['amount'],
                    unit = recipe_ingredient['unit'],
                    ingredient = Ingredient.objects.get(id=recipe_ingredient['ingredient'])
                )
        """for repeatable in Repeatable.objects.all():
            if repeatable.ingredient:
                repeatable.ingredient.status = False
                repeatable.ingredient.save()
            if repeatable.item:
                repeatable.item.status = False
                repeatable.item.save()"""


class ChecklistBaseItem(models.Model):
    checklist = models.ForeignKey(Checklist, verbose_name='Checklist')
    status = models.BooleanField(default=False, blank=True)
    amount = models.DecimalField(decimal_places=3, max_digits=6, default=1)
    unit = models.CharField(max_length=4, choices=UNITS)

    class Meta:
        abstract = True

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


class ChecklistIngredient(ChecklistBaseItem):
    ingredient = models.ForeignKey(Ingredient, verbose_name='Ingredient')

    def __unicode__(self):
        return self.ingredient.name


class ChecklistItem(ChecklistBaseItem):
    name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, verbose_name='Category', blank=True, null=True)

    def __unicode__(self):
        return self.name


class Exclusion(models.Model):
    ingredient = models.ForeignKey(Ingredient, verbose_name='Ingredient')

    def __unicode__(self):
        return self.ingredient.name


class Repeatable(models.Model):
    ingredient = models.ForeignKey(ChecklistIngredient, verbose_name='Ingredient', blank=True, null=True)
    item = models.ForeignKey(ChecklistItem, verbose_name='Item', blank=True, null=True)

    def __unicode__(self):
        if self.ingredient:
            return str(self.ingredient)
        if self.item:
            return str(self.item)
        return None
