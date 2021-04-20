# Import required libraries

from utils.libs import *

from app import app

server = app.server

# get relative data folder
PATH = pathlib.Path(__file__).parent

# Load data
df = funs.get_data()

controls_df = df[
    [
        'instructor', 'length', 'power_zone', 'fitness_discipline', 'class_title',
        'difficulty', 'calories', 'distance', 'total_work', 'leaderboard_rank_pct_of_total'
    ]
]

INSTRUCTORS = funs.get_controls(controls_df, 'instructor')
CLASS_LENGTH = [el for el in funs.get_controls(controls_df, 'length') if el.get('value') != 0]
POWER_ZONE = funs.get_controls(controls_df, 'power_zone')
DISCIPLINE = funs.get_controls(controls_df, 'fitness_discipline')

# Create app layout
layout = [
    html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Button("Reset All Filters", id="workouts-reset-filters"),
                            html.Br(),
                            html.Br(),
                            html.P("Date Range Filter:", className="control_label"),
                            dcc.DatePickerRange(
                                id="workouts-date-picker",
                                min_date_allowed=df['created_at'].min(),
                                max_date_allowed=df['created_at'].max(),
                                start_date=df['created_at'].min(),
                                end_date=df['created_at'].max(),
                                persistence=True,
                                persistence_type='session',
                                className='dcc_control',
                                day_size=49
                            )
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options-1"
                    ),
                    html.Div(
                        [
                            html.P("Filter by Instructor:", className="control_label"),
                            dcc.Dropdown(
                                id="workouts-instructor-dropdown",
                                options=INSTRUCTORS,
                                multi=True,
                                value=None,
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                            html.P("Filter by Class Length:", className="control_label"),
                            dcc.Dropdown(
                                id="workouts-class-length-dropdown",
                                options=CLASS_LENGTH,
                                multi=True,
                                value=None,
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                            html.P("Filter by Fitness Discipline:", className="control_label"),
                            dcc.Dropdown(
                                id="workouts-discipline-dropdown",
                                options=DISCIPLINE,
                                multi=True,
                                value=None,
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options-2",
                    ),
                    html.Div(
                        [
                            html.P("Filter by Output:", className="control_label"),
                            dcc.RangeSlider(
                                id="workouts-output-range",
                                min=math.floor(controls_df['total_work'].min()),
                                max=math.ceil(controls_df['total_work'].max()),
                                step=25,
                                value=[
                                    math.floor(controls_df['total_work'].min()),
                                    math.ceil(controls_df['total_work'].max())
                                ],
                                marks={
                                    str(math.floor(controls_df['total_work'].min())): str(math.floor(controls_df['total_work'].min())),
                                    str(math.ceil(controls_df['total_work'].max())): str(math.ceil(controls_df['total_work'].max()/1000))
                                },
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                            html.P("Filter by Calories:", className="control_label"),
                            dcc.RangeSlider(
                                id="workouts-calories-range",
                                min=math.floor(controls_df['calories'].min()),
                                max=math.ceil(controls_df['calories'].max()),
                                step=25,
                                value=[
                                    math.floor(controls_df['calories'].min()),
                                    math.ceil(controls_df['calories'].max())
                                ],
                                marks={
                                    str(math.floor(controls_df['calories'].min())): str(math.floor(controls_df['calories'].min())),
                                    str(math.ceil(controls_df['calories'].max())): str(math.ceil(controls_df['calories'].max()))
                                },
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                            html.P("Filter by Distance:", className="control_label"),
                            dcc.RangeSlider(
                                id="workouts-distance-range",
                                min=math.floor(controls_df['distance'].min()),
                                max=math.ceil(controls_df['distance'].max()),
                                step=1,
                                value=[
                                    math.floor(controls_df['distance'].min()),
                                    math.ceil(controls_df['distance'].max())
                                ],
                                marks={
                                    str(math.floor(controls_df['distance'].min())): str(math.floor(controls_df['distance'].min())),
                                    str(math.ceil(controls_df['distance'].max())): str(math.ceil(controls_df['distance'].max()))
                                },
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                            html.P("Filter by Difficulty:", className="control_label"),
                            dcc.RangeSlider(
                                id="workouts-difficulty-range",
                                min=0,
                                max=10,
                                step=0.5,
                                value=[0, 10],
                                marks={i: '{}'.format(i) for i in range(11)},
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                            html.P("Filter by Leaderboard Rank (% of Total):", className="control_label"),
                            dcc.RangeSlider(
                                id="workouts-leaderboard-range",
                                min=0,
                                max=100,
                                step=1,
                                value=[0, 100],
                                marks={i*5: '{}'.format(i*5) for i in range(21)},
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            )
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options-3",
                    )
                ],
                className="row flex-display"
            ),
            html.Div(
                id='workouts-table',
                className="pretty_container"
            )
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"}
    )
]


def parse_date(raw_date):

    if isinstance(raw_date, list):
        ret_date = parse(raw_date[0])
    else:
        ret_date = parse(raw_date)

    return ret_date

# Helper functions to create figures


def create_workouts_table(table_df):

    table_dff = table_df[
        [
            'created_at', 'name', 'class_title', 'instructor', 'instructor_spotify_playlist', 'power_zone',
            'total_work', 'is_total_work_personal_record', 'difficulty', 'leaderboard_rank', 'total_leaderboard_users',
            'leaderboard_pct_finish', 'distance', 'calories', 'max_power', 'avg_power', 'max_cadence', 'avg_cadence',
            'max_resistance', 'avg_resistance', 'max_speed', 'avg_speed', 'max_heart_rate', 'avg_heart_rate'

        ]
    ]
    table_dff.columns = [
        'Ride Time', 'Workout Type', 'Title', 'Instructor', "Instructor's Personal Playlist",
        "Is Power Zone", 'Output (kJ)', 'Is PR', 'Difficulty', 'Rank', 'Total Users', 'Leaderboard % Rank',
        'Distance (mi)', 'Calories', 'Max Power', 'Avg Power', 'Max Cadence', 'Avg Cadence', 'Max Resistance',
        'Avg Resistance', 'Max Speed', 'Avg Speed', 'Max Heart Rate', 'Avg Heart Rate'
    ]

    table_dff['Output (kJ)'] = np.round(table_dff['Output (kJ)']/1000, 2)
    table_dff["Instructor's Personal Playlist"] = "[Link](" + table_dff["Instructor's Personal Playlist"] + ")"

    dt = dash_table.DataTable(
        columns=[
            {
                "name": i,
                "id": i,
                "presentation": "markdown" if i == "Instructor's Personal Playlist" else 'input',
                "hideable": True
            }
            for i in table_dff.columns
        ],
        data=table_dff.sort_values('Ride Time', ascending=False).to_dict('records'),
        style_data={
            'background-color': "white",
            'border': '1px solid #C0C0C0',
            'font-family': 'Arial, Helvetica, sans-serif'
        },
        style_cell={
            'text-align': 'left',
            'minWidth': '150px'
        },
        style_header={
            'fontWeight': 'bold',
            'whiteSpace': 'normal',
            'height': 'auto',
            'font-family': 'Arial, Helvetica, sans-serif'
        },
        page_action='native',
        page_size=50,
        sort_action='native',
        style_table={'overflowX': 'auto'}
    )

    return dt


@app.callback(
    [
        Output("workouts-date-picker", "start_date"),
        Output("workouts-date-picker", "end_date"),
        Output("workouts-instructor-dropdown", "value"),
        Output("workouts-class-length-dropdown", "value"),
        Output("workouts-discipline-dropdown", "value"),
        Output("workouts-output-range", "value"),
        Output("workouts-calories-range", "value"),
        Output("workouts-distance-range", "value"),
        Output("workouts-difficulty-range", "value"),
        Output("workouts-leaderboard-range", "value")
    ],
    [
        Input("workouts-reset-filters", "n_clicks_timestamp"),
        Input("main-session-filters", "data"),
        Input("main-session-filters", "modified_timestamp")
    ]
)
def update_filters(reset, main_filters, main_ts):
    reset = -1 if reset is None else reset
    output_value = [math.floor(df['total_work'].min()), math.ceil(df['total_work'].max())]
    calories_value = [math.floor(df['calories'].min()), math.ceil(df['calories'].max())]
    distance_value = [math.floor(df['distance'].min()), math.ceil(df['distance'].max())]
    if reset > main_ts:
        ret = [
            df['created_at'].min(), df['created_at'].max(),
            None, None, None,
            output_value,
            calories_value,
            distance_value,
            [0, 10],
            [0, 100]
        ]
    else:
        if main_ts == -1:
            ret = [
                df['created_at'].min(), df['created_at'].max(),
                None, None, None,
                output_value,
                calories_value,
                distance_value,
                [0, 10],
                [0, 100]
            ]
        else:
            ret = [
                main_filters.get('start_date'),
                main_filters.get('end_date'),
                main_filters.get('instructor'),
                main_filters.get('length'),
                main_filters.get('discipline'),
                main_filters.get('output') if main_filters.get('output') is not None else output_value,
                main_filters.get('calories') if main_filters.get('calories') is not None else calories_value,
                main_filters.get('distance') if main_filters.get('distance') is not None else distance_value,
                main_filters.get('difficulty') if main_filters.get('difficulty') is not None else [0, 10],
                main_filters.get('leaderboard') if main_filters.get('leaderboard') is not None else [0, 100]
            ]

    return ret


@app.callback(
    [
        Output("workouts-table", "children"),
        Output("workouts-session-filters", "data")
    ],
    [
        Input("workouts-date-picker", "start_date"),
        Input("workouts-date-picker", "end_date"),
        Input("workouts-instructor-dropdown", "value"),
        Input("workouts-class-length-dropdown", "value"),
        Input("workouts-discipline-dropdown", "value"),
        Input("workouts-output-range", "value"),
        Input("workouts-calories-range", "value"),
        Input("workouts-distance-range", "value"),
        Input("workouts-difficulty-range", "value"),
        Input("workouts-leaderboard-range", "value"),
        Input("main-session-filters", "data")
    ]
)
def update_widgets(
        start_date, end_date, instructors, class_lengths, disciplines,
        output, calories, distance, difficulty, leaderboard, filters
):

    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    df['leaderboard_pct_finish'] = np.round(100*(df['leaderboard_rank'] / df['total_leaderboard_users']), 2)

    df_filtered = df.loc[
        (df['created_at'] >= start_date) &
        (df['created_at'] <= end_date) &
        (df['total_work'] >= output[0]) &
        (df['total_work'] <= output[1]) &
        (df['calories'] >= calories[0]) &
        (df['calories'] <= calories[1]) &
        (df['distance'] >= distance[0]) &
        (df['distance'] <= distance[1]) &
        (df['difficulty'] >= difficulty[0]) &
        (df['difficulty'] <= difficulty[1]) &
        (df['leaderboard_pct_finish'] >= leaderboard[0]) &
        (df['leaderboard_pct_finish'] <= leaderboard[1]) &
        (df['length'] != 0),
    ]

    if instructors is not None:
        if len(instructors) > 0:
            df_filtered = df_filtered.loc[df_filtered['instructor'].isin(instructors), ]

    if class_lengths is not None:
        if len(class_lengths) > 0:
            df_filtered = df_filtered.loc[df_filtered['length'].isin(class_lengths), ]

    if disciplines is not None:
        if len(disciplines) > 0:
            df_filtered = df_filtered.loc[df_filtered['fitness_discipline'].isin(disciplines), ]

    workouts_table = create_workouts_table(df_filtered)

    filters = {} if filters is None else filters

    filters['start_date'] = start_date
    filters['end_date'] = end_date
    filters['instructor'] = instructors
    filters['length'] = class_lengths
    filters['discipline'] = disciplines
    filters['output'] = output
    filters['calories'] = calories
    filters['distance'] = distance
    filters['difficulty'] = difficulty
    filters['leaderboard'] = leaderboard

    ret = [workouts_table, filters]

    return ret

