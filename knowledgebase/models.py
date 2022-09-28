from django.db import models

# Create your models here.


class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class Caste(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class District(models.Model):
    state = models.ForeignKey(State)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    capital = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Taluk(models.Model):
    district = models.ForeignKey(District)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# male, female, transgender
class Gender(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

# group of village is called as hobli as per google
class Hobli(models.Model):
    name = models.CharField(max_length=100)
    taluk = models.ForeignKey(Taluk)

    def __str__(self):
        return self.name


class Village(models.Model):
    hobli = models.ForeignKey(Hobli)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BloodGroup(models.Model):
    name = models.CharField(max_length=10)


class Bank(models.Model):
    name = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=30)
    micr_code = models.CharField(max_length=30, blank=True, null=True)








