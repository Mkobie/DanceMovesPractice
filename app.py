import shutil
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

assets_folder = Path.cwd() / 'assets'
media_folder = Path.cwd() / 'media'

# todo: add moves from
#  https://thebluesroom.com/courses/side-by-side/
source_names = ["Basic Turns", "Ballroom Blues", "Ballroom Blues - turns", "Close Embrace Intensive", "Close Embrace - spin"]  # refers to source of video source on Blues Room site

column_files = []
for i, source_name in enumerate(source_names):
    video_folder = media_folder.joinpath(source_name)
    video_files = [f.name for f in video_folder.iterdir() if f.suffix in ['.mp4', '.webm', '.ogg']]
    column_files.append(video_files)

    for src_file in video_folder.glob('*.*'):
        shutil.copy(src_file, assets_folder)

video_files = [f.name for f in assets_folder.iterdir() if f.suffix in ['.mp4', '.webm', '.ogg']]


def button_list(title, video_list):
    return dbc.Col([
        html.H6(title, className="card-title"),
        dbc.ButtonGroup([
            dbc.Button(video[3:].replace('.mp4', ''), id={'type': 'video-button', 'index': f"{title}_{i}"}, color="secondary",
                       className="mb-2")
            for i, video in enumerate(video_list)
        ], vertical=True)
    ], className="h-100", width='auto')

def generate_button_lists():
    button_lists = []
    for i, entry in enumerate(source_names):
        button_lists.append(button_list(source_names[i], column_files[i]))
    return button_lists


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
                ], className="mb-4"), width={"size": 5, "offset": 2},
            )
        ),

        dbc.Row(generate_button_lists())
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
    prefix, idx = index.split('_')
    idx = int(idx)

    for i in range(20):
        if prefix == source_names[i]:
            return f"/assets/{column_files[i][idx]}"

    return dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)