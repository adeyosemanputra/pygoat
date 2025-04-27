from django.db import models

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    comment = models.CharField(max_length=600)

    def __str__(self):
        return f"{self.name}: {self.comment}" 