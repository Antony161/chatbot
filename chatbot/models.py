from django.db import models
from django.contrib.auth.models import User



# Create your models here.
class Chat(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    message=models.TextField()
    response=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username}:{self.message}"
    

class UploadedDocument(models.Model):
    file = models.FileField(upload_to='')  # This specifies where the file is stored. An empty string means it's stored in 'uploaded_documents/'
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Automatically adds the upload date and time when a file is uploaded.

    def __str__(self):
        return self.file.name  # For easy representation, display the file name
