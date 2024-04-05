import dash
from dash import dcc, html, Input,Output, dash_table
import seaborn as sns
import plotly.express as px
from dash.exceptions import PreventUpdate
import pandas as pd



twitter_df=pd.read_csv('ProcessedTweets.csv')


# Get the categorical columns
categorical_columns = twitter_df.select_dtypes(include=['object', 'category']).columns.tolist()

# Get the numeric columns
numeric_columns = twitter_df.select_dtypes(include=['number']).columns.tolist()

# Get the months
months = twitter_df['Month'].unique()

#graph components
dropdown=html.Div(className="child1_1_1",children=[dcc.Dropdown(id='monthDropdown',options=months, value=months[0])])
rangeslider1=html.Div(className="child1_1_1",children=[dcc.RangeSlider(id='sentimentSlider',
                                                                       min=twitter_df['Sentiment'].min(),max=twitter_df['Sentiment'].max(),
                                                                       value=[twitter_df['Sentiment'].min(),twitter_df['Sentiment'].max()],
                                                                        marks={int(twitter_df['Sentiment'].min()) : str(twitter_df['Sentiment'].min()), int(twitter_df['Sentiment'].max()) : str(twitter_df['Sentiment'].max()) })])
rangeslider2=html.Div(className="child1_1_1",children=[dcc.RangeSlider(id='subjectivitySlider',
                                                                       min=twitter_df['Subjectivity'].min(),max=twitter_df['Subjectivity'].max(),
                                                                       value=[twitter_df['Subjectivity'].min(),twitter_df['Subjectivity'].max()],
                                                                        marks={int(twitter_df['Subjectivity'].min()) : str(twitter_df['Subjectivity'].min()), int(twitter_df['Subjectivity'].max()) : str(twitter_df['Subjectivity'].max()) })])


app = dash.Dash(__name__)

server = app.server

app.layout = html.Div(className="parent", children=[
    html.Div(className="child1",children=[html.Div(["Month ", dropdown, "Sentiment Score " ,rangeslider1, "Subjectivity Score ",rangeslider2], className="child1_1"),
                                          html.Div(dcc.Graph(id='graph'), className="child1_2"),
                                          dash_table.DataTable(id='selected-tweets',columns=[{"name": "RawTweet", "id": "RawTweet"}],data=[],
                                                               style_data={'whiteSpace': 'normal','height': 'auto'},
                                                               style_table={'height': '350px', 'overflowY': 'auto', "overflowX": "auto"}, 
                                                               style_cell={'textAlign': 'center'}, 
                                                               style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                                                               page_current=0, page_size=10, page_action='custom')]
                                        )]
)



# Define callback function for graph
@app.callback(Output('graph', 'figure'),
              [Input('monthDropdown', 'value'),Input('sentimentSlider', 'value'),Input('subjectivitySlider', 'value')])
def update_graph(month, sentiment, subjectivity):
    if(month is not None and sentiment is not None and subjectivity is not None):
        filtered_df = twitter_df[(twitter_df['Month'] == month) & (twitter_df['Sentiment'] >= sentiment[0]) & (twitter_df['Sentiment'] <= sentiment[1]) & 
                                 (twitter_df['Subjectivity'] >= subjectivity[0]) & (twitter_df['Subjectivity'] <= subjectivity[1])]
        fig = px.scatter(filtered_df, x='Sentiment', y='Subjectivity')
        fig.update_layout(dragmode='lasso', 
                          modebar={
                            'orientation': 'v',
                            'bgcolor': '#E9E9E9',
                            'color': 'black',
                            'activecolor': '#9ED3CD'
                        }
            )
        return fig
    else:
        raise PreventUpdate

@app.callback(Output('selected-tweets', 'data'),[Input('graph', 'selectedData'), Input('selected-tweets', "page_current"), Input('selected-tweets', "page_size")])
def update_table(selectedData,page_current, page_size ):
    if selectedData is not None:
        indices = [point['pointIndex'] for point in selectedData['points']]
        selected_df = twitter_df.iloc[indices][['RawTweet']]
        paged_list = selected_df.iloc[page_current*page_size:(page_current+1)*page_size]
        return paged_list.to_dict('records')
    return []

if __name__ == '__main__':
    app.run_server(debug=False)

