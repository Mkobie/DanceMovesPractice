from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, dcc

from DanceMove import DanceMoveCollection

# todo: add moves from
#  https://thebluesroom.com/courses/side-by-side/

grouping_titles = ["Basic turns", "Ballroom blues", "Ballroom blues - turns", "Close embrace", "Close embrace - spins"]
assets_folder = Path.cwd() / 'assets'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

dance_moves = DanceMoveCollection()

def button_group(title):
    moves_for_group = [move for move in dance_moves.moves if move.grouping == title]
    return dbc.Col([
        html.H6(title, className="card-title"),
        dbc.ButtonGroup([
            dbc.Button(move.name, id={'type': 'video-button', 'index': f"{move.name}"}, color="secondary",
                       className="mb-2")
            for move in moves_for_group
        ], vertical=True)
    ], className="d-grid gap-2", width=12)

def generate_button_groups():
    button_groups = []
    for i, entry in enumerate(grouping_titles):
        button_groups.append(button_group(grouping_titles[i]))
    return button_groups

app.layout = html.Div([
    html.Div([

        html.Div([
            html.H1("Title"),
            dcc.Store(id='current-video', data=dance_moves.moves[0].name),
            html.Video(
                id="video-player",
                src=f"/assets/{dance_moves.moves[0].name}.mp4",
                controls=True,
                autoPlay=True,
                loop=True,
                style={"width": "100%", "height": "auto"}
            ),
            html.Div("Controls"),
        ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top',
                  'padding': '20px', 'box-sizing': 'border-box'}),

        html.Div([
            dbc.Row(generate_button_groups()),
        ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top',
                  'padding': '20px', 'box-sizing': 'border-box',
                  'height': '100vh', 'overflow-y': 'scroll'}),
    ])
])


@callback(
[Output("video-player", "src"),
     Output("current-video", "data")],
    Input({'type': 'video-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_video(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    move_name = eval(button_id)['index']

    return f"/assets/{move_name}.mp4", move_name


@app.callback(
    Output({'type': 'video-button', 'index': dash.dependencies.ALL}, 'color'),
    Input('current-video', 'data')
)
def update_button_colors(current_video):
    # if not current_video:
    #     return ['secondary'] * len(dance_moves.moves)  # Default color

    return ['primary' if move.name == current_video else 'secondary' for move in dance_moves.moves]



if __name__ == '__main__':
    app.run_server(debug=True)
