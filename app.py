from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, dcc

# todo:
#   Add toggle for video y/n during practice mix
#   Decide how want metronome and mix to play together, or not at all
#   Maybe also add option for verbal count (1,2,3,4,5,6,7,8) in background
#   Smooth out video player reload on new src (preload? use vid lib eg videos.js or plyr?)
#   Check how to reduce memory for faster / more consistent response of count / move audio
#       Maybe have 2 audio players, swap back and forth?
#   Review which elements users can interact with when mixing (disable video pause? make stop button more colourful?)
#   If user starts mix with no moves selected, then select them all?
#   Mix up to xyz group instead of few/all
#   Decide about audio/video start on 1 vs audio in anticipation of move (maybe record self saying prompts to music)
#   Make title into banner across top
#   Separate code into multiple files, may be make a flow chart

from DanceMove import DanceMoveCollection
from MoveMixer import generate_dance_sequence

# todo: add moves from
#  https://thebluesroom.com/courses/side-by-side/
#   and add basic slow taps and quick quicks.

grouping_titles = ["Basic turns", "Ballroom blues", "Ballroom blues - turns", "Close embrace", "Close embrace - spins"]
mixer_moves = {"all": grouping_titles,
               "some": ["Basic turns", "Ballroom blues", "Ballroom blues - turns"],
               "a few": ["Basic turns"]}
bmp_limits = {"min": 30, "max": 300}
mixer_btn_names = {"start": "Let's go!", "stop": "Aaand stop!"}

default_interval = {"bpm": 75}
default_interval["ms"] = 60000 / default_interval["bpm"]


assets_folder = Path.cwd() / 'assets'
metronome_audio = "/assets/Perc_MetronomeQuartz_hi.wav"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

dance_moves = DanceMoveCollection()

def generate_move_button_row(move):
    return html.Div([
        dbc.Button(move.name, id={'type': 'move-button', 'index': f"{move.name}"}, color="secondary", className="flex-grow-1", n_clicks=0),
        dbc.Button("\U0001F855", id={'type': 'lesson-button', 'index': f"{move.name}"}, href=f"{move.lesson}", target="_blank", style={'display': 'none'}, color="secondary", className="flex-shrink-1"),
        dbc.Checkbox(id={'type': 'move-checkbox', 'index': f"{move.name}"}, style={'margin-left': '10px'}, value=False),
    ], className="d-flex align-items-center mb-1 ms-4")

def generate_column_of_move_button_rows(title):
    moves_for_column = [move for move in dance_moves.moves if move.grouping == title]
    return html.Div([
        html.Div([dbc.Checkbox(id={'type': 'group-checkbox', 'index': f"{title}"}, value=False), html.H6(title, className="card-title")], className="d-flex align-items-center mb-1"),
        html.Div([generate_move_button_row(move) for move in moves_for_column])
    ])

def generate_groups_of_moves():
    groups = []
    for title in grouping_titles:
        groups.append(generate_column_of_move_button_rows(title))
    return html.Div(groups)

app.layout = html.Div([
    html.Div([

        html.Div([
            html.H1("Blues Moves Practice"),
            html.Video(
                id="video-player",
                src=f"/assets/{dance_moves.moves[0].name}.mp4",
                controls=True,
                autoPlay=True,
                loop=True,
                style={"width": "100%", "height": "auto"}
            ),
            dbc.Row([
                html.H6("Move mixer"),
                dbc.Col([
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Practice"),
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
                            dbc.Input(id="metronome-bpm-input", type="number", value=default_interval["bpm"], min=bmp_limits["min"], max=bmp_limits["max"], step=1, debounce=True),
                            dbc.InputGroupText("bpm"),
                            dbc.Button("\U0000266a", id="metronome-button", color="secondary", ),
                            dbc.DropdownMenu(
                                    label="", id="mixer-show-vid", color="secondary",
                                    children=[
                                        dbc.DropdownMenuItem(item, id={'type': 'mixer-show-vid-dropdown-item', 'index': item}) for item in [" ", "with videos"]
                                    ],
                                ),
                        ],
                    ),
                    dcc.Interval(id="metronome-interval", interval=600, n_intervals=0, disabled=True),
                    html.Div(id="metronome-dummy", style={'display': 'none'}),
                    html.Audio(id="metronome-sound", src=metronome_audio, controls=False,
                               style={'display': 'none'}),
                ], width=8),
                dbc.Col([
                    dbc.Button(mixer_btn_names["start"], id="mixer-button", color="secondary"),
                    dcc.Interval(id="mixer-count-interval", interval=default_interval["ms"], n_intervals=0, disabled=True),
                    html.Div(id="mixer-dummy", style={'display': 'none'}),
                    html.Audio(id="mixer-sound", controls=False, style={'display': 'none'}),
                    dcc.Store(id="current-move", data=None),
                    dcc.Store(id="current-sequence", data=[]),
                    dcc.Store(id="current-move-countdown", data=None),
                    dcc.Store(id="mixer-available-moves", data=[]),
                ]),
            ], className="mt-3")
        ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top',
                  'padding': '20px', 'box-sizing': 'border-box'}),

        html.Div([
            html.H6("Move list"),
            dcc.Store(id='group-checkbox-store', data=dict(zip(grouping_titles, [False for title in grouping_titles]))),
            dcc.Store(id='move-checkbox-store', data=dict(zip([move.name for move in dance_moves.moves], [False for move in dance_moves.moves]))),
            generate_groups_of_moves()
        ],
                 style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top',
                  'padding': '20px', 'box-sizing': 'border-box',
                  'height': '100vh', 'overflow-y': 'scroll'}),
    ])
])


@callback(
    [
        Output("video-player", "src"),
        Output({'type': 'move-button', 'index': dash.dependencies.ALL}, 'color'),
        Output({'type': 'lesson-button', 'index': dash.dependencies.ALL}, 'style'),
    ],
    [
        Input({'type': 'move-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
        Input("current-move", "data"),
    ],
    prevent_initial_call=True
)
def show_selected_move(n_clicks, current_move):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == "current-move":
        clicked_move_name = current_move
    else:
        clicked_move_name = eval(triggered_id)['index']

    video_file = f"/assets/{clicked_move_name}.mp4"
    button_colors = ['primary' if move.name == clicked_move_name else 'secondary' for move in dance_moves.moves]
    href_visibility = [{'display': 'block'} if move.name == clicked_move_name else {'display': 'none'} for move in
                  dance_moves.moves]

    return video_file, button_colors, href_visibility


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
def update_checkboxes_from_mixer_moves_selection(n_clicks, group_checkbox_values, move_checkbox_values, mixer_moves_label, group_checkbox_previous_values_dict, move_checkbox_previous_values_dict):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    selection_id = ctx.triggered[0]['prop_id'].split('.')[0]
    input = eval(selection_id)['index']

    selected_mixer_value = mixer_moves_label
    group_checkbox_new_values_dict = group_checkbox_previous_values_dict
    group_checkbox_new_values = list(group_checkbox_previous_values_dict.values())
    move_checkbox_new_values_dict = move_checkbox_previous_values_dict
    move_checkbox_new_values = list(move_checkbox_previous_values_dict.values())

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


@app.callback(
    [
        Output("metronome-interval", "interval"),
        Output("mixer-count-interval", "interval"),
        Output("metronome-interval", "disabled"),
        Output("metronome-button", "children"),
    ],
    [
        Input("metronome-button", "n_clicks"),
        Input("metronome-bpm-input", "value"),
    ],
    [
        State("metronome-interval", "disabled"),
    ],
    prevent_initial_call=True
)
def control_metronome(n_clicks, bpm, is_disabled):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    metronome_interval = dash.no_update
    metronome_disabled = dash.no_update
    metronome_button_text = dash.no_update

    if triggered_id == "metronome-button":
        if is_disabled:
            metronome_interval = 60000 / bpm
            metronome_disabled = False
            metronome_button_text = "\U0000266a..."
        else:
            metronome_disabled = True
            metronome_button_text = "\U0000266a"

    elif triggered_id == "metronome-bpm-input":
        if not is_disabled:
            metronome_interval = 60000 / bpm

    return metronome_interval, metronome_interval, metronome_disabled, metronome_button_text


app.clientside_callback(
    '''
    function(n_intervals) {
        const audioElement = document.querySelector('#metronome-sound');
        if (audioElement) {
            audioElement.currentTime = 0;  // Reset the audio to the beginning
            audioElement.play();  // Play the sound on each interval tick
        }
        return null;
    }
    ''',
    Output('metronome-dummy', 'children'),
    Input('metronome-interval', 'n_intervals'),
    prevent_initial_call=True
)

@app.callback(
    [
        Output("mixer-button", "children"),
        Output({'type': 'group-checkbox', 'index': dash.dependencies.ALL}, 'disabled'),
        Output({'type': 'move-checkbox', 'index': dash.dependencies.ALL}, 'disabled'),
        Output("mixer-moves", "disabled"),
        Output("mixer-basics", "disabled"),
        Output("metronome-button", "disabled"),
    ],
    [
        Input("mixer-count-interval", "disabled"),

    ],
    [
        State({'type': 'group-checkbox', 'index': dash.dependencies.ALL}, 'value'),
        State({'type': 'move-checkbox', 'index': dash.dependencies.ALL}, 'value'),
    ],
    prevent_initial_call=True
)
def set_unset_mixer_mode_properties(mixer_disabled, group_checkbox_values, move_checkbox_values):
    if mixer_disabled:
        button_name = mixer_btn_names["start"]
        group_checkbox_disabled = [False for checkbox in group_checkbox_values]
        move_checkbox_disabled = [False for checkbox in move_checkbox_values]
        mixer_moves_disabled = False
        mixer_basics_disabled = False
        metronome_button_disabled = False
    else:
        button_name = mixer_btn_names["stop"]
        group_checkbox_disabled = [True for checkbox in group_checkbox_values]
        move_checkbox_disabled = [True for checkbox in move_checkbox_values]
        mixer_moves_disabled = True
        mixer_basics_disabled = True
        metronome_button_disabled = True

    return button_name, group_checkbox_disabled, move_checkbox_disabled, mixer_moves_disabled, mixer_basics_disabled, metronome_button_disabled


@app.callback(
    [
        Output("mixer-available-moves", "data"),
        Output("mixer-count-interval", "disabled"),
    ],
    [
        Input("mixer-button", "n_clicks"),
    ],
    [
        State("mixer-button", "children"),
        State("move-checkbox-store", "data"),
        State("mixer-count-interval", "disabled"),
    ],
    prevent_initial_call=True
)
def on_mixer_button_press(n_clicks, button_name, move_checkbox_values_dict, count_is_disabled):
    available_moves_by_name = dash.no_update

    if button_name == mixer_btn_names["start"]:
        mixer_disabled = False
        available_moves_by_name = [move_name for move_name, included in move_checkbox_values_dict.items() if included]
    else:
        mixer_disabled = True

    return available_moves_by_name, mixer_disabled


@app.callback(
    [
        Output("current-move", "data"),
        Output("current-sequence", "data"),
        Output("current-move-countdown", "data"),
    ],
    [
        Input("mixer-count-interval", "n_intervals"),
    ],
    [
        State("current-sequence", "data"),
        State("current-move-countdown", "data"),
        State("mixer-available-moves", "data"),
    ],
    prevent_initial_call=True
)
def count_down_and_sometimes_update_dance_move(n_intervals, upcoming_sequence, move_countdown, available_moves_by_name):
    new_move_name = dash.no_update
    print(f"{move_countdown}")

    if move_countdown is None:
        upcoming_sequence = ["1", "2", "3", "4", "5", "6"]

    elif move_countdown == 0:
        if len(upcoming_sequence) == 0:
            available_moves = [dance_moves.get_move_from_name(move_name) for move_name in available_moves_by_name]
            upcoming_sequence = generate_dance_sequence(available_moves)

    if not move_countdown:
        new_move_name = upcoming_sequence[0]
        if dance_moves.get_move_from_name(new_move_name):
            move = dance_moves.get_move_from_name(new_move_name)
            move_countdown = move.counts
        else:
            move_countdown = 1

        upcoming_sequence = upcoming_sequence[1:]
        print(f"Move: {new_move_name}")

    move_countdown = move_countdown - 1
    return new_move_name, upcoming_sequence, move_countdown


@app.callback(
    Output("mixer-sound", "src"),
    Input("current-move", "data"),
    prevent_initial_call=True
)
def update_mixer_audio(new_move_name):
    audio_file = f"/assets/{new_move_name}.wav"
    return audio_file


app.clientside_callback(
    '''
    function(n_intervals) {
        const audioElement = document.querySelector('#mixer-sound');
        if (audioElement) {
            audioElement.currentTime = 0;  // Reset the audio to the beginning
            audioElement.play();  // Play the sound on each interval tick
        }
        return null;
    }
    ''',
    Output('mixer-dummy', 'children'),
    Input('mixer-sound', 'src'),
    prevent_initial_call=True
)


if __name__ == '__main__':
    app.run_server(debug=True)
