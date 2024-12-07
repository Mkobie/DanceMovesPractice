import dash_bootstrap_components as dbc
from dash import html, dcc

from setup import grouping_titles, dance_moves


def generate_move_button_row(move):
    return html.Div([
        dbc.Button(move.name, id={'type': 'move-button', 'index': f"{move.name}"}, color="secondary", className="flex-grow-1", n_clicks=0),
        dbc.Button("\U0001F855", id={'type': 'lesson-button', 'index': f"{move.name}"}, href=f"{move.lesson}", target="_blank", style={'display': 'none'}, color="secondary", className="flex-shrink-1"),
        dbc.Checkbox(id={'type': 'move-checkbox', 'index': f"{move.name}"}, style={'margin-left': '10px'}, value=False),
    ], className="d-flex align-items-center mb-1 ms-4")

def generate_column_of_move_button_rows(title):
    moves_for_column = [move for move in dance_moves.moves if move.grouping == title]
    return html.Div([
        html.Div([dbc.Checkbox(id={'type': 'group-checkbox', 'index': f"{title}"}, value=False), html.H6(title, className="card-title")], className="d-flex align-items-center mb-1"),
        html.Div([generate_move_button_row(move) for move in moves_for_column])
    ])

def generate_groups_of_moves():
    groups = []
    for title in grouping_titles:
        groups.append(generate_column_of_move_button_rows(title))
    return html.Div(groups)


move_list = dbc.Card(
                dbc.CardBody(
                    [
                        html.H6("Move list", className="card-title"),
                        html.Div(
                            [
                                dcc.Store(id='group-checkbox-store', data=dict(zip(grouping_titles, [False for title in grouping_titles]))),
                                dcc.Store(id='move-checkbox-store', data=dict(zip([move.name for move in dance_moves.moves], [False for move in dance_moves.moves]))),
                                generate_groups_of_moves(),
                            ],
                            style={"maxHeight": "calc(100vh - 119px)", 'overflow-y': 'scroll', "border": "1px solid rgba(211, 211, 211, 1)",
                                   "borderRadius": "6px", "padding": "5px 0rem 5px 5px"}
                        )
                    ]
                ), className="border-0 bg-transparent"
            )
