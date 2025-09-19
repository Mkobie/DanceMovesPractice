import dash_bootstrap_components as dbc
from dash import html, dcc

from setup import bpm_limits, mixer_btn_names, default_interval, show_video_dropdown, \
    metronome_audio, get_catalog, DEFAULT_STYLE

mixer_settings = dbc.InputGroup(
                            [
                                dbc.InputGroupText("Practice up to"),
                                dbc.DropdownMenu(
                                        label=get_catalog(DEFAULT_STYLE).get_groups()[0], id="mixer-moves", color="secondary",
                                        children=[dbc.DropdownMenuItem(title, id={'type': 'mixer-moves-dropdown-item', 'index': i}) for i, title in enumerate(get_catalog(DEFAULT_STYLE).get_groups())],
                                    ),
                                dbc.InputGroupText("at"),
                                dbc.Input(id="metronome-bpm-input", type="number", value=default_interval["bpm"], min=bpm_limits["min"], max=bpm_limits["max"], step=1, debounce=True),
                                dbc.Button("\U0000266a", id="metronome-button", color="secondary", ),
                                dbc.InputGroupText("bpm"),
                                dbc.DropdownMenu(
                                        label=show_video_dropdown[0], id="mixer-show-vid", color="secondary",
                                        children=[
                                            dbc.DropdownMenuItem(show_video_dropdown[0], id="mixer-show-vid-no"),
                                            dbc.DropdownMenuItem(show_video_dropdown[1], id="mixer-show-vid-yes")
                                        ],
                                    ),
                            ],
                        )

metronome_stuff = html.Div(
    [
        dcc.Interval(id="metronome-interval", interval=600, n_intervals=0, disabled=True),
        html.Div(id="metronome-dummy", style={'display': 'none'}),
        html.Audio(id="metronome-sound", src=metronome_audio, controls=False, style={'display': 'none'})
    ]
)

mixer_stuff = html.Div(
    [
        dcc.Interval(id="mixer-count-interval", interval=0, n_intervals=0, disabled=True),
        html.Div(id="mixer-dummy", style={'display': 'none'}),
        html.Audio(id="mixer-sound", controls=False, style={'display': 'none'}),
    ]
)

mixer = dbc.Row(
                [
                    dbc.Col(
                        [
                            mixer_settings
                        ], width=8
                    ),

                    dbc.Col(
                        [
                            dbc.Button(mixer_btn_names["start"], id="mixer-button", color="secondary"),
                        ]
                    ),

                    metronome_stuff,
                    mixer_stuff

                ], className="mt-3",

            )

mixer_wrapper = html.Div(
    mixer,
    id="mixer-wrapper",
)
