from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, dcc

from DanceMove import DanceMoveCollection

# todo: add moves from
#  https://thebluesroom.com/courses/side-by-side/
#   and add basic slow taps and quick quicks.

grouping_titles = ["Basic turns", "Ballroom blues", "Ballroom blues - turns", "Close embrace", "Close embrace - spins"]
assets_folder = Path.cwd() / 'assets'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

dance_moves = DanceMoveCollection()

def generate_move_button_row(move):
    return html.Div([
        dbc.Button(move.name, id={'type': 'move-button', 'index': f"{move.name}"}, color="secondary", className="flex-grow-1"),
        dbc.Button("\U0001F855", id={'type': 'lesson-button', 'index': f"{move.name}"}, href=f"{move.lesson}", target="_blank", style={'display': 'none'}, color="secondary", className="flex-shrink-1"),
        dbc.Checkbox(id={'type': 'move-checkbox', 'index': f"{move.name}"}, style={'margin-left': '10px'}),
    ], className="d-flex align-items-center mb-1 ms-4")

def column_of_move_button_rows(title):
    moves_for_column = [move for move in dance_moves.moves if move.grouping == title]
    return html.Div([
        html.Div([dbc.Checkbox(id={'type': 'group-checkbox', 'index': f"{title}"}), html.H6(title, className="card-title")], className="d-flex align-items-center mb-1"),
        html.Div([generate_move_button_row(move) for move in moves_for_column])
    ])

def groups_of_moves():
    groups = []
    for title in grouping_titles:
        groups.append(column_of_move_button_rows(title))
    return html.Div(groups)

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

        html.Div([groups_of_moves()],
                 style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top',
                  'padding': '20px', 'box-sizing': 'border-box',
                  'height': '100vh', 'overflow-y': 'scroll'}),
    ])
])


@callback(
[Output("video-player", "src"),
     Output("current-video", "data")],
    Input({'type': 'move-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
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
    [
        Output({'type': 'move-button', 'index': dash.dependencies.ALL}, 'color'),
        Output({'type': 'lesson-button', 'index': dash.dependencies.ALL}, 'style'),
    ],
    Input('current-video', 'data')
)
def update_button_row_formatting(current_video):
    colors = ['primary' if move.name == current_video else 'secondary' for move in dance_moves.moves]
    visibility = [{'display': 'block'} if move.name == current_video else {'display': 'none'} for move in dance_moves.moves]
    return colors, visibility


if __name__ == '__main__':
    app.run_server(debug=True)
