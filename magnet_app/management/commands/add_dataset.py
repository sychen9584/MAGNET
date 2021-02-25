import csv, sys, os, yaml
from django.core.management.base import BaseCommand, CommandError
from magnet_app.models import Gene, Dataset, Cluster, Annotation
from django.db import transaction
from django.db.models import Q
import magnet_app.helper as hp
import pandas as pd

class Command(BaseCommand):
    help = "add dataset, clusters, and annotations to dataabase"

    def add_arguments(self, parser):
        parser.add_argument("dir_name", help='directory name that contains csv and yaml files for dataset')
    
    def handle(self, *args, **options):
        path_to_csv = os.path.join(options["dir_name"], "clusters.csv")
        path_to_yaml = os.path.join(options["dir_name"], "metadata.yaml")
        with open(path_to_csv) as csv_file, open(path_to_yaml) as yaml_file:
            self.add_dataset(csv_file, yaml_file)
        self.stdout.write(self.style.SUCCESS("Dataset added!"))

    @transaction.atomic
    def add_dataset(self, csv_file, yaml_file):
        """Function to add datasets, clusters, and annotations object to database
        
        Arguments:
            csv_file {file} -- csv file object (not path) containing two columns of:
                        gene ids
                        cluster numbers
            yaml_file {file} -- yaml file object (not path) containing meta data for the dataset
        """

        # parse yaml file and add dataset object
        metadata = yaml.full_load(yaml_file)
        if not Dataset.objects.filter(dataset_name=metadata["dataset_name"]).exists():
            dataset = Dataset(dataset_name=metadata["dataset_name"],
            full_title=metadata["full_title"],
            authors=metadata["authors"],
            publication_year=metadata["publication_year"],
            journal=metadata["journal"],
            link_to_pubmed=metadata["link_to_pubmed"],
            abstract=metadata["abstract"])

            dataset.save()

            # parse yaml file and add cluster objects
            cluster_dict = metadata["clusters"]
            for cluster_num, cluster_desc in cluster_dict.items():
                cluster = Cluster(cluster_number = cluster_num,
                cluster_description = cluster_desc, dataset=dataset)

                cluster.save()

        else:
            raise Exception("Dataset already uploaded to database, delete first")
        # read in csv file to create annotation entries
        self._add_annotation(csv_file,dataset)

    def _add_annotation(self, csv_file, dataset):
        """sub-function to parse csv file and add annotation objects to database
        
        Arguments:
            csv_file {file} -- csv file object (not path) containing two columns of:
                        gene ids
                        cluster numbers
            dataset {django.model} -- dataset object created by add_dataset()
        """
        df = pd.read_csv(csv_file)

        # convert genes to ensembl ids
        genes = df.iloc[:,0].tolist()

        if genes[0].startswith("ENSMUSG"):
            df["ensembl"] = genes
        else:
            _, _, result = hp.convert_gene_symbol_to_ensembl(genes)
            mapped_genes, ensembl_ids = zip(*[(k, v["ensembl"]) for k, v in result.items() if v["status"]=="mapped"])
            df = df[df.iloc[:,0].isin(mapped_genes)] # keep converted rows
            df["ensembl"] = ensembl_ids
            
        for index, row in df.iterrows():

            print(row['ensembl'])
            
            if dataset.cluster_set.filter(cluster_number=row.iloc[1]).exists() and \
                Gene.objects.filter(ensembl_id=row['ensembl']).exists():
               
                cluster = dataset.cluster_set.get(cluster_number = row.iloc[1])
                gene = Gene.objects.get(ensembl_id=row['ensembl'])
               
                # create annotation
                annotation = Annotation(gene = gene, cluster = cluster)
                annotation.save()

            else:
                continue




            #print(index)
            #Gene.objects.filter(gene_symbol=row['Symbols'].upper()).exists():
            #gene = Gene.objects.get(gene_symbol=row['Symbols'].upper()