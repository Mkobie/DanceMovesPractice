import dash_bootstrap_components as dbc
from dash import html, dcc

from setup import mixer_moves, bmp_limits, mixer_btn_names, default_interval, show_video_dropdown_options, \
    metronome_audio, dance_moves

player_and_mixer = dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6("\u00A0", className="card-title"),
                            html.Div(
                                [
                                    html.Video(
                                        id="video-player",
                                        src=f"/assets/{dance_moves.moves[0].name}.mp4",
                                        controls=True,
                                        autoPlay=True,
                                        loop=True,
                                        style={"width": "100%", "height": "auto"}
                                    ),
                                    dbc.Row([
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
                                                    dbc.Button("\U0000266a", id="metronome-button", color="secondary", ),
                                                    dbc.InputGroupText("bpm"),
                                                    dbc.DropdownMenu(
                                                            label=show_video_dropdown_options[0], id="mixer-show-vid", color="secondary",
                                                            children=[
                                                                dbc.DropdownMenuItem(show_video_dropdown_options[0], id="option-1"),
                                                                dbc.DropdownMenuItem(show_video_dropdown_options[1], id="option-2")
                                                            ],
                                                        ),
                                                ],
                                            ),
                                            dcc.Interval(id="metronome-interval", interval=600, n_intervals=0, disabled=True),
                                            html.Div(id="metronome-dummy", style={'display': 'none'}),
                                            html.Audio(id="metronome-sound", src=metronome_audio, controls=False,
                                                       style={'display': 'none'}),
                                        ], width=9),
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
                                ],
                            )
                        ], style={'height': '90vh'}
                    ), className="border-0 bg-transparent"
                )
