import sys, os, itertools
from django.core.management.base import BaseCommand, CommandError
from magnet_app.models import Gene, Cluster, Annotation, Graph_edge
from django.db import transaction

class Command(BaseCommand):
    help = "compute degree of sharing between clusters"

    def handle(self, *args, **options):
        self.compute_graph_edges()
        self.stdout.write(self.style.SUCCESS("Operation completed!"))
            
    @transaction.atomic
    def compute_graph_edges(self):
        
        """compute degree of sharing between cluster pairs"""
        
        clusters = list(Cluster.objects.all().values_list('id',flat=True))
        cluster_pairs = list(itertools.combinations(clusters,2))
        for pair in cluster_pairs:

            cluster1_genes = Annotation.objects.filter(cluster__pk=pair[0]).values_list('gene',flat=True)
            cluster2_genes = Annotation.objects.filter(cluster__pk=pair[1]).values_list('gene',flat=True)
            overlap = cluster1_genes.intersection(cluster2_genes).count()

            similarity = overlap*2/(cluster1_genes.count()+cluster2_genes.count())

            if not Graph_edge.objects.filter(cluster1=Cluster.objects.get(id=pair[0]),
                                            cluster2=Cluster.objects.get(id=pair[1])).exists():
            
                edge_obj = Graph_edge(cluster1=Cluster.objects.get(id=pair[0]),
                                        cluster2=Cluster.objects.get(id=pair[1]),
                                        proportion = similarity, overlap_num=overlap)
                edge_obj.save()
                
            else:
                edge_obj = Graph_edge.objects.get(cluster1=Cluster.objects.get(id=pair[0]),
                                                    cluster2=Cluster.objects.get(id=pair[1]))
                edge_obj.overlap_num = overlap
                edge_obj.save()
            
            print(str(edge_obj))
            