from django import forms
from .models import UploadedDocument

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedDocument  # Specify the model associated with this form
        fields = ['file']  # Only include the file field from the model
