from django.db import models
from django.contrib.postgres.fields.jsonb import JSONField

# Create your models here.
class Gene(models.Model):
    """
    Stores gene entities from ensembl gtf file
    Contains two fields:
        ensembl_id
        gene_symbol

    """

    ensembl_id = models.CharField(max_length=50, unique=True)
    gene_symbol = models.CharField(max_length=50)
    
    class Meta:
        indexes = [ models.Index(fields=['ensembl_id']),
                    models.Index(fields=['gene_symbol']),]
        verbose_name_plural = "genes"

    def __str__(self):
        return self.gene_symbol + "/" + self.ensembl_id

class Dataset(models.Model):
    """
    Stores meta info of the datasets, associates with clusters

    """
    dataset_name = models.CharField(max_length=200, unique=True)
    dataset_type = models.CharField(max_length=200, blank=True)
    full_title = models.TextField(blank=True)
    authors = models.TextField(blank=True)
    publication_year = models.IntegerField(blank=True,null=True)
    journal = models.CharField(max_length=100, blank=True)
    link_to_pubmed = models.URLField(blank=True)
    abstract = models.TextField(blank=True)
    
    class Meta:
        ordering = ["dataset_name"]

    def __str__(self):
        return self.dataset_type + " (" + self.dataset_name + ")"

    def get_clusters(self):
        clusters = self.cluster_set.all()

        # get number of genes associated with each cluster
        cluster_gene_num = {c:c.annotation_set.count() for c in clusters}
        # get total number of genes for a dataset
        total_gene_num = sum(cluster_gene_num.values())
        
        return [cluster_gene_num, total_gene_num]



class Cluster(models.Model):

    """
    Stores cluster entities, child table of Dataset

    """
    # child table of Dataset
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    cluster_number = models.IntegerField()
    cluster_description = models.CharField(max_length=500, blank=True)

    class Meta:
        indexes = [ models.Index(fields=['cluster_description']),]
        ordering = ["cluster_number"]

    def __str__(self):
        return self.cluster_description + " (" + str(self.cluster_number) + ")"


class Annotation(models.Model):

    """
    Stores annotation entities, each entry is associated with a gene and a cluster entity

    """    

    # links a Cluster to a Gene
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)

    class Meta:
        indexes = [ models.Index(fields=['cluster','gene']),]
        unique_together = ['cluster','gene']
    
    def __str__(self):
        return '{} --- {} --- {}'.format(
            str(self.gene),
            str(self.cluster.dataset),
            str(self.cluster)
        )

class Graph_edge(models.Model):

    """
    Stores proportion of genes shared between clusters, each entry is associated with a pair of cluster"

    """    

    # links a Cluster to a Gene
    cluster1 = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name="cluster1")
    cluster2 = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name="cluster2")

    proportion = models.FloatField()
    overlap_num = models.IntegerField(blank=True)
    
    def __str__(self):
        return '{} --- {} --- {}'.format(
            str(self.cluster1),
            str(self.cluster2),
            str(self.proportion)
        )

class ExampleData(models.Model):
    '''
    Store Koch et al. 2018 clusters as example

    '''
    name = models.CharField(max_length=50, unique=True)
    gene_list = JSONField()
    background = JSONField()

    def __str__(self):
        return self.name
