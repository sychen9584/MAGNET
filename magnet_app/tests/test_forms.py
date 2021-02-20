import pytest
from django.test import TestCase
#from ..forms import UserForm

'''
@pytest.mark.django_db
class UserFormTests(TestCase):

    def test_no_user_genes_and_user_genes_upload(self):
        
        form = UserForm(data={"one_or_multiple": "multiple",
                                "user_genes": None,
                                "user_genes_upload": None,
                                "user_background": "Placeholder",
                                "user_background_upload": "Placeholder",
                                "user_selected_datasets": "Placeholder"})

        self.assertEqual(
            form.errors, ["Please submit at least one query gene list!"]
        )

    def test_no_user_background_and_user_background_upload(self):
        
        form = UserForm(data={"one_or_multiple": "multiple",
                                "user_genes": "Placeholder",
                                "user_genes_upload": "Placeholder",
                                "user_background": None,
                                "user_background_upload": None,
                                "user_selected_datasets": "Placeholder"})

        self.assertEqual(
            form.errors, ["Plaase submit the background gene list!"]
        )
   '''