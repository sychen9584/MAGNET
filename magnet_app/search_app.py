import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import magnet_app.helper as helper
import itertools
from dash.exceptions import PreventUpdate

from django_plotly_dash import DjangoDash

from django.db import connection
from .models import Gene, Dataset, Cluster, Annotation

app = DjangoDash('gene_search', add_bootstrap_links=True, external_stylesheets=[dbc.themes.BOOTSTRAP])   # replaces dash.Dash

app.layout = html.Div([

                # hidden radio button for placeholder
                html.Div(dcc.RadioItems(id="placeholder", 
                                        options=[{'label': 'x', 'value': 'y'},]),
                                        style={"display":'None'}),

                dash_table.DataTable(

                id='search-table',

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
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }],

                columns=[
                {
                    'id': 'gene__gene_symbol',
                    'name': 'Gene Symbol',
                },{
                    'id': 'gene__ensembl_id',
                    'name': 'Ensembl ID',
                }, {
                    'id': 'cluster__dataset__dataset_name',
                    'name': 'Dataset Name',
                }, {
                    'id': 'cluster__dataset__dataset_type',
                    'name': 'Description',
                }, {
                    'id': 'cluster__cluster_number',
                    'name': 'Gene Set #',
                }, {
                    'id': 'cluster__cluster_description',
                    'name': 'Annotation',
                }],
                data={},
            )])


@app.expanded_callback(
    Output('search-table', 'data'),
    [Input('placeholder', 'value')])
def generate_searchtable(placeholder, **kwargs):
    
    found_entries = kwargs['session_state']["search_context"]['found_entries']
    print(found_entries)

    df = pd.DataFrame.from_dict(found_entries)
    print(df)

    return df.to_dict('records')