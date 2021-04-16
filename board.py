import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv(os.path.join(os.path.abspath(os.curdir), 'games.csv'))
df = df.dropna()
df = df.loc[df['Year_of_Release'] >= 2000].sort_values(by=['Year_of_Release', 'Platform'])

grp = df.groupby(["Year_of_Release", "Platform"])["Name"].count()

main_frame = pd.merge(df, grp, how='outer', on=['Year_of_Release', 'Platform'])
main_frame = main_frame.rename(columns={'Name_y': 'Games quantity', 'Year_of_Release': 'Year of Release',
                                        'Critic_Score': 'Critic Score', 'User_Score': 'User Score'})

available_genres = main_frame['Genre'].unique()
available_ratings = main_frame['Rating'].unique()

app.layout = html.Div([
    html.Div([

        html.Div([
            html.H5("Games statistics"),
            html.H6("You can adjust genre, rating and time interval filters to see the number of games released"),
            html.Br()]),

        html.Div([dcc.Dropdown(
            id='genre_filter',
            options=[{'label': i, 'value': i} for i in available_genres],
            value='Shooter',
            multi=True
        )
        ],
            style={'width': '48%', 'display': 'inline-block'}),

        html.Div([dcc.Dropdown(
            id='rating_filter',
            options=[{'label': i, 'value': i} for i in available_ratings],
            value='E',
            multi=True
        )
        ],
            style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    html.Div(id='games_quantity',
             children=[
                 html.Br()
                 # html.P("Selected games quantity: "),
                 # html.Br()
             ]
             ),

    html.Div(children=[
        dcc.Graph(id='graph_1', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='graph_2', style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.RangeSlider(
        id='year_slider',
        min=main_frame['Year of Release'].min(),
        max=main_frame['Year of Release'].max(),
        value=[main_frame['Year of Release'].min(), main_frame['Year of Release'].max()],
        marks={int(year): str(round(year)) for year in main_frame['Year of Release'].unique()}
    )
])

chosen_genre_list = []
chosen_rating_list = []


@app.callback(
    Output('games_quantity', 'children'),
    Output('graph_1', 'figure'),
    Output('graph_2', 'figure'),
    [Input('genre_filter', 'value'),
     Input('rating_filter', 'value'),
     Input('year_slider', 'value')]
)
def update_dash(selected_genre, selected_rating, year_interval):
    chosen_genre_list.append(selected_genre)
    chosen_rating_list.append(selected_rating)
    genres = [i for i in available_genres if i in chosen_genre_list[-1]]
    ratings = [i for i in available_ratings if i in chosen_rating_list[-1]]
    years = list(range(year_interval[0], year_interval[1]))

    if chosen_genre_list[-1] and chosen_rating_list[-1]:
        abs_main_frame = ((main_frame.loc[main_frame['Genre'].isin(genres)]).loc[main_frame['Rating'].isin(ratings)]).loc[main_frame['Year of Release'].isin(years)]
    elif chosen_genre_list[-1]:
        abs_main_frame = (main_frame.loc[main_frame['Genre'].isin(genres)]).loc[main_frame['Year of Release'].isin(years)]
    elif chosen_rating_list[-1]:
        abs_main_frame = (main_frame.loc[main_frame['Rating'].isin(ratings)]).loc[main_frame['Year of Release'].isin(years)]
    else:
        abs_main_frame = main_frame.loc[main_frame['Year of Release'].isin(years)]
    x_ax = abs_main_frame["Year of Release"]
    y_ax = abs_main_frame["Games quantity"]
    fig_1 = px.area(
        abs_main_frame,
        x=x_ax,
        y=y_ax,
        color="Platform"
    )
    df1 = abs_main_frame.sort_values('User Score')
    fig_2 = px.scatter(
        df1,
        x=df1['User Score'],
        y='Critic Score',
        color='Genre'
    )
    text_display = u'Selected games quantity: {}'.format(abs_main_frame.size)
    print(text_display)
    return text_display, fig_1, fig_2


if __name__ == '__main__':
    app.run_server(debug=True)
