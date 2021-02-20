import pytest, sys, csv, io, os, yaml
from ..models import Gene, Dataset, Cluster, Annotation

path_to_module = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'management','commands'))
sys.path.insert(0, path_to_module)
import populate_genes as pg, add_dataset as ad

@pytest.mark.django_db
class TestPopulateGene:
    def make_temp_csv(self, header):
            self.table = [
                ['ensembl','gene_symbol'],
                ['ENSMUSG00000029580', 'Actb'],
                ['ENSMUSG00000064339', 'mt-Rnr2'],
                ['ENSMUSG00000049775','Tmsb4x'],
                ['ENSMUSG00000069516','Lyz2'],
                ['ENSMUSG00000064337','mt-Rnr1'],
                ['ENSMUSG00000092341','Malat1'],
                ['ENSMUSG00000073411','H2-D1'],
                ['ENSMUSG00000064341','mt-Nd1'],
                ['ENSMUSG00000064363','mt-Nd4'],
                ['ENSMUSG00000032562','Gnai2']]
            
            temp_csv = io.StringIO()
            temp_writer = csv.writer(temp_csv,delimiter=",")
            
            if not header:
                self.table = self.table[1:] # remove header
            
            temp_writer.writerows(self.table)

            return temp_csv

    def test_populate_gene_objects(self):
        temp_csv = self.make_temp_csv(header=True)

        temp_csv.seek(0)
        tmp = pg.Command()
        tmp.populate_genes(temp_csv)

        assert Gene.objects.count() == 10

        gene_1 = Gene.objects.get(ensembl_id="ENSMUSG00000029580")
        assert gene_1.gene_symbol == "actb"

        gene_6 = Gene.objects.get(ensembl_id="ENSMUSG00000092341")
        assert gene_6.gene_symbol == "malat1"
            
        gene_10 = Gene.objects.get(ensembl_id="ENSMUSG00000032562")
        assert gene_10.gene_symbol == "gnai2"


    def test_populate_gene_skipped_header(self,capsys):
        temp_csv = self.make_temp_csv(header=True)
        temp_csv.seek(0)
        tmp = pg.Command()
        tmp.populate_genes(temp_csv)
        captured = capsys.readouterr()  # Capture output
        assert "skipped header column" in captured.out

        temp_csv = self.make_temp_csv(header=False)
        temp_csv.seek(0)
        tmp = pg.Command()
        tmp.populate_genes(temp_csv)
        captured = capsys.readouterr()  # Capture output
        assert "skipped header column" not in captured.out

@pytest.mark.django_db
class TestAddDataset:
    def make_temp_yaml(self):
        metadata = {"dataset_name": "Lavin Et al. 2014",
        'full_title': "Tissue-resident Macrophage",
        'authors': 'Yonit Lavin, Deborah Winter',
        'publication_year': 2014,
        'journal': "Cell",
        'link_to_pubmed': "https://pubmed.ncbi.nlm.nih.gov/25480296/",
        'abstract': 'This is a test',
        'clusters': {1: "Microglia",
        2: "Kupffer cells & Spleen MΦ"}}

        temp_yaml = io.StringIO()
        yaml.dump(metadata,temp_yaml)
        return(temp_yaml)
        
    def make_temp_csv(self):
        self.table = [
                ['Symbols', 'Clusters'],
                ['CST3', 1],
                ['CX3CR1', 1],
                ['SELPLG', 1],
                ['TBXAS1', 2],
                ['CD79B', 2],
                ['TGTP2', 2]]
            
        temp_csv = io.StringIO()
        temp_writer = csv.writer(temp_csv,delimiter=",")
        temp_writer.writerows(self.table)
        return temp_csv

    def setup(self):
        temp_yaml = self.make_temp_yaml()
        temp_csv = self.make_temp_csv()
        temp_yaml.seek(0)
        temp_csv.seek(0)

        return [temp_csv, temp_yaml]

    def test_add_dataset_name(self):
        temp_csv, temp_yaml = self.setup()
        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        assert Dataset.objects.count() == 1
        dataset = Dataset.objects.get(dataset_name= "Lavin Et al. 2014")
        assert dataset.dataset_name == 'Lavin Et al. 2014'

    def test_add_dataset_full_title(self):
        temp_csv, temp_yaml = self.setup()
        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        dataset = Dataset.objects.get(dataset_name= "Lavin Et al. 2014")
        assert dataset.full_title == "Tissue-resident Macrophage"

    def test_add_dataset_authors(self):
        temp_csv, temp_yaml = self.setup()
        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        dataset = Dataset.objects.get(dataset_name= "Lavin Et al. 2014")
        assert dataset.authors == 'Yonit Lavin, Deborah Winter'

    def test_add_dataset_publication_year(self):
        temp_csv, temp_yaml = self.setup()
        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        dataset = Dataset.objects.get(dataset_name= "Lavin Et al. 2014")
        assert dataset.publication_year == 2014
    
    def test_add_dataset_journal(self):
        temp_csv, temp_yaml = self.setup()
        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        dataset = Dataset.objects.get(dataset_name= "Lavin Et al. 2014")
        assert dataset.journal == "Cell"
    
    def test_add_dataset_link_to_pubmed(self):
        temp_csv, temp_yaml = self.setup()
        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        dataset = Dataset.objects.get(dataset_name= "Lavin Et al. 2014")
        assert dataset.link_to_pubmed == "https://pubmed.ncbi.nlm.nih.gov/25480296/"
    
    def test_add_dataset_abstract(self):
        temp_csv, temp_yaml = self.setup()
        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        dataset = Dataset.objects.get(dataset_name= "Lavin Et al. 2014")
        assert dataset.abstract == 'This is a test'

    def test_add_dataset_cluster_number(self):
        temp_csv, temp_yaml = self.setup()
        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        assert Cluster.objects.count() == 2
        c1 = Cluster.objects.get(cluster_number= 1)
        assert c1.cluster_number == 1
        c2 = Cluster.objects.get(cluster_number= 2)
        assert c2.cluster_number == 2

    def test_add_dataset_cluster_description(self):
        temp_csv, temp_yaml = self.setup()
        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        c1 = Cluster.objects.get(cluster_number= 1)
        assert c1.cluster_description == "Microglia"
        c2 = Cluster.objects.get(cluster_number= 2)
        assert c2.cluster_description == "Kupffer cells & Spleen MΦ"

    def test_add_dataset_cluster__dataset(self):
        temp_csv, temp_yaml = self.setup()
        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        c1 = Cluster.objects.get(cluster_number= 1)
        assert c1.dataset.dataset_name == 'Lavin Et al. 2014'
        
    def test_add_dataset_annotation(self):
        temp_csv, temp_yaml = self.setup()

        # add gene objects for testing
        test_genes = [("ENSMUSG00000027447", "Cst3"),
        ("ENSMUSG00000052336", "Cx3cr1"),
        ("ENSMUSG00000048163", "Selplg"),
        ("ENSMUSG00000029925", "Tbxas1"),
        ("ENSMUSG00000040592", "Cd79b"),
        ("ENSMUSG00000078921", "Tgtp2")]

        for g in test_genes:
            gene = Gene(ensembl_id=g[0],
                        gene_symbol=g[1].lower())
            gene.save()

        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        assert Annotation.objects.count() == 5
        a2 = Annotation.objects.get(gene__gene_symbol = "cx3cr1",cluster__cluster_number = 1)
        assert a2.cluster.cluster_description == 'Microglia'
        assert a2.gene.ensembl_id == 'ENSMUSG00000052336'
        assert a2.cluster.dataset.dataset_name == 'Lavin Et al. 2014'

    def test_add_dataset_invalid_annotation(self):
        temp_csv, temp_yaml = self.setup()

        # write an extra invalid row to csv
        temp_writer = csv.writer(temp_csv,delimiter=",")
        temp_writer.writerow(["abcde","2"])
        temp_csv.seek(0)

        # add gene objects for testing
        test_genes = [("ENSMUSG00000027447", "Cst3"),
        ("ENSMUSG00000052336", "Cx3cr1"),
        ("ENSMUSG00000048163", "Selplg"),
        ("ENSMUSG00000029925", "Tbxas1"),
        ("ENSMUSG00000040592", "Cd79b"),
        ("ENSMUSG00000078921", "Tgtp2")]

        for g in test_genes:
            gene = Gene(ensembl_id=g[0],
                        gene_symbol=g[1].lower())
            gene.save()

        tmp = ad.Command()
        tmp.add_dataset(temp_csv,temp_yaml)

        assert Annotation.objects.count() == 5
        a2 = Annotation.objects.get(gene__gene_symbol = "cx3cr1",cluster__cluster_number = 1)
        assert a2.cluster.cluster_description == 'Microglia'
        assert a2.gene.ensembl_id == 'ENSMUSG00000052336'
        assert a2.cluster.dataset.dataset_name == 'Lavin Et al. 2014'
