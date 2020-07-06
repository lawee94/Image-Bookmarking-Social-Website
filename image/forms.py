from django import forms
from .models import Image
from django.utils.text import slugify
from urllib import request
from django.core.files.base import ContentFile

class ImageCreationForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        widgets = { 
            'url': forms.HiddenInput,  
            'title': forms.TextInput(attrs={'placeholder': 'Image Title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description' })
            }

    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extention = ['jpeg', 'jpg', 'png']
        extention = url.rsplit('.', 1)[1].lower()
        if extention not in valid_extention:
            raise forms.ValidationError('The given image doesn\'t match a valid image extention')
        return url
    
    def save(self, force_insert=False, force_update=False, commit=True):
        image = super(ImageCreationForm, self).save(commit=False)
        image_url = self.cleaned_data['url']
        image_name = '{}.{}'.format(slugify(image.title), image_url.rsplit('.', 1)[1].lower())
        
        #Download image froma agive url
        response = request.urlopen(image_url)
        image.image.save(image_name, ContentFile(response.read()), save=False)

        if commit:
            image.save()
        return image