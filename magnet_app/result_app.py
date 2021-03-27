import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
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

#high_values = [0.50, 0.65, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99, 0.995, 0.999]
high_values = [0.5, 0.9, 0.95, 0.99, 0.995, 0.999, 0.9995, 0.9999, 0.99995, 0.99999]
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


app.layout = dbc.Container(children=[

    dbc.Container(
        dbc.Row(
            [dbc.Col(width=5, children=html.Div([
                    html.H5("Significance cutoffs:"),
                    html.Div([
                            html.Label("Enrichment", style={'display': 'inline-block',
                                                        'width': '95%',
                                                        'text-align': 'right',
                                                        'color': 'red'}),
                            html.Div(dcc.Slider(
                                id='low-cutoff',
                                marks={k: {'label': '{}'.format(v), 'style':{"transform": "rotate(45deg)"}} for k, v in low_dict.items()},
                                min=0, max=9, step=None,value=7,
                            ),style={'font-size':'10px'}),

                            html.Br(),

                            html.Label("Depletion", style={'display': 'inline-block',
                                                                'width': '95%',
                                                                'text-align': 'right',
                                                                'color': 'blue'}),
                            dcc.Slider(
                                id='high-cutoff',
                                marks={k: {'label': '{}'.format(v), 'style':{"transform": "rotate(45deg)"}} for k, v in high_dict.items()},
                                min=0, max=9, step=None, value=2,
                            ),
                    ], style={'width': '85%','margin':'0 auto'})]
            )),
            dbc.Col(width=5, children=html.Div(children=[html.A("Explanation of Output",href="/documentation/?page=exp_output", target="_blank", className="btn btn-info btn-lg mb-3"), 
                            html.Br(), 
                            html.A("Back to home",href="/", target="_blank", className="btn btn-secondary btn-lg"), ], className="text-center"), 
                            className="my-auto")
        ], justify="around")),
    
    html.Br(), html.Br(),

    dbc.Container([
            html.Ul([
                html.Li(html.A(html.H5("Heatmap Visualization"),
                                        className="nav-link active", **{"data-toggle": "tab"}, href="#heatmap-view"),
                                className="nav-item"),

                html.Li(html.A(html.H5("All Significantly Enriched Results"),
                                        className="nav-link", **{"data-toggle": "tab"}, href="#sig"),
                                className="nav-item"),
                 
                html.Li(html.A(html.H5("Network View"),
                                        className="nav-link", **{"data-toggle": "tab"}, href="#network-view"),
                                className="nav-item"),], 
                        className="nav nav-tabs nav-justified", role="tablist"),

                html.Div([
                        html.Div([
                            dbc.Row(
                                [html.Div(id='heatmap_left', className="col-5 pt-3"),
                                html.Div(id='heatmap_right', className="col-5 pt-5")], justify="around"),
                        ], id="heatmap-view", className="container tab-pane active"),
                        html.Div(html.Div([html.A("Download Significant Results", className="btn btn-primary mt-2 mb-3",
                                                        href="/results/download/"),
                                            html.Div(id='sig_table'),]),
                                id="sig", className="container tab-pane"),
                                
                        html.Div(html.Div(
                            [html.Div(dcc.RadioItems(id="hidden_input", 
                                        options=[{'label': 'x', 'value': 'y'},]),
                                        style={"display":'None'}),
                            dcc.Dropdown(id='network-dropdown', clearable=False),
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

                        className="tab-content"),], fluid=True)
    
])

#Output("test_table", "data"),
@app.expanded_callback(
    [Output("heatmap_left", "children"),
    Output("heatmap_right", "children"),
    Output("sig_table", "children"),],
    [Input("low-cutoff", "value"),
    Input("high-cutoff", "value")])
def update_heatmap(low_cutoff, high_cutoff, **kwargs):
    # retrieve hypergeom results
    dataset_dict = kwargs['session_state']["django_to_dash_context"]['dataset_dict']
    dataset_df = pd.DataFrame(dataset_dict)
    
    user_dataset_dict = kwargs['session_state']["django_to_dash_context"]['user_dataset_dict']
    user_dataset_df = pd.DataFrame(user_dataset_dict)

    try:
        user_heatmap_left, user_heatmap_right, user_updated_df = helper.dash_generate_heatmaps(user_dataset_df, True,
                                                            low_dict, low_cutoff,
                                                            high_dict, high_cutoff)
    except AttributeError:
        user_heatmap_left = []
        user_heatmap_right = []
        user_updated_df = None
    
    user_updated_df = pd.concat(user_updated_df) if user_updated_df else None
    
    try:
        heatmap_left, heatmap_right, updated_df = helper.dash_generate_heatmaps(dataset_df, False,
                                                            low_dict, low_cutoff,
                                                            high_dict, high_cutoff)
    except AttributeError:
        heatmap_left = []
        heatmap_right = []
        updated_df = None


    updated_df = pd.concat(updated_df) if updated_df else None

    heatmap_legend = [html.Img(src='/static/magnet_app/images/legend_new.jpg',
                                        width="50%",
                                        className="rounded mx-auto d-block img-thumbnail"),
                     html.Br()]

    heatmap_content_left = user_heatmap_left + heatmap_left
    heatmap_content_right = heatmap_legend + user_heatmap_right + heatmap_right
    
    sig_df = helper.merge_sig_dataframes(user_updated_df, updated_df)
    sig_table_content = helper.dataframe_to_dash_table(sig_df)
    kwargs['session_state']['dash_to_django_context'] = sig_df.to_dict()

    return [heatmap_content_left, heatmap_content_right, sig_table_content]

@app.expanded_callback(
    [Output("network-dropdown", "options"),
    Output("network-dropdown", "value")],
    [Input("hidden_input", "value")])
def network_dropdown(hidden_input,  **kwargs):
    
    dataset_dict = kwargs['session_state']["django_to_dash_context"]['dataset_dict']
     #### render dropdown menu for network
    try:
        df = pd.DataFrame(dataset_dict)
        cluster_choices = [{'label': 'User cluster '+x, 'value': x} for x in df.user_cluster.unique()]
        default_value = df.user_cluster.unique()[0]

    except AttributeError:
        cluster_choices = [{'label': 'User cluster Null', 'value': 'Null'}]
        default_value = "Null"

    return [cluster_choices, default_value]

@app.expanded_callback(
    Output("network", "children"),
    [Input("network-dropdown", "value")])
def network_view(user_cluster,  **kwargs):

    try:
        dataset_dict = kwargs['session_state']["django_to_dash_context"]['dataset_dict']
        df = pd.DataFrame(dataset_dict)
        # flatten parameters in to string
        df["parameters"] = df.apply(lambda x: ', '.join(str(e) for e in list(x['parameters'].values())), axis=1)

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
                                        style={'width': '100%', 'height': '600px'},
                                        stylesheet= default_stylesheet + new_style,
                                        elements=list(itertools.chain(
                                        network_elements["dataset_nodes"],
                                        network_elements["cluster_nodes"],
                                        network_elements['edges']
                                        ))) ]
    
    except ValueError:
        network_content = []
    
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

        
