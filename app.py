import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from pathlib import Path

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Path to the assets folder
assets_folder = Path.cwd() / 'assets'

# Get the list of all video files in the assets folder
video_files = [f.name for f in assets_folder.iterdir() if f.suffix in ['.mp4', '.webm', '.ogg']]

basic_turn_videos = [f for f in video_files if "turn" in f]
promenade_videos = [f for f in video_files if "Promenade" in f]

column_names = ["Basic turns", "Promenade"]
column_files = [basic_turn_videos, promenade_videos]


def button_list(title, video_list):
    return dbc.Col([
        html.H4(title, className="card-title"),
        dbc.ButtonGroup([
            dbc.Button(video, id={'type': 'video-button', 'index': f"{title}-{i}"}, color="primary",
                       className="mb-2")
            for i, video in enumerate(video_list)
        ], vertical=True)
    ], className="h-100", width='auto')


# Layout of the app
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.Video(
                            id="video-player",
                            src=f"/assets/{video_files[0]}",
                            controls=True,
                            autoPlay=True,
                            loop=True,
                            style={"width": "100%", "height": "auto"}
                        )
                    ])
                ], className="mb-4"), width={"size": 6, "offset": 3},
            )
        ),

        dbc.Row([
                button_list(column_names[0], column_files[0]),
                button_list(column_names[1], column_files[1]),
        ])
    ], fluid=True)


# Callback to update the video source
@callback(
    Output("video-player", "src"),
    Input({'type': 'video-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_video(n_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update

    # Get the id of the button clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    index = eval(button_id)['index']

    # Determine the video list and file index
    prefix, idx = index.split('-')
    idx = int(idx)

    if prefix == column_names[0]:
        return f"/assets/{column_files[0][idx]}"
    elif prefix == column_names[1]:
        return f"/assets/{column_files[1][idx]}"

    return dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)