# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ExamResults(models.Model):
    id = models.BigIntegerField(primary_key=True)
    sbd = models.BigIntegerField()
    literature = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    math = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    language_score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    physic = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    chemistry = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    biology = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    history = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    geography = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    civic = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exam_results'
