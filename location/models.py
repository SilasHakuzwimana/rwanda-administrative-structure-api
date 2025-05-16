from django.db import models

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
class Province(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    # Add a unique constraint to ensure that the combination of name and country is unique
    class Meta:
        unique_together = ('name', 'country')
        #Optional: Add ordering to the model
        ordering = ['name']
    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    # Add a unique constraint to ensure that the combination of name and province is unique
    # This will ensure that no two districts can have the same name within the same province
    class Meta:
        
        # Add a unique constraint to ensure that the combination of name and province is unique
        # This will ensure that no two districts can have the same name within the same province
        
        unique_together = ('name', 'province')
        #Optional: Add ordering to the model
        # This will ensure that the districts are ordered by name when queried
        # This is optional, but it can be useful for displaying the districts in a specific order
        ordering = ['name']
    def __str__(self):
        return self.name

class Sector(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'district')
        #Optional: Add ordering to the model
        ordering = ['name']
    def __str__(self):
        return self.name

class Cell(models.Model):
    name = models.CharField(max_length=100)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'sector')
        #Optional: Add ordering to the model
        ordering = ['name']
    def __str__(self):  
        return self.name
        

class Village(models.Model):
    name = models.CharField(max_length=100)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'cell')
        #Optional: Add ordering to the model
        ordering = ['name']
    def __str__(self):
        return self.name
