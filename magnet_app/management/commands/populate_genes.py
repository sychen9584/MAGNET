import csv, sys, os
from django.core.management.base import BaseCommand, CommandError
from magnet_app.models import Gene
from django.db import transaction

class Command(BaseCommand):
    help = "populate genes in database"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", help='csv file that contains gene and cluster information')
    
    def handle(self, *args, **options):
        with open(options["csv_file"]) as f:
            self.populate_genes(f)
            self.stdout.write(self.style.SUCCESS("Operation completed!"))

    @transaction.atomic
    def populate_genes(self,f):
        """Function to add gene objects to database
        
        Arguments:
            f {file} -- csv file object (not path) containing two columns:
                        ensembl_id
                        gene_symbol
        """
        reader=csv.reader(f,delimiter=",")
        for ensembl, symbol in reader:
            if not ensembl.startswith("ENSMUSG"):
                print("skipped header column")
            else:
                # create gene entries if they do not exist
                if not Gene.objects.filter(ensembl_id=ensembl).exists():
                    gene = Gene(ensembl_id=ensembl,
                                gene_symbol=symbol.upper())
                    gene.save()
                else:
                    gene = Gene.objects.get(ensembl_id=ensembl)
                    gene.gene_symbol = gene.gene_symbol.upper()
                    gene.save()
                        
            print(ensembl + "/" + symbol)
                    
        

    