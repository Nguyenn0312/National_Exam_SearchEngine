from django.db import models

class ExamResult(models.Model):
    # sbd is your identifier from the screenshot
    sbd = models.BigIntegerField(unique=True, db_index=True)
    literature = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    math = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    language_code = models.CharField(max_length=10, null=True)
    language_score = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    physic = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    # Add your other fields here: chemistry, biology, history, geography, civic
    chemistry = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    biology = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    history = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    geography = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    civic = models.DecimalField(max_digits=4, decimal_places=2, null=True)

    class Meta:
        db_table = 'exam_results'  # MUST match your MySQL table name exactly
        managed = False            # Tells Django NOT to try and modify your table

    def __str__(self):
        return f"Student {self.sbd}"