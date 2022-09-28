from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UnitCv(models.Model):
    name = models.CharField(max_length=100)


class YieldEstimationTypeCv(models.Model):
    name = models.CharField(max_length=100)

    # plantation, individual


class YieldFormulaCv(models.Model):
    name = models.CharField(max_length=100)
    formula = models.CharField(max_length=100)

    # Quadratic, # straight line

class CloneYieldEstimationTypeMap(models.Model):
    clone = models.ForeignKey('main.Clone', on_delete=models.CASCADE)
    yield_estimation_type = models.ForeignKey(YieldEstimationTypeCv, on_delete=models.CASCADE)
    yield_formula = models.ForeignKey(YieldFormulaCv, on_delete=models.CASCADE)
    sample_percentage = models.DecimalField(max_digits=10, decimal_places=3)

class PlantationYield(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farmer_user')
    population = models.PositiveIntegerField() #number of trees
    clone = models.ForeignKey(CloneYieldEstimationTypeMap, on_delete=models.CASCADE)
    date_of_planting = models.DateField(blank=True, null=True)
    number_of_trees_to_sample = models.PositiveIntegerField()
    area_in_acre = models.DecimalField(max_digits=10, decimal_places=3)
    estimated_yield = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    actual_yield = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True) # y
    yield_unit = models.ForeignKey(UnitCv, on_delete=models.CASCADE)
    estimated_on = models.DateTimeField()
    estimated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='estimated_by')
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PlantationSample(models.Model):
    plantation_yield = models.ForeignKey(PlantationYield, on_delete=models.CASCADE)
    nth_sample = models.PositiveIntegerField() #example - 1st, 2nd
    girth = models.DecimalField(max_digits=10, decimal_places=5) 
    girth_unit = models.ForeignKey(UnitCv, on_delete=models.CASCADE)
    calculated_yield = models.DecimalField(max_digits=10, decimal_places=5)
    formula_used = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class YieldFormula(models.Model):
    yield_formula = models.ForeignKey(YieldFormulaCv, on_delete=models.CASCADE)
    clone = models.ForeignKey(CloneYieldEstimationTypeMap, on_delete=models.CASCADE)
    yield_estimation_type = models.ForeignKey(YieldEstimationTypeCv, on_delete=models.CASCADE)
    constant = models.CharField(max_length=100)
    constant_value = models.DecimalField(max_digits=12, decimal_places=7)
    constant_ordinal = models.PositiveIntegerField(default=1)
    user_created = models.ForeignKey(User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class IndividualYield(models.Model):
    population = models.PositiveIntegerField(default=1) #number of trees - default 1
    clone = models.ForeignKey(CloneYieldEstimationTypeMap, on_delete=models.CASCADE)
    girth = models.DecimalField(max_digits=10, decimal_places=5) 
    girth_unit = models.ForeignKey(UnitCv, on_delete=models.CASCADE, related_name='girth_unit')
    estimated_yield = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    yield_unit = models.ForeignKey(UnitCv, on_delete=models.CASCADE, related_name='yield_unit')
    estimated_on = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



