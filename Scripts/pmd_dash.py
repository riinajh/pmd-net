'''
    Adapted from https://dash.plotly.com/cytoscape and other Plotly dash tutorials. 
    wanted to be able to visualize the network a little bit, and nx is not great.
'''
# Run with `python Scripts/pmd_dash.py` and
# visit 127.0.0.1:8050/ in your web browser.


import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import bz2
import networkx as nx
import json
import os

os.chdir('..')
os.chdir('pmd_baseline/pmd_filtered')
fileinfo=bz2.BZ2File('Net', 'r')
filtered_articles_net=nx.read_gpickle(fileinfo)
fileinfo=bz2.BZ2File('articles', 'r')
unfiltered_articles=nx.read_gpickle(fileinfo)
fileinfo.close()
os.chdir('..')
os.chdir('..')
os.chdir('Scripts')



app = dash.Dash(__name__)

def generate_nodes(filtered_articles_net, unfiltered_articles):
    for item in filtered_articles_net:
        node={'data': {'id': item,
                        'label': unfiltered_articles[item]['PMID']}}
        yield node
nodes=[]
for node in generate_nodes(filtered_articles_net, unfiltered_articles):
    nodes.append(node)
def generate_edges(filtered_articles_net, unfiltered_articles):
    for item in filtered_articles_net:
        for n in filtered_articles_net.neighbors(item):
            edge={'data':{'source':item, 'target':n}}
            yield edge
edges=[]
for edge in generate_edges(filtered_articles_net, unfiltered_articles):
    edges.append(edge)
default_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': '#999999',
            'label': 'data(label)'
        }
    }
]
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape-event-callbacks-2',
        layout={'name': 'breadthfirst'},
        elements=edges+nodes,
        stylesheet=default_stylesheet,
        style={'width': '100%', 'height': '450px'}
    ),
    html.P(id='cytoscape-tapNodeData-output'),
    html.P(id='cytoscape-tapEdgeData-output'),
    html.P(id='cytoscape-mouseoverNodeData-output'),
    html.P(id='cytoscape-mouseoverEdgeData-output')
])

@app.callback(Output('cytoscape-tapNodeData-output', 'children'),
              Input('cytoscape-event-callbacks-2', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        return ["You recently clicked: " + data['label'], 
               '- '+ unfiltered_articles[str(data['label'])]['abstract'][0]]

@app.callback(Output('cytoscape-tapEdgeData-output', 'children'),
              Input('cytoscape-event-callbacks-2', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "You recently clicked the edge between " + \
               data['source'].upper() + " and " + data['target'].upper()

@app.callback(Output('cytoscape-mouseoverNodeData-output', 'children'),
              Input('cytoscape-event-callbacks-2', 'mouseoverNodeData'))
def displayTapNodeData(data):
    if data:
        return "You recently hovered over: " + data['label']

@app.callback(Output('cytoscape-mouseoverEdgeData-output', 'children'),
              Input('cytoscape-event-callbacks-2', 'mouseoverEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "You recently hovered over the edge between " + \
               data['source'].upper() + " and " + data['target'].upper()

if __name__ == '__main__':
    app.run_server(debug=True)
