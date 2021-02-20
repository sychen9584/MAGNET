import pytest
from django.test import TestCase, Client
#from magnet_app.forms import *   # import all forms
from magnet_app.models import Gene, Dataset, Cluster, Annotation

# Create your tests here.
@pytest.mark.django_db
class IndexViewTest(TestCase):
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/index')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/index')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'magnet_app/index.html')

@pytest.mark.django_db
class DatasetInfoViewTest(TestCase):

    def setup(self):
        dataset = Dataset.objects.create(dataset_name="Lavin Et al. 2014")
        dataset.save()
        return dataset.id

    def test_view_url_exists_at_desired_location(self):
        dataset_id = self.setup()
        response = self.client.get('/dataset/'+ str(dataset_id)+'/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        dataset_id = self.setup()
        response = self.client.get('/dataset/'+ str(dataset_id)+'/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'magnet_app/dataset_info.html')

class DocumentationViewTest(TestCase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/documentation')
        self.assertEqual(response.status_code, 301)

    def test_view_uses_correct_template(self):
        response = self.client.get('/documentation')
        self.assertEqual(response.status_code, 301)
        self.assertTemplateUsed(response, 'magnet_app/documentation.html')

class GeneSearchViewTest(TestCase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/search')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/search')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'magnet_app/search.html')
