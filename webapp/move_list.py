import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback

from setup import get_catalog, DEFAULT_STYLE, CUSTOM_MIXER_MOVES_LABEL


def generate_move_button_row(move):
    return html.Div([
        dbc.Button(move.name, id={'type': 'move-button', 'index': f"{move.name}"}, color="secondary", className="flex-grow-1", n_clicks=0),
        dbc.Button("\U0001F855", id={'type': 'lesson-button', 'index': f"{move.name}"}, href=f"{move.lesson}", target="_blank", style={'display': 'none'}, color="secondary", className="flex-shrink-1"),
        dbc.Checkbox(id={'type': 'move-checkbox', 'index': f"{move.name}"}, style={'margin-left': '10px'}, value=False),
    ], className="d-flex align-items-center mb-1 ms-4")

def generate_column_of_move_button_rows(catalog, title):
    moves_for_column = [move for move in catalog.moves if move.grouping == title]
    return html.Div([
        html.Div([dbc.Checkbox(id={'type': 'group-checkbox', 'index': f"{title}"}, value=False), html.H6(title, className="card-title")], className="d-flex align-items-center mb-1"),
        html.Div([generate_move_button_row(move) for move in moves_for_column])
    ])

def generate_groups_of_moves(catalog):
    groups = []
    for title in catalog.get_groups():
        groups.append(generate_column_of_move_button_rows(catalog, title))
    return html.Div(groups)


move_list = dbc.Card(
                dbc.CardBody(
                    [
                        html.H6("Move list", className="card-title"),
                        dcc.Store(id='group-checkbox-store', data=[False]*len(get_catalog(DEFAULT_STYLE).groups)),
                        html.Div(
                            id="move-list-body",
                            children=generate_groups_of_moves(get_catalog(DEFAULT_STYLE)),
                            style={"maxHeight": "calc(100vh - 119px)", 'overflow-y': 'scroll', "border": "1px solid rgba(211, 211, 211, 1)",
                                   "borderRadius": "6px", "padding": "5px 0rem 5px 5px"}
                        )
                    ]
                ), className="border-0 bg-transparent"
            )


@callback(
    Output("move-list-body", "children"),
    Input("style", "data"),
)
def render_move_list(style):
    catalog = get_catalog(style)
    return generate_groups_of_moves(catalog)


@callback(
    [
        Output("mixer-moves", "label"),
        Output({'type': 'group-checkbox', 'index': dash.dependencies.ALL}, 'value'),
        Output({'type': 'move-checkbox', 'index': dash.dependencies.ALL}, 'value'),
        Output("group-checkbox-store", "data"),
        Output("selected-moves", "data"),
    ],
    [
        Input({'type': 'mixer-moves-dropdown-item', 'index': dash.dependencies.ALL}, 'n_clicks'),
        Input({'type': 'group-checkbox', 'index': dash.dependencies.ALL}, 'value'),
        Input({'type': 'move-checkbox', 'index': dash.dependencies.ALL}, 'value'),
        Input("style", "data"),
    ],
    [
        State("mixer-moves", "label"),
        State("group-checkbox-store", "data"),
    ],
)
def update_selected_move_checkboxes(n_clicks, group_checkbox_values, move_checkbox_values, style, mixer_moves_label, group_checkbox_previous_values):
    ctx = dash.callback_context
    tid = ctx.triggered_id

    catalog = get_catalog(style)
    groups = catalog.groups
    moves = catalog.moves
    group_map = catalog.groups_map()

    new_group_checkbox_values = (group_checkbox_values
                      if group_checkbox_values and len(group_checkbox_values) == len(groups)
                      else [False] * len(groups))
    new_move_checkbox_values = (move_checkbox_values
                     if move_checkbox_values and len(move_checkbox_values) == len(moves)
                     else [False] * len(moves))
    mixer_moves_label = mixer_moves_label or CUSTOM_MIXER_MOVES_LABEL

    if not tid or tid == "style":
        dropdown_index = 0
        new_group_checkbox_values = [i <= dropdown_index for i in range(len(groups))]
        sel_groups = {groups[i] for i, v in enumerate(new_group_checkbox_values) if v}
        new_move_checkbox_values = [m.grouping in sel_groups for m in moves]
        mixer_moves_label = groups[0]
        return mixer_moves_label, new_group_checkbox_values, new_move_checkbox_values, new_group_checkbox_values, new_move_checkbox_values

    if isinstance(tid, dict):
        trigger_source = tid.get("type")
        trigger_index = tid.get("index")
    else:
        trigger_source = tid
        trigger_index = None

    match trigger_source:
        case "mixer-moves-dropdown-item":
            dropdown_index = int(trigger_index)
            new_group_checkbox_values = [i <= dropdown_index for i in range(len(groups))]
            sel_groups = {groups[i] for i, v in enumerate(new_group_checkbox_values) if v}
            new_move_checkbox_values = [m.grouping in sel_groups for m in moves]
            mixer_moves_label = groups[dropdown_index]

        case "group-checkbox":
            prev = (group_checkbox_previous_values
                    if group_checkbox_previous_values and len(group_checkbox_previous_values) == len(groups)
                    else [False] * len(groups))
            changed_i = next((i for i, (a, b) in enumerate(zip(prev, new_group_checkbox_values)) if a != b), None)
            if changed_i is not None:
                gname = groups[changed_i]
                target = new_group_checkbox_values[changed_i]
                for mi in group_map[gname]:
                    new_move_checkbox_values[mi] = target
            mixer_moves_label = CUSTOM_MIXER_MOVES_LABEL

        case "move-checkbox":
            new_group_checkbox_values = []
            for g in groups:
                idxs = group_map[g]
                new_group_checkbox_values.append(all(new_move_checkbox_values[i] for i in idxs))
            mixer_moves_label = CUSTOM_MIXER_MOVES_LABEL

    return mixer_moves_label, new_group_checkbox_values, new_move_checkbox_values, new_group_checkbox_values, new_move_checkbox_values
