# Create your tasks here
from __future__ import absolute_import, unicode_literals

from django.db import connection
from django.db.models import Q
import mygene, json, itertools
import scipy.stats as sp
import statsmodels.sandbox.stats.multicomp as mt
import pandas as pd
from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .models import Gene, Dataset, Cluster, Annotation
import magnet_app.helper as helper

import time

progress_recorder = None
progress = None
total = None


@shared_task(bind=True)
def task_wrapper(self, user_data):
    '''Overall wrapper for celery task'''

    global progress_recorder, progress, total
    progress_recorder = ProgressRecorder(self)
    progress = 0
    
    user_genes, user_background, user_choices, background_calc , user_dataset = user_data
    print(user_genes)
    total = len(user_genes)*4 + 3
    progress_recorder.set_progress(0, total, description="Initiating.....{}/{}".format(progress, total))
    print("Initiating....")
    
    
    hg_output = hypergeom_wrapper(user_genes, user_background, 
                                user_choices, background_calc, user_dataset, total)
    
    results = hg_output['results']
    missed_genes =  hg_output['missed_genes']
    missed_background = hg_output['missed_background']
    matched_num = [hg_output['matched_gene_num'], hg_output['matched_bg_num']]
    user_results = hg_output['user_results']
    user_missed_genes= hg_output['user_missed_genes']
    user_matched_num = hg_output['user_matched_gene_num']

    
    # get total number of genes the user submitted
    gene_num = list(user_genes.values()) 
    gene_num = len([e for sublist in gene_num for e in sublist])
    orig_num = [gene_num, len(user_background)]
    
    # update progress bar
    progress = hg_output['progress']+1
    progress_recorder.set_progress(progress, total, description="Compiling final results......{}/{}".format(progress, total))
    print("Compiling final results......{}/{}".format(progress, total))

    context = {'dataset_dict': results, 'user_dataset_dict': user_results,
               'missed_genes': missed_genes, 'missed_background': missed_background,
               'matched_num': matched_num,'orig_num':orig_num,  
               'user_missed_genes':user_missed_genes, 'user_matched_num': user_matched_num}

    progress_recorder.set_progress(total, total, description="Done!")
    print("Done!")
    
    return [context]


def hypergeom_wrapper(user_genes, user_background,
                   user_choices, background_calc, user_dataset, total):

    ''' wrapper for hypergeometric function ''' 

    results = []
    user_results = []
    missed_genes = {}
    user_missed_genes = {}
    matched_gene_num = 0
    user_matched_gene_num = {}
    
    background_query = Gene.objects.filter(Q(ensembl_id__in=user_background)|Q(gene_symbol__in=user_background))
    background_query_list = list(background_query.values_list('ensembl_id', 'gene_symbol'))
    background_query_vals = list(background_query.values_list("id",flat=True))

    db_matched_bg = list(itertools.chain(*background_query_list))
    missed_background = [x.capitalize() for x in user_background if x not in db_matched_bg]

    progress = 1
    progress_recorder.set_progress(1, total, description="Counted missed genes....{}/{}".format(progress, total))
    print("Counted missed background genes")
    
    
    datasets = Dataset.objects.filter(pk__in=user_choices) # get user selected datasets
    clusters = Cluster.objects.filter(dataset__in=datasets).prefetch_related('dataset') # get all associated clusters

    for user_cluster in user_genes:
        
        user_query = Gene.objects.filter(Q(ensembl_id__in=user_genes[user_cluster])|Q(gene_symbol__in=user_genes[user_cluster]))
        user_query_list = user_query.values_list('ensembl_id', 'gene_symbol')
        user_query_vals = list(user_query.values_list('id',flat=True))

        # get missed genes
        db_matched_g = list(itertools.chain(*user_query_list))
        # flatten ensembl ID and gene ID
        db_nomatch_g = [x.capitalize() for x in user_genes[user_cluster] if x not in db_matched_g]
        missed_genes[user_cluster] = db_nomatch_g
        
        user_genes_set = [gene[0] for gene in user_query_list]
        matched_gene_num = matched_gene_num + len(user_query_list)

        #### run hypergeometric tests against user uploaded custom datasets
        for user_dataset_name, user_dataset_content in user_dataset.items():
            uhr, umg, umgn = user_dataset_hypergeom(user_query, 
                        background_query, user_cluster, 
                        user_dataset_name, user_dataset_content, 
                        background_calc)
            user_results.extend(uhr)
            user_missed_genes[user_dataset_name] = umg
            user_matched_gene_num[user_dataset_name] = umgn
        
        progress += 1
        progress_recorder.set_progress(progress, total ,description="Computed dataset params...{}/{}".format(progress, total))
        print("computed user uploaded dataset params...{}/{}".format(progress, total))

        dataset_params = [ get_dataset_params(user_query_vals, background_query_vals, dataset, background_calc)
                          for dataset in datasets]
        progress += 1
        progress_recorder.set_progress(progress, total ,description="Computed dataset params...{}/{}".format(progress, total))
        print("computed MAGNET dataset params...{}/{}".format(progress, total))
        
        t0 = time.time()
        cluster_params = [ get_cluster_params(user_query_vals, background_query_vals, cluster)
                          for cluster in clusters.iterator()]
        t1 = time.time()
        print(t1-t0)
        progress += 1
        progress_recorder.set_progress(progress, total, description="Computed cluster params...{}/{}".format(progress, total))
        print("computed cluster params...{}/{}".format(progress, total))
        
        
        hypergeom_results = compute_hypergeom(dataset_params, cluster_params, user_cluster)
        results.extend(hypergeom_results)
        
        progress += 1
        progress_recorder.set_progress(progress, total, description="Compiled hypergeom test results...{}/{}".format(progress, total))
        print("compiled hypergeom test results...{}/{}".format(progress, total))
    
    combined_results = results + user_results
    pvals = [r['pval'] for r in combined_results]
    adjusted_pvals = mt.multipletests(pvals, method="fdr_bh")[1]

    for r, p in zip(combined_results, adjusted_pvals):
        r['adjusted_pval'] = p

        if r['pval'] <= 0.05:
            r['color'] = 1
        elif r['pval'] >= 0.95:
            r['color'] = -1
        else:
            r['color'] = 0

    results = [r for r in combined_results if "cluster_description" in r]
    user_results = [r for r in combined_results if "cluster_description" not in r]
    return {'results': results, 'missed_genes': missed_genes,
            'missed_background': missed_background,
            'matched_gene_num': matched_gene_num,
            'matched_bg_num': len(background_query_list),
            'progress': progress, 
            'user_results': user_results, 
            'user_missed_genes': user_missed_genes,
            'user_matched_gene_num': user_matched_gene_num}


def get_dataset_params(user_query, background_query, dataset, background_calc):
    
    '''Calculate and return dataset-specific parameters for hypergeometric tests'''

    if background_calc == "Intersect": 
        N = Annotation.objects.filter(gene__in=background_query, cluster__dataset_id=dataset.id).count()
        n = Annotation.objects.filter(gene__in=user_query, cluster__dataset_id=dataset.id).count()
    else:
        N = len(background_query)
        n = len(user_query)
    
    params = {'N': N, 'n': n, 
                'dataset_name': dataset.dataset_name,
                'dataset_id': dataset.id,
                'dataset_type': dataset.dataset_type}
    
    return params

def get_cluster_params(user_query, background_query, cluster):

    '''Calculate and return cluster-specific parameters for hypergeometric tests'''
    
    K = Annotation.objects.filter(cluster_id=cluster.id, gene__in=background_query).count()
    overlap_genes = list(Annotation.objects.filter(cluster_id=cluster.id, gene__in=user_query).values_list('gene__gene_symbol', flat=True))
    k = len(overlap_genes)
    
    params = {'K': K, 'k': k, 'overlap_genes': overlap_genes,
              'cluster_id': cluster.id,
              'cluster_number': cluster.cluster_number,
              'cluster_name': cluster.cluster_description,
              'cluster_description': str(cluster),
              'dataset_name': cluster.dataset.dataset_name}
    
    return params


def compute_hypergeom(dataset_params, cluster_params, user_cluster):
    
    ''' Function for performing hypergeometric tests using previously retrieved 
        dataset and cluster-specific parameters'''

    # compile dataset and cluster paramters
    compiled_params = [{**cluster_entry, **dataset_entry}
                        for cluster_entry in cluster_params
                        for dataset_entry in dataset_params
                        if cluster_entry['dataset_name'] == dataset_entry['dataset_name']]
    
    results = []
    
    for entry in compiled_params:
        if entry['k'] == 0:
            pval = 1
        else:
            pval = sp.hypergeom.sf(entry['k'], entry['N'], entry['n'], entry['K'])
        
        
        r = {'user_cluster': user_cluster,
            'pval': pval, 
            'parameters': {'N': entry['N'], 'B': entry['K'], 
                            'n': entry['n'], 'b': entry['k']}, 
            'overlap_genes': entry['overlap_genes'],
            'dataset_id': entry['dataset_id'],
            'dataset_name': entry['dataset_name'],
            'dataset_type': entry['dataset_type'],
            'cluster_id': entry['cluster_id'],
            'cluster_number': entry['cluster_number'],
            'cluster_name': entry['cluster_name'],
            'cluster_description': entry['cluster_description']
            }

        results.append(r)
        
    return results

def user_dataset_hypergeom(user_query, background_query, user_cluster,
                        user_dataset_name, user_dataset_content, background_calc):
    # search for gene objects in database
    user_dataset_background = list(itertools.chain.from_iterable(user_dataset_content.values()))
    user_dataset_background_q = Gene.objects.filter(Q(ensembl_id__in=user_dataset_background)|Q(gene_symbol__in=user_dataset_background))

    # count missed genes
    user_dataset_background_l = list(user_dataset_background_q.values_list('ensembl_id', 'gene_symbol'))
    db_matched = list(itertools.chain(*user_dataset_background_l))
    missed_genes = [x.capitalize() for x in user_dataset_background if x not in db_matched]
    matched_gene_nums = [len(user_dataset_background), len(user_dataset_background_l)]
    
    results = []

    if background_calc == "Intersect":
        N = background_query.intersection(user_dataset_background_q).count()
        n = user_query.intersection(user_dataset_background_q).count()
    else:
        N = background_query.count()
        n = user_query.count()

    for dataset_cluster, genes in user_dataset_content.items():

        user_dataset_cluster_q = user_dataset_background_q.filter(Q(ensembl_id__in=genes)|Q(gene_symbol__in=genes))

        K = background_query.intersection(user_dataset_cluster_q).count()
        k = user_query.intersection(user_dataset_cluster_q)

        overlap_genes = list(k.values_list('gene_symbol',flat=True))
        k = len(overlap_genes)
        
        ## hypergeometric test
        if k == 0:
            pval = 1
        else:
            pval = sp.hypergeom.sf(k, N, n, K)

        r = {'user_cluster': user_cluster,
            'pval': pval, 
            'parameters': {'N': N, 'B': K, 
                            'n': n, 'b': k}, 
            'overlap_genes': overlap_genes,
            'dataset_name': user_dataset_name,
            'cluster_number': dataset_cluster
            }

        results.append(r)

    return([results, missed_genes, matched_gene_nums])
