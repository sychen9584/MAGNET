from __future__ import absolute_import, unicode_literals 
import mygene, re, os.path
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash_table.Format import Format
from django.db.models import Q
from .models import Gene, Dataset, Cluster, Annotation, Graph_edge
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import itertools, statistics


def convert_gene_symbol_to_ensembl(gene_list):
    """Convery a list of gene symbols to ensembl ids 
    using mygene package
    
    Arguments:
        gene_list {chr} -- list of genes
    
    Returns:
        dict -- conversion status and ensembl id for each input gene
    """
    mg = mygene.MyGeneInfo()

    query = []
    remaining = gene_list.copy()
    result = {}

    for e in gene_list:
        if e.startswith("ENSMUSG"):
            result[e] = {'status': 'unconverted', 'ensembl': e}
        else:
            query.append(e)
            remaining.remove(e)
    
    print(query)

    query_results = mg.querymany(query, scopes='symbol', fields='ensembl.gene', species='mouse',returnall=True)
    print(query_results)

    seen = []

    for d in query_results["out"]:
        if 'notfound' in d:
            result[d['query']] = {'status': 'unmapped', 'ensembl': None}
        elif "ensembl" not in d or d['query'] in seen:
            pass
        else:
            if isinstance(d["ensembl"], dict):
                result[d['query']] = {'status': 'mapped', 'ensembl': d['ensembl']['gene']}
            else:
                result[d['query']] = {'status': 'mapped', 'ensembl': d['ensembl'][0]['gene']}
            
            seen.append(d['query'])
    
    unmapped = [k for k, v in result.items() if v['status']=="unmapped" ]
    converted_genes = [v['ensembl'] for k, v in result.items() if v['status'] in {"unconverted","mapped"}]

    return [converted_genes, unmapped, result]


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):

    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
    and grouping quoted words together.
    Example:

    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''

    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):

    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)

    for term in terms:
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if query is None:
                query = q
            else:
                query = query | q
    return query

def search_genes(query_string):
    
    ''' function to search annotation entries in MAGNET database 
        by user query of gene symbols or ensembl IDs

        Arguments:
        query_string {chr} -- user inputted gene symbols or ensembl IDs
    
        Returns:
        found_entries {annotation} -- annotation entries that matched user query
    ''' 

    entry_query = get_query(query_string, ['gene__gene_symbol', 'gene__ensembl_id'])
    print(entry_query)

    found_entries = list(Annotation.objects.filter(entry_query).select_related('gene').select_related('cluster__dataset').values('gene__gene_symbol',
                        'gene__ensembl_id', 'cluster__dataset__dataset_name','cluster__dataset__dataset_type', 'cluster__cluster_number',
                        'cluster__cluster_description'))
    return found_entries
    
def form_processing(request, form):

    '''Retrieve and parse form data'''
    
    one_or_multiple = form.cleaned_data.get('one_or_multiple')
    background_calc = form.cleaned_data.get('background_calc')
    user_choices = form.cleaned_data.get('user_selected_datasets')
    user_choices = [int(i) for i in user_choices]  # convert str to int

    user_genes = form.cleaned_data.get('user_genes')
    user_background = form.cleaned_data.get('user_background')
    user_genes_upload = form.cleaned_data.get("user_genes_upload")
    user_background_upload = form.cleaned_data.get("user_background_upload")
    user_dataset_upload = request.FILES.getlist('user_dataset_upload')
    
    if user_genes_upload:
        user_genes = handle_csv(user_genes_upload, one_or_multiple, False)
    else:
        user_genes = list(filter(None, form.cleaned_data['user_genes'].split("\n")))
        user_genes = {1: [a.strip().upper() for a in user_genes]}

    if user_background_upload:
        user_background = list(filter(None, handle_csv(user_background_upload, one_or_multiple, True)))
    else:
        user_background = list(filter(None, form.cleaned_data['user_background'].split("\n")))
        user_background = [b.strip().upper() for b in user_background]

    if user_dataset_upload:
        user_dataset = handle_dataset_csv(user_dataset_upload)
        #print(user_dataset)
    else:
        user_dataset = {}

    return [user_genes, user_background, user_choices, background_calc, user_dataset]


def handle_csv(csv_file, one_or_multiple, is_background):

    ''' Parse csv file for user uploaded foreground and background'''

    file_data = csv_file.read().decode("utf-8")
    lines = file_data.split("\n")

    column_num = len(lines[0].split(",")) # check how many columns exist in csv file

    keywords = {"symbols", "Symbols", "SYMBOLS", "symbol", "Symbol", "SYMBOL",
                        "genes", "Genes", "GENES", "gene", "gene", "GENE",
                        "id","ID"}

    # one query gene list or background
    if (one_or_multiple == "One" or column_num == 1) or is_background:
        gene_list = []

        for line in lines:
            fields = line.split(",")

            if fields[0].strip() not in keywords and line != '':
                gene_list.append(fields[0].strip().upper())

        # convert to dict with cluster number of 1 if it is user query gene list
        if not is_background:
            gene_list = {1: gene_list}

    # multple query gene list
    else:
        gene_list = {}
        
        for line in lines:
            fields = line.split(",")
            
            if fields[0].strip() not in keywords and line != '':
                
                if fields[1].strip() not in gene_list:
                    gene_list[fields[1].strip()] = [fields[0].strip().upper()]
                else:
                    gene_list[fields[1].strip()].append(fields[0].strip().upper())
        
    return gene_list

def handle_dataset_csv(csv_files):

    ''' handle user uploaded custom dataset ''' 

    dataset_gene_list = {}

    for f in csv_files:
        
        filename = f.name.split('.csv')[0]
        dataset_gene_list[filename] = {}

        file_data = f.read().decode("utf-8")
        lines = file_data.split("\n")

        keywords = {"symbols", "Symbols", "SYMBOLS", "symbol", "Symbol", "SYMBOL",
                    "genes", "Genes", "GENES", "gene", "gene", "GENE", "id","ID"}
        
        for line in lines:
            fields = line.split(",")
            
            if fields[0].strip() not in keywords and line != '':
                
                if fields[1].strip() not in dataset_gene_list[filename]:
                    dataset_gene_list[filename][fields[1].strip()] = [fields[0].strip().upper()]
                else:
                    dataset_gene_list[filename][fields[1].strip()].append(fields[0].strip().upper())
        
    return dataset_gene_list

def dataframe_to_dash_table(df):
    
    df['overlap_genes'] = df.apply(lambda x: ', '.join(g.lower().capitalize() for g in x['overlap_genes']), axis=1)
    df = df[['user_cluster','dataset_name','dataset_type','cluster_description',
                'pval','adjusted_pval','parameters', 'overlap_genes']]

    dt = dash_table.DataTable(

        id='sigtable',

        sort_action='native',
        filter_action='native',
        page_action='native',
        page_size=50,

        style_header={
        'backgroundColor': '#bee5eb',
        'color': '#007bff',
        'fontWeight': 'bold',
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'center',
        'textDecoration': 'underline',
        },

        style_cell={
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'center',
        'font_family': "sans-serif",
        'font_size': '15px',
        'padding': '10px',
        },

        style_data_conditional=[
        {
            'if': {'column_id': 'overlap_genes'},
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': '50px',
            'whiteSpace': 'no-wrap',
        },{
            
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
            
        }],

        tooltip_header={
            'user_cluster': {'value': "User inputted cluster name"},
            'dataset_name': {'value': "Name of dataset tested"},
            'dataset_type': {'value': "Description of dataset tested"},
            'cluster_description': {'value': "Description of dataset cluster tested"},
            'pval': {'value': "Raw p-values from hypergeometric tests"},
            'adjusted_pval': {'value': "Adjusted by Benjamini-Hochberg procedure"},
            'parameters': {'value': 'Hypergeometric parameters used, see explanation of output for more details'},
            'overlap_genes': {'value': 'User input gene symbols associated with the dataset cluster'}
        },
        
        tooltip_data=[
        {
           'overlap_genes': {'value': row['overlap_genes']}
        } for row in df.to_dict('records')
        ],

        tooltip_delay=0,
        tooltip_duration=None,

        css=[{
        'selector': '.dash-table-tooltip',
        'rule': 'font-size: 14px; font-family: sans-serif; background-color: #bee5eb'
        }],

        columns=[{
            'id': 'user_cluster',
            'name': 'Query Gene List (n)',
        }, {
            'id': 'dataset_name',
            'name': 'Dataset',
        }, {
            'id': 'dataset_type',
            'name': 'Description',
        }, {
            'id': 'cluster_description',
            'name': 'Dataset Gene Set (K)',
        }, {
            'id': 'pval',
            'name': 'P-value',
            'type': 'numeric',
            'format': Format(precision=2)
        },{
            'id': 'adjusted_pval',
            'name': 'Adjusted P-value (FDR)',
            'type': 'numeric',
            'format': Format(precision=2)
        }, {
            'id': 'parameters',
            'name': 'Parameters (N, K, n, k)',
        }, {
            'id': 'overlap_genes',
            'name': 'Overlapping Genes',
        }],
        data=df.to_dict('records'),
    )
    
    return dt

def dash_heatmap_colorscale(heatmap_data):
    heatmap_set = set(list(itertools.chain(*heatmap_data)))
    
    if heatmap_set == {'-1'}:
        return [[0, "blue"]]

    elif heatmap_set == {'0'}:
        return [[0, "grey"]]

    elif heatmap_set == {'1'}:
        return [[0, "red"]]

    elif heatmap_set == {'-1', '0'}:
        return [[0, "blue"], [1, "grey"]]

    elif heatmap_set == {'0', '1'}:
        return [[0, "grey"], [1, "red"]]
    
    elif heatmap_set == {'-1', '1'}:
        return [[0, "blue"], [1, "red"]]
    
    else:
        return [[0, "blue"], [0.5, "grey"], [1, "red"]]
    
def dash_generate_heatmaps(dataset_df, is_user,
                            low_dict, low_cutoff, high_dict, high_cutoff):
    
    ''' function to generate result heatmaps '''

    heatmap_left = []
    heatmap_right = []
    updated_dfs = []
    
    if not is_user:
        datasets = dataset_df.dataset_id.unique()
    else:
        datasets = dataset_df.dataset_name.unique()

    
    column_indicator = "left"
    
    for d in datasets:

        heatmap_content = []

        if not is_user:
            dataset = Dataset.objects.get(id=d)
            heatmap_content.append(html.H4(children=html.A(dataset.dataset_name,href="/dataset/"+ str(dataset.id),target="_blank"),
                            style={"font-style": "italic"}))
            heatmap_content.append(html.H5(children=html.A(dataset.dataset_type,href="/dataset/"+ str(dataset.id),target="_blank"),
                            style={"font-style": "italic"}))
            # filter for dataframe rows that belong to the dataset
            df = dataset_df[dataset_df.dataset_id == d]
        else: 
            heatmap_content.append(html.H4(d, style={"font-style": "italic"}))
            df = dataset_df[dataset_df.dataset_name == d]

        ## extract parameter values from dictionary and format as string
        df["parameters"] = df.apply(lambda x: ', '.join(str(e) for e in list(x['parameters'].values())), axis=1)

        ### row names and column names of heatmap
        rows = df.user_cluster.unique()
        columns = df.cluster_number.astype(str).unique()

        ### populate heatmap cells by each row
        heatmap_data = []; p_vals = []; adjusted_pvals = []; 
        cluster_names = []; parameters = []

        df_list = [x for _, x in df.groupby('user_cluster')]
        
        for cluster_df in df_list:

            # update colors if p value threshold changes:
            ps = cluster_df.pval.values.tolist()
            hd=[]
            for p in ps:
                if p < low_dict[low_cutoff]:
                    hd.append("1")
                elif p > high_dict[high_cutoff]:
                    hd.append("-1")
                else:
                    hd.append("0")

            heatmap_data.append(hd)
            p_vals.append(ps)
            adjusted_pvals.append(cluster_df.adjusted_pval.values.tolist())
            parameters.append(cluster_df.parameters.values.tolist())

            
            if is_user:
                cluster_names.append(cluster_df.cluster_number.values.tolist())

            else:
                cluster_names.append(cluster_df.cluster_name.values.tolist())

            ## update significance determination in dataframe
            cluster_df["color"] = hd 

            updated_dfs.append(cluster_df)

        custom_data = np.stack((cluster_names, p_vals, adjusted_pvals, parameters), axis=-1)
        colorscale = dash_heatmap_colorscale(heatmap_data)
        fig = go.Figure(data=go.Heatmap(z=heatmap_data,
                        x = columns, 
                        y = rows,
                        xgap=1.5, ygap=1.5,
                        customdata=custom_data,
                        colorscale= colorscale, 
                        hovertemplate='<b><i>%{customdata[0]}</b></i><br>'+
                            'P-value: %{customdata[1]:.2e}<br>'+
                            'Adjusted P-value: %{customdata[2]:.2e}<br>'+
                            'Parameters: %{customdata[3]}<br>'+
                            '<extra></extra>'
                        
                        ))

        fig.update_traces(showscale=False,)
        fig.update_layout(
            xaxis={'title':'Dataset Gene Sets', 'title_font_size':14, 'tickfont_size':15},
            yaxis={'title':'Query Gene Lists', 'title_font_size':14, 'tickfont_size':15},
            width=400, height=250,
            margin=dict(l=30, r=20, t=20, b=30))
        fig['layout']['yaxis']['autorange'] = "reversed"
                                    
        heatmap_content.append(dcc.Graph(figure=fig,
            style={
                "display": "block",
                "margin-left": "auto",
                "margin-right": "auto",
            }
        ))
        heatmap_content.append(html.Br())

        if column_indicator == "left":
            heatmap_left.extend(heatmap_content)
            column_indicator = "right"
        else:
            heatmap_right.extend(heatmap_content)
            column_indicator = "left"

    return [heatmap_left, heatmap_right, updated_dfs]

def merge_sig_dataframes(user_updated_df, updated_df):

    if updated_df is None and user_updated_df is not None:
        user_updated_df.rename(columns={'cluster_number':'cluster_description'}, inplace=True)
        user_updated_df = user_updated_df.sort_values(["user_cluster","dataset_name"])
        user_updated_df["row_num"] = np.arange(user_updated_df.shape[0])
        user_updated_df['dataset_type'] = ''

        #user_sig_df = user_updated_df[user_updated_df.color == '1']
        user_sig_df = user_updated_df
        return  user_sig_df

    elif user_updated_df is None and updated_df is not None:
        updated_df = updated_df.drop(['cluster_number', 'cluster_name'], axis = 1)
        updated_df =  updated_df.sort_values(["user_cluster","dataset_name"])
        updated_df["row_num"] = np.arange(updated_df.shape[0])
        #print(updated_df.color == '1')

        #sig_df = updated_df[updated_df.color == '1']
        #print(sig_df)
        sig_df = updated_df

        return  sig_df
    
    else:
        user_updated_df.rename(columns={'cluster_number':'cluster_description'}, inplace=True)
        updated_df = updated_df.drop(['cluster_number', 'cluster_name'], axis = 1) 
        
        combined_sig_df = pd.concat([user_updated_df, updated_df]).sort_values(["user_cluster", "dataset_name"])
        combined_sig_df["row_num"] = np.arange(combined_sig_df.shape[0])
        #combined_sig_df = combined_sig_df[combined_sig_df.color=='1']

        return combined_sig_df

def construct_network_elements(df, user_cluster):

    '''Construct network elements for cytoscape visualization'''

    #datasets = Dataset.objects.filter(pk__in=df.dataset_id.unique()) # get user selected datasets
    #clusters = Cluster.objects.filter(dataset__in=datasets).prefetch_related('dataset') # get all associated clusters
    dataset_list = df.dataset_id.unique()
    cluster_list = df.cluster_id.unique()

    network_elements = {}

    network_elements["dataset_nodes"] = [get_dataset_node_elements(df, d) for d in dataset_list]

    network_elements["cluster_nodes"] = [get_cluster_node_elements(df, user_cluster, c) for c in cluster_list]
    
    # filter for edges with similarity score above zero
    edges = Graph_edge.objects.filter(proportion__gt=0.1).filter(cluster1__in=cluster_list, cluster2__in=cluster_list).prefetch_related('cluster1','cluster2',
                                                                                                                                        'cluster1__dataset', 'cluster2__dataset')
                                                                                                                                        
    network_elements["edges"] = [get_edge_elements(e) for e in edges]
    
    return network_elements

def get_dataset_node_elements(df, dataset):

    df_filtered = df[df.dataset_id==int(dataset)]
    return {
        'data': {'id': 'dataset_'+ str(df_filtered.dataset_id.values[0]),
                'label': df_filtered.dataset_name.values[0] },
        'classes': 'dataset'
    }

def get_cluster_node_elements(df, user_cluster, cluster):

    df_filtered = df[(df.cluster_id==cluster) & (df.user_cluster == user_cluster)]
    
    
    return {
        'data': {'id': 'cluster_'+ str(df_filtered.cluster_id.values[0]), 
                    'label': df_filtered.cluster_description.values[0],
                    'parent': 'dataset_' + str(df_filtered.dataset_id.values[0]),
                    'pval': df_filtered.pval.values[0],
                    'adj_pval': df_filtered.adjusted_pval.values[0],
                    'parameters': df_filtered.parameters.values[0],
                },
        'classes': 'cluster' 
    }

def get_edge_elements(edge):
    
    return {
        'data': {'source': 'cluster_'+ str(edge.cluster1.id), 
                    'target': 'cluster_'+ str(edge.cluster2.id),
                    'weight': edge.proportion,
                    'overlap_num': edge.overlap_num,
                    'cluster1': str(edge.cluster1),
                    'cluster2': str(edge.cluster2), }
    }


    
   