import csv, sys, os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from magnet_app.models import ExampleData
import magnet_app.helper as hp
import pandas as pd
import json

class Command(BaseCommand):
    help = "add example to database"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", help='csv file that contains example dataset')
    
    def handle(self, *args, **options):
        with open(options["csv_file"]) as f:
            self.add_example(f)
            self.stdout.write(self.style.SUCCESS("Operation completed!"))

    @transaction.atomic
    def add_example(self,f):
        """Function to add gene objects to database
        
        Arguments:
            f {file} -- csv file object (not path) containing two columns of:
                        gene ids
                        cluster numbers
        """
        df = pd.read_csv(f)

        # convert genes to ensembl ids
        genes = df.iloc[:,0].tolist()

        if genes[0].startswith("ENSMUSG"):
            df["ensembl"] = genes
        else:
            _, _, result = hp.convert_gene_symbol_to_ensembl(genes)
            mapped_genes, ensembl_ids = zip(*[(k, v["ensembl"]) for k, v in result.items() if v["status"]=="mapped"])
            df = df[df.iloc[:,0].isin(mapped_genes)] # keep converted rows
            df["ensembl"] = ensembl_ids

        background = df["ensembl"].tolist()

        df.list = [y for x, y in df.groupby('Cluster', as_index=False)]

        gene_list = {}
        for df in df.list:
            gene_list[df["Cluster"].tolist()[0]] = df["ensembl"].tolist()

        example_object = ExampleData(name="Koch et al. 2018", gene_list=gene_list, background=background)
        example_object.save()
        