import json
import random

import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, dcc, ctx, ALL
from dash.exceptions import PreventUpdate

from backend.DanceMove import DanceMoveCollection
from setup import mixer_btn_names, show_video_dropdown, default_interval, get_catalog, DEFAULT_STYLE, STYLES
from webapp.move_list import move_list
from webapp.navbar import navbar
from webapp.player_and_mixer import player_and_mixer

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(navbar)
        ]),

        dbc.Row([
            dbc.Col(player_and_mixer, style={"maxHeight": "calc(100vh - 70px)", "overflow": "hidden"}),
            dbc.Col(move_list, width=4),
        ])
    ], fluid=True),

    dcc.Store(id="style", data=DEFAULT_STYLE, storage_type="session"),
    dcc.Store(id="current-move", data=get_catalog(DEFAULT_STYLE).moves[0].name),
    dcc.Store(id="selected-moves", data=[False]*len(get_catalog(DEFAULT_STYLE).moves), storage_type="session"),
    dcc.Store(id="mixer-remaining", data=None, storage_type="session"),
])



def run():
    app.run(debug=True)


@callback(
    Output("style", "data"),
    Input({"type": "style-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def set_style(_n_clicks):
    if not ctx.triggered_id:
        raise PreventUpdate
    chosen = ctx.triggered_id["index"]
    return chosen


def get_color_for_item(name: str, active: bool) -> str:
    """Return the Bootstrap color for a given item when active/inactive."""
    if not active:
        return "secondary"

    special_colors = {
        "Salsa": "warning",
        "Blues": "primary",
    }
    return special_colors.get(name, "secondary")


@callback(
    Output({"type": "style-button", "index": ALL}, "color"),
    Input("style", "data"),
    prevent_initial_call=False,
)
def highlight_active_style_button(style):
    return [get_color_for_item(style_options, style_options == style) for style_options in STYLES]


@callback(
    Output("current-move", "data", allow_duplicate=True),
    Input({'type': 'move-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def set_current_move(active_move_button):
    ctx = dash.callback_context
    triggered_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    return triggered_id['index']


@callback(
    [
        Output({'type': 'move-button', 'index': dash.dependencies.ALL}, 'color'),
        Output({'type': 'lesson-button', 'index': dash.dependencies.ALL}, 'style'),
    ],
    [
        Input("current-move", "data"),
        Input("style", "data"),
        Input("move-list-body", "children"),
    ],
    [
        State({'type': 'move-button', 'index': dash.dependencies.ALL}, 'id'),
        State({'type': 'lesson-button', 'index': dash.dependencies.ALL}, 'id'),
    ]
)
def show_current_move_in_move_list(current_move, style, _children_ready, move_btn_ids, lesson_btn_ids):
    button_colors = [
        get_color_for_item(style, btn_id['index'] == current_move)
        for btn_id in (move_btn_ids or [])
    ]

    href_visibility = [
        {'display': 'block'} if btn_id['index'] == current_move else {'display': 'none'}
        for btn_id in (lesson_btn_ids or [])
    ]

    return button_colors, href_visibility


@callback(
    Output("video-source", "data"),
    [
        Input("current-move", "data"),
        Input("style", "data"),
    ],
    [
        State("mixer-count-interval", "disabled"),
        State("mixer-show-vid", "label"),
    ]
)
def show_current_move_in_video_player(current_move, style, mixer_disabled, show_mixer_vid):
    if mixer_disabled or (not mixer_disabled and show_mixer_vid == show_video_dropdown[1]):
        asset_path = dash.get_app().get_asset_url(f"{style}/{current_move}.mp4")
        return asset_path
    else:
        return dash.no_update


@app.callback(
    [
        Output("mixer-button", "children"),
        Output("mixer-button", "color"),
        Output("metronome-button", "disabled"),
        Output({'type': 'move-button', 'index': dash.dependencies.ALL}, 'disabled'),
        Output({'type': 'lesson-button', 'index': dash.dependencies.ALL}, 'disabled'),
    ],
    Input("mixer-button", "n_clicks"),
    [
        State("mixer-button", "children"),
        State("style", "data"),
        State({'type': 'move-button', 'index': dash.dependencies.ALL}, 'id'),
        State({'type': 'lesson-button', 'index': dash.dependencies.ALL}, 'id'),
    ],
    prevent_initial_call=True
)
def manage_layout_on_mixer_button_press(n_clicks, mixer_button_name, style, move_btn_ids, lesson_btn_ids):
    n_moves = len(move_btn_ids or [])
    n_lessons = len(lesson_btn_ids or [])

    if mixer_button_name == mixer_btn_names["start"]:
        # Start the mixer
        return mixer_btn_names["stop"], get_color_for_item(style, True), False, [True] * n_moves, [True] * n_lessons
    else:
        # Stop the mixer
        return mixer_btn_names["start"], get_color_for_item(style, False), False, [False] * n_moves, [False] * n_lessons


def pick_next_move(selected_bools, remaining, catalog: DanceMoveCollection, bpm):
    remaining = catalog.sequence_count if (remaining is None or remaining <= 0) else remaining

    pool = [m for m, sel in zip(catalog.moves, selected_bools) if sel and m.counts <= remaining]
    if not pool:
        basic = catalog.basic_move
        if basic.counts > remaining:
            remaining = catalog.sequence_count
        pool = [basic]

    chosen = random.choice(pool)
    remaining_after = remaining - chosen.counts
    interval_ms = chosen.counts * (60000 / bpm)
    return chosen, remaining_after, interval_ms


@app.callback(
    [
        Output("metronome-button", "children"),
        Output("metronome-interval", "interval"),
        Output("metronome-interval", "disabled"),

        Output("mixer-count-interval", "disabled"),
        Output("mixer-count-interval", "interval"),
        Output("mixer-sound", "src"),

        Output("current-move", "data", allow_duplicate=True),
        Output("mixer-remaining", "data"),
    ],
    [
        Input("metronome-button", "n_clicks"),
        Input("metronome-bpm-input", "value"),

        Input("mixer-button", "n_clicks"),
        Input("mixer-count-interval", "n_intervals"),

        Input("style", "data")
    ],
    [
        State("metronome-interval", "disabled"),
        State("mixer-button", "children"),
        State("selected-moves", "data"),
        State("mixer-remaining", "data"),
    ],
    prevent_initial_call=True
)
def manage_mixer_and_metronome(metronome_n_clicks, bpm, mixer_n_clicks, n_intervals, style, metronome_is_disabled, mixer_button_name, selected_moves_bools, mixer_remaining):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    metronome_button_text = metronome_interval = metronome_disabled = mixer_disabled = mixer_interval = move_file = current_move = mixer_remaining_out = dash.no_update
    catalog = get_catalog(style)

    if triggered_id in ("metronome-button", "metronome-bpm-input", "mixer-button", "mixer-count-interval"):
        if not bpm or bpm <= 0:
            bpm = 120

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
                mixer_remaining_out = catalog.sequence_count
            else:
                mixer_disabled = True

        case "mixer-count-interval":
            new_move, remaining_after, interval_ms = pick_next_move(
                selected_moves_bools or [False] * len(catalog.moves),
                mixer_remaining,
                catalog,
                bpm
            )
            move_file = dash.get_app().get_asset_url(f"{style}/{new_move.name}.wav")
            mixer_interval = interval_ms
            current_move = new_move.name
            mixer_remaining_out = remaining_after

    return metronome_button_text, metronome_interval, metronome_disabled, mixer_disabled, mixer_interval, move_file, current_move, mixer_remaining_out


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


app.clientside_callback(
    """
    function(videoSrc) {
        const videoPlayer = document.getElementById('video-player');
        if (videoPlayer && videoSrc) {
            videoPlayer.src = videoSrc;
            videoPlayer.currentTime = 0;
            videoPlayer.play();
        }
        return null;
    }
    """,
    Output("dummy", "data"),
    Input("video-source", "data")
)


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


if __name__ == '__main__':
    run()
