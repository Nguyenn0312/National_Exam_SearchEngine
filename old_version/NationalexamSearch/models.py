from django.db import models

class ExamResult(models.Model):
    # sbd is identifier
    sbd = models.BigIntegerField(unique=True, db_index=True)
    literature = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    math = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    language_code = models.CharField(max_length=10, null=True)
    language_score = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    physic = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    chemistry = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    biology = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    history = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    geography = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    civic = models.DecimalField(max_digits=4, decimal_places=2, null=True)

    class Meta:
        db_table = 'exam_results'  
        managed = False          

    def __str__(self):
        return f"Student {self.sbd}"