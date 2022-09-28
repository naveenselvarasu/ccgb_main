from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, unique=True)

    def __unicode__(self):
        return str(self.name)


class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)

    def __str__(self):
        return str(self.name)


class State(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    capital = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Taluk(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Block(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class RevenueVillage(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Village(models.Model):
    revenue_village = models.ForeignKey(RevenueVillage, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Pincode(models.Model):
    taluk = models.ForeignKey(Taluk, on_delete=models.CASCADE)
    value = models.PositiveIntegerField()

    def __str__(self):
        return '{} - {}'.format(self.taluk.name, self.value)


class InstanceLanguage(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)