import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import magnet_app.helper as helper
import itertools
from dash.exceptions import PreventUpdate


from django_plotly_dash import DjangoDash

from django.db import connection
from .models import Gene, Dataset, Cluster, Annotation

app = DjangoDash('result_heatmap', add_bootstrap_links=True, external_stylesheets=[dbc.themes.BOOTSTRAP])   # replaces dash.Dash

cyto.load_extra_layouts()

# populate possible p value thresholds for slider widget
low_values = [0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
low_dict = {i: low_values[i] for i in range(len(low_values))}

high_values = [0.50, 0.65, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99, 0.995, 0.999]
high_dict = {i: high_values[i] for i in range(len(high_values))}

# style sheet for network
default_stylesheet = [
    {
        "selector": '.dataset',
        'style': {
            "opacity": 1,
            'content': 'data(label)',
            'font-weight': 'bold',
            'font-size': 24,
            'font-style': "italic",
            "text-margin-y": -8

        }
    },

    {
        "selector": '.cluster',
        'style': {
             "opacity": 1,
            'content': 'data(label)',
        }
    },

    {
        "selector": 'edge',
        'style': {
            "curve-style": "bezier",
            "line-color": "#559E54",
            "opacity": 0.5
        }
    },

    # edge widths depending on similarity scores
    {
        "selector": '[weight <= 0.15]',
        'style': { "width": 3 }
    },

    {
        "selector": '[weight > 0.15][weight <= 0.20]',
        'style': { "width": 8 }
    },

    {
        "selector": '[weight > 0.2][weight <= 0.25]',
        'style': { "width": 13 }
    },

    {
        "selector": '[weight > 0.25][weight <= 0.3]',
        'style': { "width": 18 }
    },

    {
        "selector": '[weight > 0.3]',
        'style': { "width": 25 }
    },

]


app.layout = html.Div([
    html.Br(),
    dbc.Container(
    dbc.Row(
            [
                dbc.Col(html.Div(id='heatmaps'), className="sm my-auto"),
                dbc.Col(html.Div([
                    html.H5("Significance cutoffs:"),
                    html.Div([
                            html.Label("Low threshold", style={'display': 'inline-block',
                                                        'width': '95%',
                                                        'text-align': 'right',
                                                        'color': 'red'}),
                            html.Div(dcc.Slider(
                                id='low-cutoff',
                                marks={k: {'label': '{}'.format(v), 'style':{"transform": "rotate(45deg)"}} for k, v in low_dict.items()},
                                min=0, max=9, step=None,value=7,
                            ),style={'font-size':'10px'}),

                            html.Br(),

                            html.Label("High threshold", style={'display': 'inline-block',
                                                                'width': '95%',
                                                                'text-align': 'right',
                                                                'color': 'blue'}),
                            dcc.Slider(
                                id='high-cutoff',
                                marks={k: {'label': '{}'.format(v), 'style':{"transform": "rotate(45deg)"}} for k, v in high_dict.items()},
                                min=0, max=9, step=None, value=6,
                            ),
                    ], style={'width': '85%','margin':'0 auto'}),
                    

                    

                    html.Br(), html.Br(),

                    html.Div([html.Img(src='/static/magnet_app/images/legend_new.jpg',
                                        width="35%",
                                        className="rounded mx-auto d-block img-thumbnail")]),
                    html.Br(), html.Br(),

                    html.Div(children=html.A("Explanation of Output",href="/documentation/?page=exp_output", target="_blank",
                            className="btn btn-info btn-lg"), className="text-center"),
                    html.Br(),

                ]), className="sm my-auto justify-content-center"),
            ]
        ),
    ),
    dbc.Container([
            html.Ul([html.Li(html.A(html.H5("Significant Results"),
                                        className="nav-link active", **{"data-toggle": "tab"}, href="#sig"),
                                className="nav-item"),
                 
                html.Li(html.A(html.H5("Network View"),
                                        className="nav-link", **{"data-toggle": "tab"}, href="#network-view"),
                                className="nav-item"),], 
                        className="nav nav-tabs nav-justified", role="tablist"),

                html.Div([
                        html.Div(html.Div([html.A("Download Significant Results", className="btn btn-primary mt-2 mb-3",
                                                        href="/results/download/"),
                                             html.Div(id='sig_table'),
                                            ]),
                                id="sig", className="container tab-pane active"),
                                
                        html.Div(html.Div(
                            [dcc.Dropdown(id='network-dropdown', clearable=False),
                            # Hidden div inside the app that stores the intermediate value
                            html.Div(id='hidden-df', style={'display': 'none'}),
                            html.Div(id='network'),
                            html.Hr(),
                            dbc.Container(
                                dbc.Row(
                                    [dbc.Col([
                                        html.Div(id='node-hover'),
                                        html.Div(id='edge-hover'),
                                        ]),
                                    dbc.Col([html.Img(src='/static/magnet_app/images/network_legend.jpg',
                                            width="85%",
                                            className="rounded mx-auto d-block img-thumbnail"),
                                            html.Button("Download Network", id="network_download",
                                            className="btn btn-primary btn-md mt-2")], className="text-center")]
                                ),
                                style={'margin-top':'10px','margin-bottom':'10px'}),
                            ]),
                                id="network-view", className="container tab-pane"),],

                        className="tab-content"),])
    
])


@app.expanded_callback(
    [Output("heatmaps", "children"),
    Output("sig_table", "children"),
    Output("network-dropdown", "options"),
    Output("network-dropdown", "value"),
    Output('hidden-df', 'children')],
    [Input("low-cutoff", "value"),
    Input("high-cutoff", "value")])
def update_heatmap(low_cutoff, high_cutoff, **kwargs):
    # retrieve hypergeom results
    dataset_dict = kwargs['session_state']["django_to_dash_context"]['dataset_dict']
    dataset_df = pd.DataFrame(dataset_dict)
    
    user_dataset_dict = kwargs['session_state']["django_to_dash_context"]['user_dataset_dict']
    user_dataset_df = pd.DataFrame(user_dataset_dict)

    ## build up table for significant result entries:
    sig_table_content = []

    table_header = [
        html.Thead(html.Tr([html.Th(children=html.A("User Cluster",
                                    href="#", **{"data-toggle": "tool-tip"},
                                    title="User inputted cluster name")), 
                            html.Th(children=html.A("Dataset",
                                    href="#", **{"data-toggle": "tool-tip"},
                                    title="Name of dataset tested")),
                            html.Th(children=html.A("Dataset Cluster",
                                    href="#", **{"data-toggle": "tool-tip"},
                                    title="Description of dataset cluster tested")),
                            html.Th(children=html.A("P-value",
                                    href="#", **{"data-toggle": "tool-tip"},
                                    title="Raw p-values from hypergeometric tests")),
                            html.Th(children=html.A("Adjusted P-Value (FDR)",
                                    href="#", **{"data-toggle": "tool-tip"},
                                    title="Adjusted by Benjamini-Hochberg procedure")),
                            html.Th(children=html.A("Parameters (N, B, n, b)",
                                    href="#", **{"data-toggle": "tool-tip"},
                                    title='''Explanation of hypergeometric parameters:
                                    N = Total number of background genes, depending on background calculation mode selected 
                                    B = Number of background genes associated with the dataset cluster
                                    n = Total number of user input genes
                                    b = Number of user input genes associated with the dataset cluster''')),
                            html.Th(children=html.A("Overlapped Genes",
                                    href="#", **{"data-toggle": "tool-tip"},
                                    title="User input gene symbols associated with the dataset cluster")),
                            ]), style={"text-align":'center'}, className="table-info"),
    ]


    try:
        user_heatmap_content, user_updated_df = helper.dash_generate_heatmaps(user_dataset_df, True,
                                                            low_dict, low_cutoff,
                                                            high_dict, high_cutoff)
    except AttributeError:
        user_heatmap_content = []
        user_updated_df = None
    
    user_updated_df = pd.concat(user_updated_df) if user_updated_df else None
    
    try:
        heatmap_content, updated_df = helper.dash_generate_heatmaps(dataset_df, False,
                                                            low_dict, low_cutoff,
                                                            high_dict, high_cutoff)
    except AttributeError:
        heatmap_content = []
        updated_df = None


    updated_df = pd.concat(updated_df) if updated_df else None
   
    sig_df = helper.merge_sig_dataframes(user_updated_df, updated_df)
    
    heatmap_content = user_heatmap_content + heatmap_content

    table_body = [html.Tbody([helper.dataframe_to_html_table(row) for row in 
                zip(sig_df["user_cluster"], sig_df["dataset_name"],
                    sig_df["cluster_description"], sig_df["pval"],
                    sig_df["adjusted_pval"], sig_df["parameters"],
                    sig_df["overlap_genes"], sig_df["row_num"])])]

    sig_table_content.append(dbc.Table(table_header+table_body, bordered=True,striped=True,hover=True,size="lg"))
    kwargs['session_state']['dash_to_django_context'] = sig_df.to_dict()

    #### render dropdown menu for network
    try:
        cluster_choices = [{'label': 'User cluster '+x, 'value': x} for x in updated_df.user_cluster.unique()]
        default_value = updated_df.user_cluster.unique()[0]
        #### hide dataframe in layout to pass to network callback
        hidden_df = updated_df.to_json()  
    except AttributeError:
        cluster_choices = [{'label': 'User cluster Null', 'value': 'Null'}]
        default_value = "Null"
        hidden_df = None
        
    return [heatmap_content, sig_table_content, 
        cluster_choices, default_value, hidden_df]

@app.expanded_callback(
    Output("network", "children"),
    [Input("network-dropdown", "value"),
    Input('hidden-df', "children")])
def network_view(user_cluster, hidden_df,  **kwargs):

    df = pd.read_json(hidden_df)
    network_elements = helper.construct_network_elements(df, user_cluster)
    

    # node colors depending on p-values
    new_style = [
    {
        "selector": '[pval < 0.00001]',
        'style': { "background-color": "#e31a1c" }
    },
    {
        "selector": '[pval >= 0.00001][pval < 0.0001]',
        'style': { "background-color": "#fc4e2a" }
    },
    {
        "selector": '[pval >= 0.0001][pval < 0.001]',
        'style': { "background-color": "#fd8d3c" }
    },
    {
        "selector": '[pval >= 0.001][pval < 0.01]',
        'style': { "background-color": "#fed976" }
    },
    {
        "selector": '[pval >= 0.01][pval < 0.05]',
        'style': { "background-color": "#ffeda0" }
    },
    {
        "selector": '[pval >= 0.05]',
        'style': { "background-color": "#b3b3b3" }
    },]

    network_content = [ cyto.Cytoscape(id='network1',
                                    layout={'name': 'cola', 
                                            'boundingBox':{'x1':400, 'y1': 200, 'x2':650, 'y2':450}},
                                    style={'width': '105%', 'height': '600px'},
                                    stylesheet= default_stylesheet + new_style,
                                    elements=list(itertools.chain(
                                    network_elements["dataset_nodes"],
                                    network_elements["cluster_nodes"],
                                    network_elements['edges']
                                    ))) ]
    
    '''network_content = [ cyto.Cytoscape(id='network1',
                                    layout={'name': 'preset'},
                                    style={'width': '105%', 'height': '600px'},
                                    stylesheet= default_stylesheet + new_style,
                                    elements= [
                                                {
                                                    'data': {'id': 'one', 'label': 'Node 1','pval':0.1},
                                                    'position': {'x': 200, 'y': 400}
                                                },
                                                {
                                                    'data': {'id': 'two', 'label': 'Node 2','pval':0.04},
                                                    'position': {'x': 300, 'y': 400}
                                                }, 
                                                {
                                                    'data': {'id': 'three', 'label': 'Node 3','pval':0.009},
                                                    'position': {'x': 400, 'y': 400}
                                                },
                                                {
                                                    'data': {'id': 'four', 'label': 'Node 4','pval':0.0009},
                                                    'position': {'x': 500, 'y': 400}
                                                },
                                                {
                                                    'data': {'id': 'five', 'label': 'Node 5','pval':0.00009},
                                                    'position': {'x': 600, 'y': 400}
                                                },
                                                {
                                                    'data': {'id': 'six', 'label': 'Node 6', 'pval': 0.000009},
                                                    'position': {'x': 700, 'y': 400}
                                                },
                                                {
                                                    'data': {
                                                        'id': 'one-two',
                                                        'source': 'one','target': 'two',
                                                        'weight': 0.2
                                                    }
                                                },
                                                 {
                                                    'data': {
                                                        'id': 'two-three',
                                                        'source': 'two','target': 'three',
                                                        'weight': 0.3
                                                    }
                                                },
                                                 {
                                                    'data': {
                                                        'id': 'three-four',
                                                        'source': 'three','target': 'four',
                                                        'weight': 0.4
                                                    }
                                                },
                                                 {
                                                    'data': {
                                                        'id': 'four-five',
                                                        'source': 'four','target': 'five',
                                                        'weight': 0.5
                                                    }
                                                },
                                                 {
                                                    'data': {
                                                        'id': 'five-six',
                                                        'source': 'five','target': 'six',
                                                        'weight': 0.6
                                                    }
                                                },
            ])]'''

    return network_content

@app.expanded_callback(
    Output('node-hover', 'children'),
    [Input('network1', 'tapNodeData')])
def displayHoverNodeData(data, **kwargs):

    node_hover_content = []

    if data:
        if 'parent' in data:
            node_hover_content = [

                html.H5(data['label']),
                html.Ul([
                    html.Li([html.B("p-value: "), "{:.2e}".format(data['pval'])]),
                    html.Li([html.B("Adj. p-value: "),  "{:.2e}".format(data['adj_pval'])]),
                    html.Li([html.B("Parameters: "), data['parameters']]),
                ])
            ]
        else:
            node_hover_content = [

                html.H5(data['label'])

            ]
            

    else: pass
    
    return node_hover_content

@app.expanded_callback(
    Output('edge-hover', 'children'),
    [Input('network1', 'tapEdgeData')])
def displayHoverEdgeData(data, **kwargs):

    edge_hover_content = []

    if data:
        edge_hover_content = [
            
            html.P([
                html.B(data['cluster1']),
                " --- ",
                html.B(data['cluster2']),
                " => ",
                html.B(data['overlap_num'], style = {'color':'red'}),
                " genes"
            ])
        ]

    else: pass
    
    return edge_hover_content


@app.expanded_callback(
    Output("network1", "generateImage"),
    [
        Input("network_download", "n_clicks"),
    ])
def get_image(network_download, **kwargs):

    ctx = dash.callback_context
    if ctx.triggered:

        return {
            'type': 'jpg',
            'action': 'download',
            'filename': "network"
            }
            
    else:
        raise PreventUpdate

        
