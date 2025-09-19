import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback

from setup import show_video_dropdown, bpm_limits, default_interval, get_catalog, DEFAULT_STYLE
from webapp.mixer import mixer

player = html.Video(id="video-player",
                    src=f"/assets/{DEFAULT_STYLE}/{get_catalog(DEFAULT_STYLE).moves[0].name}.mp4",
                    controls=True,
                    autoPlay=True,
                    loop=True,
                    muted=True,
                    style={"width": "100%", "height": "auto"})

player_and_mixer = dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(
                                [
                                    player,
                                    mixer,
                                    dcc.Store(id="video-source"),
                                    dcc.Store(id="dummy"),
                                ],
                            )
                        ], style={'height': '90vh'}
                    ), className="border-0 bg-transparent"
                )


@callback(
    Output("mixer-show-vid", "label"),
    [
        Input("mixer-show-vid-no", "n_clicks"),
        Input("mixer-show-vid-yes", "n_clicks")
    ],
    prevent_initial_call=True
)
def update_dropdown_label(n1, n2):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if "no" in triggered_id:
        return show_video_dropdown[False]
    elif "yes" in triggered_id:
        return show_video_dropdown[True]
    else:
        return dash.no_update


@callback(
    Output("metronome-bpm-input", "value"),
    Input("metronome-bpm-input", "value"),
    prevent_initial_call=True,
)
def enforce_bpm_range(value):
    if value is None:
        return default_interval["bpm"]
    return max(bpm_limits["min"], min(bpm_limits["max"], value))
