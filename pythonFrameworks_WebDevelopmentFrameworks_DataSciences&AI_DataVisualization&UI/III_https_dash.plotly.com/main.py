'''ModuleNotFoundError: No module named 'dash'  '''
from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Hello WorldTDEVYK3'),
    html.Div(children='''
        Dash: A web application framework for your data.
    ''')
])

if __name__ == '__main__':
    app.run(debug=True)
