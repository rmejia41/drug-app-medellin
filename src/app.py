# #App with positron
import dash
from dash import html, dcc, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import openpyxl

# Load the dataset
data_path = 'https://github.com/rmejia41/open_datasets/raw/main/intoxicacion_medellin_final.xlsx'
data = pd.read_excel(data_path)

# Convert 'year' to numeric, handling errors by coercing to NaN
data['year'] = pd.to_numeric(data['year'], errors='coerce')

# Ensure 'latitude' and 'longitude' are floats, converting any problematic data to NaN
data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')

# Map 'hospitalized' data if necessary (adjust based on actual data structure)
data['hospitalized'] = data.get('hospitalized_').map({1: 'Yes', 2: 'No'}, na_action='ignore')

# Prepare the 'year' dropdown options
year_options = [{'label': str(year), 'value': year} for year in sorted(data['year'].unique())]
year_options.insert(0, {'label': 'All Years', 'value': 'All Years'})

# Initialize the Dash app with LITERA theme and additional CSS for title and dropdown
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Reported Drug Intoxication Cases in Medellin, Colombia", style={'color': '#007BFF', 'fontFamily': 'Arial, sans-serif', 'fontWeight': 'bold'}), className="mb-4")
    ]),
    dbc.Row([
        dbc.Col([
            html.Label('Select Year:', style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='year-dropdown', options=year_options, value='All Years', style={'width': '50%'}),
        ], width=4),
    ], justify="start"),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='map-plot'),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.Label('Details of Cases:', style={'fontWeight': 'bold'}),
            dash_table.DataTable(
                id='case-details-table',
                columns=[
                    {'name': 'ID', 'id': 'id'},
                    {'name': 'Sex', 'id': 'sex'},
                    {'name': 'Age', 'id': 'age'},
                    {'name': 'Neighborhood', 'id': 'neighborhood name'},
                    {'name': 'Date Provider Visit', 'id': 'date provider visit'},
                    {'name': 'Time in Days to Visit Provider', 'id': 'time in days to visit provider'},
                    {'name': 'Hospitalized', 'id': 'hospitalized'},
                ],
                style_table={'overflowX': 'auto', 'width': '100%', 'minWidth': '100%'},
                page_size=10,
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                column_selectable='single',
                row_selectable='multi',
                style_cell={
                    'fontSize': '12px',
                    'padding': '5px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'textAlign': 'left'
                },
                style_header={
                    'backgroundColor': 'lightgrey',
                    'fontWeight': 'bold',
                    'fontSize': '14px',
                }
            )
        ], width=12),
    ])
], fluid=True)

@app.callback(
    Output('case-details-table', 'data'),
    Input('year-dropdown', 'value')
)
def update_table(selected_year):
    if selected_year == 'All Years':
        filtered_data = data.copy()
    else:
        selected_year_int = int(selected_year)
        filtered_data = data[data['year'] == selected_year_int].copy()

    table_data = filtered_data.to_dict('records')
    return table_data

@app.callback(
    Output('map-plot', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('case-details-table', 'selected_rows'),
     Input('case-details-table', 'data')]
)
def update_map(selected_year, selected_rows, rows_data):
    if selected_rows:
        selected_ids = [rows_data[idx]['id'] for idx in selected_rows]
        filtered_data = data[data['id'].isin(selected_ids)]
    else:
        if selected_year == 'All Years':
            filtered_data = data.copy()
        else:
            selected_year_int = int(selected_year)
            filtered_data = data[data['year'] == selected_year_int]

    hover_data = {
        'id': True,
        'age': True,
        'sex': True,
        'neighborhood name': True,
        'comuna': True,
        'hospitalized': True,
        'time in days to visit provider': True,
        'latitude': False,
        'longitude': False
    }

    fig = px.scatter_mapbox(filtered_data,
                            lat='latitude',
                            lon='longitude',
                            hover_name='neighborhood name',
                            color='comuna',
                            color_continuous_scale=[[color, color.replace("rgb", "rgba").replace(")", ", 0.7)")] for color in px.colors.qualitative.Plotly],
                            zoom=10,
                            size_max=15,
                            title="Drug Intoxication Cases in Medellin",
                            center={"lat": 6.244338, "lon": -75.573553},
                            hover_data=hover_data)

    fig.update_traces(marker=dict(size=9))

    fig.update_layout(mapbox_style="carto-positron",
                      margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)