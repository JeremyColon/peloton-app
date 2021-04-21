import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from panels import main, workouts

import os

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='main-session-filters', storage_type='session'),
    dcc.Store(id='workouts-session-filters', storage_type='session'),
    html.Div(
        [
            html.Div(
                [
                    html.A(
                        html.Img(
                            src=app.get_asset_url("peloton-logo.png"),
                            id="peloton-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        ),
                        href="/panels/main"
                    )
                ],
                className="one-third column",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                f"{os.environ.get('PELOTON_DISPLAY_NAME')}'s Peloton Performance",
                                style={"margin-bottom": "0px", "text-align": "center"},
                            )
                        ]
                    )
                ],
                className="one-half column",
                id="title",
            ),
            html.Div(
                [
                    html.A(
                        html.Button("Main", id="main-panel"),
                        href="/panels/main",
                    ),
                    html.A(
                        html.Button("Workouts", id="workout-panel"),
                        href="/panels/workouts",
                    )
                ],
                className="one-third column",
                id="panels",
                style={'text-align': 'right'}
            )
        ],
        id="header",
        className="row flex-display",
        style={"margin-bottom": "25px"},
    ),
    html.Div(id='page-content'),
])


@app.callback(
    [
        Output("page-content", "children")
    ],
    [Input("url", "pathname")],
)
def display_page(pathname):

    if pathname == "/panels/workouts":
        return workouts.layout
    else:
        return main.layout


if __name__ == "__main__":
    app.run_server(debug=False)
