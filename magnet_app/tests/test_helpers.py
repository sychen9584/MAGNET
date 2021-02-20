import mygene, collections, pytest
import magnet_app.helper as helper
from django.test import TestCase
from ..models import Gene, Dataset, Cluster, Annotation

class TestSymboltoEnsemblConversion:
    def setup(self):
        input_gene = ["H19", "NARF", "CAV2"]
        expected_list = ["ENSMUSG00000000031", "ENSMUSG00000000056", "ENSMUSG00000000058"]
        expected_result = {"H19": {"status": "mapped", 'ensembl': "ENSMUSG00000000031"},
        "NARF": {"status": "mapped", 'ensembl': "ENSMUSG00000000056"},
        "CAV2": {"status": "mapped", 'ensembl': "ENSMUSG00000000058"}}

        return([input_gene, expected_list, expected_result])

    def test_convert_success(self):
        
        input_gene, expected_list, expected_result = self.setup()

        mapped, unmapped, result= helper.convert_gene_symbol_to_ensembl(input_gene)
        assert mapped == expected_list
        assert unmapped == []
        assert result == expected_result
        

    def test_convert_fail(self):
        
        input_gene, expected_list, expected_result = self.setup()
        input_gene.append("abcd")
        expected_result["abcd"] = {'status': "unmapped", "ensembl": None}

        mapped, unmapped, result = helper.convert_gene_symbol_to_ensembl(input_gene)
        assert mapped == expected_list
        assert unmapped == ['abcd']
        assert result == expected_result

    def test_convert_unconverted(self):
        
        input_gene, expected_list, expected_result = self.setup()
        input_gene.append("ENSMUSG00000000266")
        expected_list.append("ENSMUSG00000000266")
        expected_result["ENSMUSG00000000266"] = {'status': "unconverted", "ensembl": 'ENSMUSG00000000266'}

        mapped, unmapped, result = helper.convert_gene_symbol_to_ensembl(input_gene)
        assert collections.Counter(mapped) == collections.Counter(expected_list)
        assert unmapped == []
        assert result == expected_result
    
    def test_full_ensembl_input(self):
        input_gene = ["ENSMUSG00000000120", "ENSMUSG00000000148", "ENSMUSG00000111685"]
        expected_list = ["ENSMUSG00000000120", "ENSMUSG00000000148", "ENSMUSG00000111685"]
        expected_result = {"ENSMUSG00000000120": {"status": "unconverted", 'ensembl': "ENSMUSG00000000120"},
        "ENSMUSG00000000148": {"status": "unconverted", 'ensembl': "ENSMUSG00000000148"},
        "ENSMUSG00000111685": {"status": "unconverted", 'ensembl': "ENSMUSG00000111685"}}

        mapped, unmapped, result = helper.convert_gene_symbol_to_ensembl(input_gene)
        assert collections.Counter(mapped) == collections.Counter(expected_list)
        assert unmapped == []
        assert result == expected_result

@pytest.mark.django_db
class TestGeneSearchFunction(TestCase):
    def setup(self):
        dataset = Dataset.objects.create(dataset_name="Lavin Et al. 2014")
        dataset.save()

        gene1 = Gene.objects.create(ensembl_id="ENSMUSG00000002111",gene_symbol="spi1")
        gene1.save()
        gene2 = Gene.objects.create(ensembl_id="ENSMUSG00000002112",gene_symbol="spi2")
        gene2.save()

        cluster1 = Cluster.objects.create(dataset=dataset, 
                                        cluster_number=1,
                                        cluster_description="test1")
        cluster1.save()
        cluster2 = Cluster.objects.create(dataset=dataset, 
                                        cluster_number=2,
                                        cluster_description="test2")
        cluster2.save()

        annotation1 = Annotation.objects.create(gene=gene1, cluster=cluster1)
        annotation1.save()
        annotation2 = Annotation.objects.create(gene=gene2, cluster=cluster2)
        annotation2.save()

        return (annotation1, annotation2)

    def test_search_genes_symbol(self):
        annotation1, annotation2 = self.setup()
        found_entries = helper.search_genes("Spi1")

        assert found_entries.count() == 1
        assert found_entries.first() == annotation1

    def test_search_genes_ensembl(self):
        annotation1, annotation2 = self.setup()
        found_entries = helper.search_genes("ENSMUSG00000002112")

        assert found_entries.count() == 1
        assert found_entries.first() == annotation2

    def test_search_genes_multiple_hits(self):
        annotation1, annotation2 = self.setup()
        found_entries = helper.search_genes("ENSMUSG0000000211 Spi1")

        assert found_entries.count() == 2
    
    def test_search_genes_no_hits(self):
        annotation1, annotation2 = self.setup()
        found_entries = helper.search_genes("ENSMUSG35235345233 Spi4")

        assert found_entries.count() == 0

