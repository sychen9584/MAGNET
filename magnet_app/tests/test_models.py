import pytest, csv, io, os
from django.test import TestCase
from ..models import Gene, Dataset, Cluster, Annotation

# Create your tests here.

@pytest.mark.django_db
class TestGeneModel:

    def test_gene_str(self):
        gene = Gene.objects.create(ensembl_id="ENSMUSG00000002111",gene_symbol="spi1")
        assert str(gene) == "spi1/ENSMUSG00000002111"

    def test_verbose_name_plural(self):
        assert str(Gene._meta.verbose_name_plural) == "genes"


@pytest.mark.django_db
class TestDatasetModel:

    def test_dataset_str(self):
        dataset = Dataset.objects.create(dataset_name="Lavin Et al. 2014")
        assert str(dataset) == "Lavin Et al. 2014"
    
    def test_get_clusters(self):
        gene1 = Gene.objects.create(ensembl_id="ENSMUSG00000002111",gene_symbol="spi1")
        gene2 = Gene.objects.create(ensembl_id="ENSMUSG00000002112",gene_symbol="spi2")
        
        dataset = Dataset.objects.create(dataset_name="Lavin Et al. 2014")
        
        cluster1 = Cluster.objects.create(dataset=dataset, 
                                        cluster_number=1,
                                        cluster_description="test1")
        cluster2 = Cluster.objects.create(dataset=dataset, 
                                        cluster_number=2,
                                        cluster_description="test2")
        
        annotation1 = Annotation.objects.create(gene=gene1, cluster=cluster1)
        annotation2 = Annotation.objects.create(gene=gene2, cluster=cluster2)
        
        cluster_gene_num, total_gene_num = dataset.get_clusters()

        assert list(cluster_gene_num)[0] == cluster1
        assert list(cluster_gene_num.values())[0] == 1
        assert total_gene_num == 2

@pytest.mark.django_db
class TestClusterModel:

    def test_cluster_str(self):
        dataset = Dataset.objects.create(dataset_name="Lavin Et al. 2014")
        cluster= Cluster.objects.create(dataset=dataset, 
                                        cluster_number=1,
                                        cluster_description="test")
        assert str(cluster) == "test (1)"
        
@pytest.mark.django_db
class TestAnnotationModel:

    def test_gene_str(self):
        gene = Gene.objects.create(ensembl_id="ENSMUSG00000002111",gene_symbol="spi1")
        dataset = Dataset.objects.create(dataset_name="Lavin Et al. 2014")
        cluster = Cluster.objects.create(dataset=dataset, 
                                        cluster_number=1,
                                        cluster_description="test")
        annotation = Annotation.objects.create(gene=gene, cluster=cluster)

        assert str(annotation) == "spi1/ENSMUSG00000002111 --- Lavin Et al. 2014 --- test (1)"