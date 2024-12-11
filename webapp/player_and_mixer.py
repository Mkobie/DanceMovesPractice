import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output

from mixer import mixer
from player import player
from setup import show_video_dropdown
from webapp.server import app

player_and_mixer = dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6("\u00A0", className="card-title"),
                            html.Div(
                                [
                                    player,
                                    mixer
                                ],
                            )
                        ], style={'height': '90vh'}
                    ), className="border-0 bg-transparent"
                )


@app.callback(
    Output("mixer-show-vid", "label"),
    [
        Input("mixer-show-vid-no", "n_clicks"),
        Input("mixer-show-vid-yes", "n_clicks")
    ],
    prevent_initial_call=True
)
def update_dropdown_label(n1, n2):
    if n1:
        return show_video_dropdown[0]
    elif n2:
        return show_video_dropdown[1]
    return dash.no_update
