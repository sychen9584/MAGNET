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
from django.db import connection

progress_recorder = None
progress = None
total = None


@shared_task(bind=True)
def task_wrapper(self, user_data):
    '''Overall wrapper for celery task'''

    global progress_recorder, progress, total
    progress_recorder = ProgressRecorder(self)
    
    user_genes, user_background, user_choices, background_calc , user_dataset = user_data
    
    hg_output = hypergeom_wrapper(user_genes, user_background, 
                                user_choices, background_calc, user_dataset)
    
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
    total = hg_output['total']
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
                   user_choices, background_calc, user_dataset):

    ''' wrapper for hypergeometric function ''' 

    results = []
    user_results = []
    missed_genes = {}
    user_missed_genes = {}
    matched_gene_num = 0
    user_matched_gene_num = {}
    user_query_ids = {}

    #### get associated datasets and clusters
    datasets = Dataset.objects.filter(pk__in=user_choices) # get user selected datasets
    clusters = Cluster.objects.filter(dataset__in=datasets).select_related('dataset') # get all associated clusters
    
    ##### initiate progress bar
    total = 7
    progress = 0
    progress_recorder.set_progress(0, total)
    print("Initiating....")

    ######## process user supplied background gene lists
    background_query = Gene.objects.filter(Q(ensembl_id__in=user_background)|Q(gene_symbol__in=user_background))
    background_query_list = list(background_query.values_list('id','ensembl_id', 'gene_symbol'))

    background_query_ids = [i[0] for i in background_query_list]
    #background_query_ids = background_query
    background_query_list = [i[1:] for i in background_query_list]

    db_matched_bg = list(itertools.chain(*background_query_list))
    missed_background = [x.capitalize() for x in user_background if x not in db_matched_bg]

    progress = 1
    progress_recorder.set_progress(1, total)
    print("processed user supplied background...{}/{}".format(progress, total))

    
    ##### process user supplied query gene lists
    for user_cluster in user_genes:
        user_query = Gene.objects.filter(Q(ensembl_id__in=user_genes[user_cluster])|Q(gene_symbol__in=user_genes[user_cluster]))
        user_query_list = user_query.values_list('id','ensembl_id', 'gene_symbol')

        user_query_ids[user_cluster] = [i[0] for i in user_query_list]
        #user_query_ids[user_cluster] = user_query
        user_query_list = [i[1:] for i in user_query_list]

        # get missed genes
        db_matched_g = list(itertools.chain(*user_query_list))
        # flatten ensembl ID and gene ID
        db_nomatch_g = [x.capitalize() for x in user_genes[user_cluster] if x not in db_matched_g]
        missed_genes[user_cluster] = db_nomatch_g
        matched_gene_num = matched_gene_num + len(user_query_list)

    progress += 1
    progress_recorder.set_progress(progress, total)
    print("processed user supplied query gene lists...{}/{}".format(progress, total))

    ####### calculate dataset parameters 
    dataset_params = [get_dataset_params(user_cluster, user_query_ids[user_cluster],
                                            background_query_ids, dataset, background_calc)
                        for dataset in datasets  for user_cluster in user_query_ids ]

    progress += 1
    progress_recorder.set_progress(progress, total)
    print("computed MAGNET dataset params...{}/{}".format(progress, total))
    
    
    ##### calculate cluster parameters
    cluster_params = [get_cluster_params(user_cluster, user_query_ids[user_cluster], 
                                            background_query_ids, cluster)
                      for cluster in clusters for user_cluster in user_query_ids]

    progress += 1
    progress_recorder.set_progress(progress, total)
    print("computed cluster params...{}/{}".format(progress, total))

    ##### perform hypergeometric tests for MAGNET datasets
    results = compute_hypergeom(dataset_params, cluster_params, False)
    
    progress += 1
    progress_recorder.set_progress(progress, total, description="Compiled hypergeom test results...{}/{}".format(progress, total))
    print("compiled hypergeom test results...{}/{}".format(progress, total))

    #### run hypergeometric tests against user uploaded custom datasets
    ####### iterate across user uploaded datasets
    user_dataset_params = []
    user_cluster_params = []
    for user_dataset_name, user_dataset_content in user_dataset.items():
        
        # process genes unrecognized by MAGNET for user uploaded datasets
        u_background_query, umg, umgn = user_compute_missed_genes(user_dataset_content)
        user_missed_genes[user_dataset_name] = umg
        user_matched_gene_num[user_dataset_name] = umgn

        # retrieve dataset specific parameters
        udp = [user_get_dataset_params(user_cluster, user_query_ids[user_cluster], background_query_ids,
                            user_dataset_name, u_background_query, background_calc) 
                            for user_cluster in user_query_ids]
        user_dataset_params.extend(udp)
        
        # retrive cluster specific parameters
        ucp = [user_get_cluster_params(user_cluster, user_query_ids[user_cluster],
                            background_query_ids, user_dataset_name,  
                            user_dataset_cluster, user_dataset_cluster_g)
                            for user_dataset_cluster, user_dataset_cluster_g in user_dataset_content.items()
                            for user_cluster in user_query_ids]
        user_cluster_params.extend(ucp)
        
    user_results = compute_hypergeom(user_dataset_params, user_cluster_params, True)

    progress += 1
    progress_recorder.set_progress(progress, total ,description="Computed dataset params...{}/{}".format(progress, total))
    print("performed hypergeometric test on user uploaded dataset...{}/{}".format(progress, total))

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
            'progress': progress, 'total': total,
            'user_results': user_results, 
            'user_missed_genes': user_missed_genes,
            'user_matched_gene_num': user_matched_gene_num}

def get_dataset_params(user_cluster, user_query, background_query, dataset, background_calc):
    
    '''Calculate and return dataset-specific parameters for hypergeometric tests'''

    if background_calc == "Intersect": 
        N = Annotation.objects.filter(gene__in=background_query, cluster__dataset_id=dataset.id).count()
        n = Annotation.objects.filter(gene__in=user_query, cluster__dataset_id=dataset.id).count()
    else:
        N = len(background_query)
        n = len(user_query)
    
    params = {'user_cluster': user_cluster,
                'N': N, 'n': n, 
                'dataset_name': dataset.dataset_name,
                'dataset_id': dataset.id,
                'dataset_type': dataset.dataset_type}
    
    return params

def get_cluster_params(user_cluster, user_query, background_query, cluster):

    '''Calculate and return cluster-specific parameters for hypergeometric tests'''
    
    K = Annotation.objects.filter(cluster_id=cluster.id, gene__in=background_query).count()
    k = Annotation.objects.filter(cluster_id=cluster.id, gene__in=user_query).select_related('gene')
    overlap_genes = list(k.values_list('gene__gene_symbol', flat=True))
    k = len(overlap_genes)
    
    params = {'user_cluster': user_cluster,
              'K': K, 'k': k, 'overlap_genes': overlap_genes,
              'cluster_id': cluster.id,
              'cluster_number': cluster.cluster_number,
              'cluster_name': cluster.cluster_description,
              'cluster_description': str(cluster),
              'dataset_name': cluster.dataset.dataset_name}
    
    return params

def user_compute_missed_genes(user_dataset_content):

    # search for gene objects in database
    user_dataset_background = list(itertools.chain.from_iterable(user_dataset_content.values()))
    user_dataset_background_q = Gene.objects.filter(Q(ensembl_id__in=user_dataset_background)|Q(gene_symbol__in=user_dataset_background))

    # count missed genes
    user_dataset_background_l = list(user_dataset_background_q.values_list('ensembl_id', 'gene_symbol'))
    db_matched = list(itertools.chain(*user_dataset_background_l))
    missed_genes = [x.capitalize() for x in user_dataset_background if x not in db_matched]
    matched_gene_nums = [len(user_dataset_background), len(user_dataset_background_l)]

    return [user_dataset_background_q, missed_genes, matched_gene_nums]

def user_get_dataset_params(user_cluster, user_query, background_query,
                            user_dataset_name, user_dataset_background_q, background_calc):
    
    ##### get querysets 
    bg_query = Gene.objects.filter(pk__in = background_query)
    us_query = Gene.objects.filter(pk__in = user_query)
    
    if background_calc == "Intersect":
        N = bg_query.intersection(user_dataset_background_q).count()
        n = us_query.intersection(user_dataset_background_q).count()
    else:
        N = len(background_query)
        n = len(user_query)

    params = {'user_cluster': user_cluster,
                'N': N, 'n': n, 
                'dataset_name': user_dataset_name}
    
    return params

def user_get_cluster_params(user_cluster, user_query, background_query, user_dataset_name, 
                        user_dataset_cluster, user_dataset_cluster_g):

    user_dataset_cluster_q = Gene.objects.filter(Q(ensembl_id__in=user_dataset_cluster_g)|Q(gene_symbol__in=user_dataset_cluster_g))

    ##### get querysets 
    bg_query = Gene.objects.filter(pk__in = background_query)
    us_query = Gene.objects.filter(pk__in = user_query)

    K = bg_query.intersection(user_dataset_cluster_q).count()
    k = us_query.intersection(user_dataset_cluster_q)

    overlap_genes = list(k.values_list('gene_symbol',flat=True))
    k = len(overlap_genes)

    params = {'user_cluster': user_cluster,
              'K': K, 'k': k, 'overlap_genes': overlap_genes,
              'cluster_number': user_dataset_cluster,
              'dataset_name': user_dataset_name }
    
    return params

def compute_hypergeom(dataset_params, cluster_params, is_user):
    
    ''' Function for performing hypergeometric tests using previously retrieved 
        dataset and cluster-specific parameters'''

    # compile dataset and cluster paramters
    compiled_params = [{**cluster_entry, **dataset_entry}
                        for cluster_entry in cluster_params
                        for dataset_entry in dataset_params
                        if cluster_entry['dataset_name'] == dataset_entry['dataset_name'] and 
                        cluster_entry['user_cluster'] == dataset_entry['user_cluster']]
    
    results = []
    
    for entry in compiled_params:
        if entry['k'] == 0:
            pval = 1
        else:
            pval = sp.hypergeom.sf(entry['k'], entry['N'], entry['n'], entry['K'])
        
        if is_user:
            r = {'user_cluster': entry['user_cluster'],
                'pval': pval, 
                'parameters': {'N': entry['N'], 'B': entry['K'], 
                                'n': entry['n'], 'b': entry['k']}, 
                'overlap_genes': entry['overlap_genes'],
                'dataset_name': entry['dataset_name'],
                'cluster_number': entry['cluster_number']
                }
        else:
            r = {'user_cluster': entry['user_cluster'],
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