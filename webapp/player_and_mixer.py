import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

from setup import dance_moves
from setup import show_video_dropdown
from webapp.mixer import mixer
from webapp.server import app

player = html.Video(id="video-player",
                    src=f"assets/{dance_moves.moves[0].name}.mp4",
                    controls=True,
                    autoPlay=True,
                    loop=True,
                    muted=True,
                    style={"width": "100%", "height": "auto"})

player_and_mixer = dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6("\u00A0", className="card-title"),
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


@app.callback(
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
