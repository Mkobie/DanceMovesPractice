from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, dcc

from DanceMove import DanceMoveCollection

# todo: add moves from
#  https://thebluesroom.com/courses/side-by-side/
#   and add basic slow taps and quick quicks.

grouping_titles = ["Basic turns", "Ballroom blues", "Ballroom blues - turns", "Close embrace", "Close embrace - spins"]
mixer_moves = {"all": grouping_titles,
               "some": ["Basic turns", "Ballroom blues", "Ballroom blues - turns"],
               "a few": ["Basic turns"]}

assets_folder = Path.cwd() / 'assets'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

dance_moves = DanceMoveCollection()

def generate_move_button_row(move):
    return html.Div([
        dbc.Button(move.name, id={'type': 'move-button', 'index': f"{move.name}"}, color="secondary", className="flex-grow-1"),
        dbc.Button("\U0001F855", id={'type': 'lesson-button', 'index': f"{move.name}"}, href=f"{move.lesson}", target="_blank", style={'display': 'none'}, color="secondary", className="flex-shrink-1"),
        dbc.Checkbox(id={'type': 'move-checkbox', 'index': f"{move.name}"}, style={'margin-left': '10px'}, value=False),
    ], className="d-flex align-items-center mb-1 ms-4")

def column_of_move_button_rows(title):
    moves_for_column = [move for move in dance_moves.moves if move.grouping == title]
    return html.Div([
        html.Div([dbc.Checkbox(id={'type': 'group-checkbox', 'index': f"{title}"}, value=False), html.H6(title, className="card-title")], className="d-flex align-items-center mb-1"),
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
            html.H1("Blues Moves Practice"),
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
            dbc.Row([
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Mix me a practice session with"),
                            dbc.DropdownMenu(
                                    label="-", id="mixer-moves", color="secondary",
                                    children=[
                                        dbc.DropdownMenuItem(item, id={'type': 'mixer-moves-dropdown-item', 'index': item}) for item in mixer_moves.keys()
                                    ],
                                ),
                            dbc.InputGroupText("moves and"),
                            dbc.DropdownMenu(
                                    label="some", id="mixer-basics", color="secondary",
                                    children=[
                                        dbc.DropdownMenuItem(item, id={'type': 'mixer-basics-dropdown-item', 'index': item}) for item in ["no", "some", "a lot of"]
                                    ],
                                ),
                            dbc.InputGroupText("basics at"),
                            dbc.Input(value=75, type="number", id="mixer-bpm"),
                            dbc.InputGroupText("bpm"),
                        ],
                    ), width=9
                ),
                dbc.Col(
                    dbc.Button("Let's go!", id="mixer-start", color="secondary")
                ),
            ])
        ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top',
                  'padding': '20px', 'box-sizing': 'border-box'}),

        html.Div([
            dcc.Store(id='group-checkbox-store', data=dict(zip(grouping_titles, [False for title in grouping_titles]))),
            dcc.Store(id='move-checkbox-store', data=dict(zip([move.name for move in dance_moves.moves], [False for move in dance_moves.moves]))),
            groups_of_moves()
        ],
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


@app.callback(
    [
        Output("mixer-moves", "label"),
        Output({'type': 'group-checkbox', 'index': dash.dependencies.ALL}, 'value'),
        Output({'type': 'move-checkbox', 'index': dash.dependencies.ALL}, 'value'),
        Output("group-checkbox-store", "data"),
        Output("move-checkbox-store", "data"),
    ],
    [
        Input({'type': 'mixer-moves-dropdown-item', 'index': dash.dependencies.ALL}, 'n_clicks'),
        Input({'type': 'group-checkbox', 'index': dash.dependencies.ALL}, 'value'),
        Input({'type': 'move-checkbox', 'index': dash.dependencies.ALL}, 'value'),
    ],
    [
        State("mixer-moves", "label"),
        State("group-checkbox-store", "data"),
        State("move-checkbox-store", "data"),

    ],
    prevent_initial_call=True
)
def update_mixer_moves_selection(n_clicks, group_checkbox_values, move_checkbox_values, mixer_moves_label, group_checkbox_previous_values_dict, move_checkbox_previous_values_dict):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    selection_id = ctx.triggered[0]['prop_id'].split('.')[0]
    input = eval(selection_id)['index']

    selected_mixer_value = mixer_moves_label
    group_checkbox_new_values_dict = group_checkbox_previous_values_dict
    group_checkbox_new_values = group_checkbox_previous_values_dict.values()
    move_checkbox_new_values_dict = move_checkbox_previous_values_dict
    move_checkbox_new_values = move_checkbox_previous_values_dict.values()

    if input in mixer_moves.keys():
        selected_mixer_value = input
        group_checkbox_new_values = [True if title in mixer_moves[selected_mixer_value] else False for title in grouping_titles]
        move_checkbox_new_values = [True if move.grouping in mixer_moves[selected_mixer_value] else False for move in dance_moves.moves]
        move_checkbox_new_values_dict = dict(zip(move_checkbox_previous_values_dict.keys(), move_checkbox_new_values))
        group_checkbox_new_values_dict = dict(zip(grouping_titles, group_checkbox_new_values))
    elif input in grouping_titles:
        group_checkbox_new_values = group_checkbox_values
        group_checkbox_new_values_dict = dict(zip(grouping_titles, group_checkbox_new_values))
        move_checkbox_new_values = [group_checkbox_new_values_dict[input] if dance_moves.get_grouping_from_name(move_name) == input else prev_value for move_name, prev_value in move_checkbox_previous_values_dict.items()]
        move_checkbox_new_values_dict = dict(zip(move_checkbox_previous_values_dict.keys(), move_checkbox_new_values))
        selected_mixer_value = "custom"
    elif input in [move.name for move in dance_moves.moves]:
        move_checkbox_new_values = move_checkbox_values
        move_checkbox_new_values_dict = dict(zip(move_checkbox_previous_values_dict.keys(), move_checkbox_new_values))
        moves_in_grouping = [move_name for move_name in move_checkbox_previous_values_dict.keys() if dance_moves.get_grouping_from_name(move_name) == dance_moves.get_grouping_from_name(input)]
        checkbox_values_for_moves_in_grouping = {k: move_checkbox_new_values_dict[k] for k in moves_in_grouping}.values()
        group_checkbox_new_values = [all(checkbox_values_for_moves_in_grouping) if title == dance_moves.get_grouping_from_name(input) else prev_value for title, prev_value in group_checkbox_previous_values_dict.items()]
        group_checkbox_new_values_dict = dict(zip(grouping_titles, group_checkbox_new_values))
        selected_mixer_value = "custom"

    return selected_mixer_value, group_checkbox_new_values, move_checkbox_new_values, group_checkbox_new_values_dict, move_checkbox_new_values_dict


if __name__ == '__main__':
    app.run_server(debug=True)
