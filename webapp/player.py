from dash import html

from setup import dance_moves

player = html.Video(id="video-player",
                    src=f"assets/{dance_moves.moves[0].name}.mp4",
                    controls=True,
                    autoPlay=True,
                    loop=True,
                    style={"width": "100%", "height": "auto"})