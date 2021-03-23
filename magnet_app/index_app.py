from types import LambdaType
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import magnet_app.helper as helper
from django_plotly_dash import DjangoDash
from django.db import connection
from .models import Gene, Dataset, Cluster, Annotation

app = DjangoDash('index_form', add_bootstrap_links=True, external_stylesheets=[dbc.themes.BOOTSTRAP])   # replaces dash.Dash

app.layout = html.Div([html.P("How many query gene clusters are being submitted?",className="label"),
                        dbc.RadioItems(
                            id = "one-or-multiple",
                            options=[
                                {'label': 'Single', 'value': 'One'},
                                {'label': 'Multiple', 'value': 'Multiple'},
                            ], inline=True, name = "one_or_multiple", className="mb-2",
                            value='One'
                        ),
                        dbc.Label("Gene list:"),
                        dbc.Textarea(
                            id='user-genes',
                            name = "user_genes",
                            placeholder='Enter your list of query genes here',
                            rows=4, cols=15, disabled=False, className="mb-3"
                        )])


@app.expanded_callback(
    Output('user-genes', 'disabled'),
    [Input('one-or-multiple', 'value')])
def disable_textarea(one_or_multiple, **kwargs):
    
    if one_or_multiple == "One":
        return False
    else:
        return True