import dash_bootstrap_components as dbc
from dash import html

from setup import STYLES

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.Div(
                [
                    dbc.NavbarBrand("Dance Moves Practice:", className="me-2"),
                    dbc.ButtonGroup(
                        [
                            dbc.Button(
                                style,
                                id={"type": "style-button", "index": style},
                                size="md",
                                color="secondary",
                            )
                            for style in STYLES
                        ],
                        size="md",
                        className="ms-2",
                    ),
                ],
                className="d-flex align-items-center",
            ),
            dbc.Nav(
                dbc.NavItem(
                    dbc.NavLink(
                        "Contribute",
                        href="https://github.com/Mkobie/DanceMovesPractice",
                        target="_blank"
                    )
                ),
                className="ms-auto",
            ),
        ],
        fluid=True,
    ),
    color="secondary",
    dark=False,
)
