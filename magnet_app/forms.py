from django import forms
from .models import Dataset
import pytest

@pytest.mark.django_db
class UserForm(forms.Form):

    # radio button to ask whether the user is submitting one or multiple query gene lists
    one_or_multiple = forms.ChoiceField(label='',
                                        choices=[('One', 'One'),
                                                 ('Multiple', 'Multiple'),
                                                 ("Example", "Example")],
                                        widget=forms.RadioSelect, required=True)

    # text area for pasting a single query gene list
    user_genes = forms.CharField(label='Gene List:',
                                 required=False,
                                 widget=forms.Textarea(attrs={'placeholder': 'Enter your list of query genes here',
                                                              'rows': 4, 'cols': 15}))

    # file upload for query gene lists
    user_genes_upload = forms.FileField(label="", required=False)

    # text area for pasting a background gene list
    user_background = forms.CharField(label='Background:',
                                      required=False,
                                      widget=forms.Textarea(attrs={'placeholder': 'Enter your list of background genes here',
                                                                   'rows': 4,
                                                                   'cols': 15}))

    # file upload for the background gene list
    user_background_upload = forms.FileField(label="", required=False)

    # radio button for background processing modes
    background_calc = forms.ChoiceField(label='',
                                        choices=[('Intersect', 'Intersect'), ("User", 'User')],
                                        widget=forms.RadioSelect, required=True)

    # checkboxes for datasets to include
    dataset_choices = [(dataset.id, str(dataset)) for dataset in Dataset.objects.all()]
    #dataset_choices = []
    user_selected_datasets = forms.MultipleChoiceField(choices=dataset_choices,
                                                    label='Include the following datasets from the database :',
                                                    required=False,
                                                    error_messages={'required': 'Please select at least one dataset!'},
                                                    widget=forms.CheckboxSelectMultiple)

    # file upload for user custom datasets
    user_dataset_upload = forms.FileField(label="", required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))


    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        
        one_or_multiple = cleaned_data.get("one_or_multiple")
        user_genes_upload = cleaned_data.get("user_genes_upload")
        user_background_upload = cleaned_data.get("user_background_upload")
        user_genes = cleaned_data.get('user_genes')
        user_background = cleaned_data.get('user_background')
        user_selected_datasets = cleaned_data.get('user_selected_datasets')
        user_dataset_upload = cleaned_data.get('user_dataset_upload')

        if not user_genes and not user_genes_upload and one_or_multiple != "Example":
            raise forms.ValidationError('Please submit at least one query gene list!')
            
        if not user_background and not user_background_upload and one_or_multiple != "Example":
            raise forms.ValidationError('Please submit the background gene list!')

        if not user_selected_datasets and not user_dataset_upload:
            raise forms.ValidationError('Please select a dataset to test against or upload your own!')

        return self.cleaned_data
