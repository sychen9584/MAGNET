from django.contrib import admin
from .models import Gene, Dataset, Cluster, Annotation, Graph_edge
# Register your models here.
class GeneAdmin(admin.ModelAdmin):
    list_display = ('ensembl_id','gene_symbol')
    search_fields = ['ensembl_id','gene_symbol']
    ordering = ['ensembl_id']
class ClusterInline(admin.TabularInline):
    model = Cluster
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('dataset_name', 'journal')
    fieldsets = [
            (None, {'fields': ['dataset_name',
                               'full_title',
                               'authors',
                               'abstract',
                               'publication_year',
                               'journal',
                               'link_to_pubmed']
                    }),
    ]

    inlines = [ClusterInline]
    search_fields = ['dataset_name']

class AnnotationAdmin(admin.ModelAdmin):
    search_fields = ['gene']


class GraphedgeAdmin(admin.ModelAdmin):
    search_fields = ['cluster']

admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Gene, GeneAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Graph_edge, AnnotationAdmin)