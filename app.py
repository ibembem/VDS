import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Use your dataframe
df = pd.read_csv('df_final_cleaned.csv') # Загружаем сохраненный файл

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Global Tourism Impact Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        html.P("Select/Highlight countries on the Map to update the other charts (Brushing & Linking)."),
    ], style={'padding': '10px', 'textAlign': 'center'}),

    # Top Row: World Map
    html.Div([
        dcc.Graph(
            id='world-map',
            figure=px.choropleth(
                df, 
                locations="ISO3_Code", 
                color="Tourism_Density",
                hover_name="Country_Name", # FIXED: Changed from 'Country' to 'Country_Name'
                title="Global Tourism Density",
                color_continuous_scale=px.colors.sequential.Plasma
            ).update_layout(clickmode='event+select', margin={"r":0,"t":40,"l":0,"b":0})
        )
    ], style={'width': '100%', 'height': '400px'}),

    # Bottom Row: Three Charts
    html.Div([
        html.Div([
            dcc.Graph(id='scatter-gdp')
        ], style={'width': '33%'}),
        
        html.Div([
            dcc.Graph(id='scatter-regression')
        ], style={'width': '33%'}),

        html.Div([
            dcc.Graph(id='bar-burden')
        ], style={'width': '33%'}),
    ], style={'display': 'flex', 'marginTop': '20px'})
])

# --- Brushing & Linking Logic ---
@app.callback(
    [Output('scatter-gdp', 'figure'),
     Output('scatter-regression', 'figure'),
     Output('bar-burden', 'figure')],
    [Input('world-map', 'selectedData')]
)
def update_charts(selectedData):
    filtered_df = df
    if selectedData and 'points' in selectedData:
        selected_iso = [p['location'] for p in selectedData['points']]
        filtered_df = df[df['ISO3_Code'].isin(selected_iso)]

    # Chart 1: Wealth vs Volume
    fig1 = px.scatter(filtered_df, x="GDP_per_capita", y="Inbound_Tourists", 
                     hover_name="Country_Name", # FIXED
                     title="Wealth vs. Volume", log_x=True, template="plotly_white")
    
    # Chart 2: Regression Model
    fig2 = px.scatter(filtered_df, x="Population_Density", y="Tourism_Density", 
                     trendline="ols", 
                     hover_name="Country_Name", # FIXED
                     title="Density Correlation (Model)", template="plotly_white")
    
    # Chart 3: Top 10 Burden
    top_10 = filtered_df.nlargest(10, 'Tourists_per_Resident')
    fig3 = px.bar(top_10, x="Country_Name", # FIXED
                  y="Tourists_per_Resident", 
                  title="Top 10 Local Burden", template="plotly_white")

    return fig1, fig2, fig3
    
if __name__ == '__main__':
    # 'run_server' is obsolete in newer Dash versions; 'run' is the new standard.
    app.run(debug=True)
