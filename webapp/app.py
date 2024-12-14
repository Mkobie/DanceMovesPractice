import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, dcc

from setup import mixer_btn_names, show_video_dropdown, dance_moves, default_interval
from webapp.move_list import move_list
from webapp.navbar import navbar
from webapp.player_and_mixer import player_and_mixer
from webapp.server import app

# todo:
#   Metronome isn't consistent, esp when move changes. Possible to make it smoother? (separate it again?)
#   Make it possible to use "up to move" selection dropdown even while mixer is running?
#   Smooth out video player reload on new src (preload? use vid lib eg videos.js or plyr?)
#   Iron out video automatic start / stop in different contexts
#   Fix paths s.t. can run from main.py or app.py

# todo: add moves from
#  https://thebluesroom.com/courses/side-by-side/


layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(navbar)
        ]),

        dbc.Row([
            dbc.Col(player_and_mixer, style={"maxHeight": "calc(100vh - 70px)", "overflow": "hidden"}),
            dbc.Col(move_list, width=4),
        ])
    ], fluid=True),

    dcc.Store(id="current-move", data=dance_moves.moves[0].name),
])



def run():
    app.layout = layout
    app.run_server(debug=True)


@callback(
    Output("current-move", "data", allow_duplicate=True),
    Input({'type': 'move-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def set_current_move(active_move_button):
    # todo: goes in app if current-move is used by mixer, else in move_list if only for showing move list clicks?
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    clicked_move_name = eval(triggered_id)['index']
    return clicked_move_name


@callback(
    [
        Output({'type': 'move-button', 'index': dash.dependencies.ALL}, 'color'),
        Output({'type': 'lesson-button', 'index': dash.dependencies.ALL}, 'style'),
    ],
    Input("current-move", "data"),
)
def show_current_move_in_move_list(current_move):
    # todo: goes in move_list?
    button_colors = ['primary' if move.name == current_move else 'secondary' for move in dance_moves.moves]
    href_visibility = [{'display': 'block'} if move.name == current_move else {'display': 'none'} for move in dance_moves.moves]

    return button_colors, href_visibility


@callback(
    Output("video-player", "src"),
    Input("current-move", "data"),
    [
        State("mixer-count-interval", "disabled"),
        State("mixer-show-vid", "label"),
    ]
)
def show_current_move_in_video_player(current_move, mixer_disabled, show_mixer_vid):
    # todo: goes in player? Naaaa... cross contaminated with mixer stuff
    if mixer_disabled or (not mixer_disabled and show_mixer_vid == show_video_dropdown[1]):
        return f"assets/{current_move}.mp4"
    else:
        return dash.no_update


@app.callback(
    [
        Output("mixer-button", "children"),
        Output("mixer-button", "color"),
        Output({'type': 'group-checkbox', 'index': dash.dependencies.ALL}, 'disabled'),
        Output({'type': 'move-checkbox', 'index': dash.dependencies.ALL}, 'disabled'),
        Output("mixer-moves", "disabled"),
        Output("metronome-button", "disabled"),
        Output({'type': 'move-button', 'index': dash.dependencies.ALL}, 'disabled'),
        Output({'type': 'lesson-button', 'index': dash.dependencies.ALL}, 'disabled'),
    ],
    Input("mixer-button", "n_clicks"),
    State("mixer-button", "children"),
    prevent_initial_call=True
)
def manage_layout_on_mixer_button_press(n_clicks, mixer_button_name):
    if mixer_button_name == mixer_btn_names["start"]:
        # Start the mixer
        mixer_button_name = mixer_btn_names["stop"]
        mixer_button_color = 'primary'
        group_checkbox_disabled = [True for group in dance_moves.groups]
        move_checkbox_disabled = [True for move in dance_moves.moves]
        mixer_moves_disabled = True
        metronome_button_disabled = False
        move_list_button_enable = [True for move in dance_moves.moves]
    else:
        # Stop the mixer
        mixer_button_name = mixer_btn_names["start"]
        mixer_button_color = 'secondary'
        group_checkbox_disabled = [False for group in dance_moves.groups]
        move_checkbox_disabled = [False for move in dance_moves.moves]
        mixer_moves_disabled = False
        metronome_button_disabled = False
        move_list_button_enable = [False for move in dance_moves.moves]

    return mixer_button_name, mixer_button_color, group_checkbox_disabled, move_checkbox_disabled, mixer_moves_disabled, metronome_button_disabled, move_list_button_enable, move_list_button_enable


@app.callback(
    [
        Output("metronome-button", "children"),
        Output("metronome-interval", "interval"),
        Output("metronome-interval", "disabled"),

        Output("mixer-count-interval", "disabled"),
        Output("mixer-count-interval", "interval"),
        Output("mixer-sound", "src"),

        Output("current-move", "data", allow_duplicate=True),
    ],
    [
        Input("metronome-button", "n_clicks"),
        Input("metronome-bpm-input", "value"),

        Input("mixer-button", "n_clicks"),
        Input("mixer-count-interval", "n_intervals"),
    ],
    [
        State("metronome-interval", "disabled"),
        State("mixer-button", "children"),
    ],
    prevent_initial_call=True
)
def manage_mixer_and_metronome(metronome_n_clicks, bpm, mixer_n_clicks, n_intervals, metronome_is_disabled, mixer_button_name):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    metronome_button_text = metronome_interval = metronome_disabled = mixer_disabled = mixer_interval = move_file = current_move = dash.no_update

    match triggered_id:
        case "metronome-button":
            if metronome_is_disabled:
                metronome_interval = 60000 / bpm
                metronome_disabled = False
                metronome_button_text = "\U0000266a..."
            else:
                metronome_disabled = True
                metronome_button_text = "\U0000266a"

        case "metronome-bpm-input":
            if not metronome_is_disabled:
                metronome_interval = 60000 / bpm

        case "mixer-button":
            if mixer_button_name == mixer_btn_names["start"]:
                mixer_disabled = False
                mixer_interval = default_interval["ms"]/2
            else:
                mixer_disabled = True

        case "mixer-count-interval":
            new_move = dance_moves.pop_current_move()
            move_file = f"/assets/{new_move.name}.wav"
            mixer_interval = new_move.counts * (60000 / bpm)  # todo: maybe bpm_interval would be more useful?
            current_move = new_move.name

    return metronome_button_text, metronome_interval, metronome_disabled, mixer_disabled, mixer_interval, move_file, current_move


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
    run()
