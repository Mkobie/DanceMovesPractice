import dash_bootstrap_components as dbc

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("Blues Moves Practice", className="me-auto"),

            # dbc.Nav(  # todo: add link to repo in future
            #     dbc.NavItem(
            #         dbc.NavLink(
            #             "Contribute",
            #             href="",
            #             target="_blank"
            #         )
            #     ),
            #     className="ms-auto",
            # ),
        ],
        fluid=True,
    ),
    color="primary",
    dark=True,
)
