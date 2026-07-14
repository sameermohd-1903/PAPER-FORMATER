from django.db import models


class Program(models.Model):

    LEVEL_CHOICES = (
        ('UG', 'Under Graduate'),
        ('PG', 'Post Graduate'),
    )

    level = models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES
    )

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return f"{self.level} - {self.name}"


class Semester(models.Model):

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE
    )

    number = models.IntegerField()

    def __str__(self):
        return f"{self.program.name} - Semester {self.number}"


class Subject(models.Model):

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        default=1
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE
    )
    

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name