# Import required libraries

from utils.libs import *

from app import app

server = app.server

# get relative data folder
PATH = pathlib.Path(__file__).parent

# Load data
df, heart_rate_zones, ftp, weight = funs.get_data(PATH.parent)

controls_df = df[
    [
        'instructor', 'length', 'power_zone', 'fitness_discipline', 'class_title',
        'difficulty', 'calories', 'distance', 'total_work', 'leaderboard_rank_pct_of_total'
    ]
]

heart_rate_colors = {
    'Zone 1': '#51C3AA',
    'Zone 2': '#B7C85B',
    'Zone 3': '#F9CB3D',
    'Zone 4': '#FC800F',
    'Zone 5': '#FF4658'
}

power_zones = {
    'Zone 1': {'color': '#56A5CD', 'min': 0, 'max': ftp*.56},
    'Zone 2': {'color': '#47C09F', 'min': ftp*.56, 'max': ftp*.75},
    'Zone 3': {'color': '#ADC44E', 'min': ftp*.75, 'max': ftp*.90},
    'Zone 4': {'color': '#D6A835', 'min': ftp*.90, 'max': ftp*1.05},
    'Zone 5': {'color': '#D28F2E', 'min': ftp*1.05, 'max': ftp*1.2},
    'Zone 6': {'color': '#D56514', 'min': ftp*1.2, 'max': ftp*1.5},
    'Zone 7': {'color': '#DA374A', 'min': ftp*1.5, 'max': ftp*10},
}

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
                                step=None,
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
                                step=None,
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
                id='workouts-table-div',
                className="pretty_container"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [html.H6(id="workout-output-text"), html.P("Output")],
                                id="output",
                                className="mini_container",
                            ),
                            html.Div(
                                [html.H6(id="workout-distance-text"), html.P("Distance")],
                                id="distance",
                                className="mini_container",
                            ),
                            html.Div(
                                [html.H6(id="workout-calories-text"), html.P("Calories")],
                                id="calories",
                                className="mini_container",
                            )
                        ],
                        id="workout-info-container",
                        className="row container-display",
                    ),
                    html.Div(
                        [
                            html.Div(
                                id='metrics-line-div-1',
                                className="pretty_container six columns"
                            ),
                            html.Div(
                                id='metrics-line-div-2',
                                className="pretty_container six columns",
                            )
                        ],
                        id='workout-charts',
                        className='row flex-display'
                    )
                ],
                id='workout-stats',
                className="row flex-display"
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


def create_heart_rate_zone_bar_chart(heart_rate_zones):
    fig = go.Figure()
    for z in heart_rate_zones:
        fig.add_trace(go.Bar(
            x=[z.get('display_name')],
            y=[z.get('duration')],
            name=z.get('display_name'),
            hovertemplate="<b>%{x}</b><br>"
                          "Duration (s): %{y}<br>"
                          "<extra></extra>",
            marker_color=heart_rate_colors.get(z.get('display_name'))
        ))

    fig.update_layout(
        yaxis={
            'title': 'Duration (s)'
        },
        plot_bgcolor='white',
        showlegend=False,
        title="Time in Heart Rate Zones"
    )

    return dcc.Graph(id='hr-zones-bar-chart', figure=fig)


def create_metrics_line_charts(workout_time_series, segments, ftp, is_pz, power_zones):
    power_zones = {
        'Zone 1': {'color': '#56A5CD', 'min': 0, 'max': ftp * .56},
        'Zone 2': {'color': '#47C09F', 'min': ftp * .56, 'max': ftp * .75},
        'Zone 3': {'color': '#ADC44E', 'min': ftp * .75, 'max': ftp * .90},
        'Zone 4': {'color': '#D6A835', 'min': ftp * .90, 'max': ftp * 1.05},
        'Zone 5': {'color': '#D28F2E', 'min': ftp * 1.05, 'max': ftp * 1.2},
        'Zone 6': {'color': '#D56514', 'min': ftp * 1.2, 'max': ftp * 1.5},
        'Zone 7': {'color': '#DA374A', 'min': ftp * 1.5, 'max': ftp * 10},
    }
    output_fig = go.Figure()
    output_fig.add_trace(go.Scatter(
        x=workout_time_series['interval_start'],
        y=workout_time_series['output'],
        customdata=workout_time_series[['interval_end', 'cadence', 'resistance', 'speed', 'heart_rate']],
        name='Output (kJ)',
        mode='lines+markers',
        hovertemplate="<b>Ride Interval</b>: %{x}s - %{customdata[0]}s<br>"
                      "<b>Average Output</b>: %{y} kJ<br>"
                      "<b>Average Cadence</b>: %{customdata[1]} rpm<br>"
                      "<b>Average Resistance</b>: %{customdata[2]}<br>"
                      "<b>Average Speed</b>: %{customdata[3]} mph<br>"
                      "<b>Average Heart Rate</b>: %{customdata[4]} bpm"
                      "<extra></extra>"
    ))

    cadence_fig = go.Figure()
    cadence_fig.add_trace(go.Scatter(
        x=workout_time_series['interval_start'],
        y=workout_time_series['cadence'],
        customdata=workout_time_series[['interval_end', 'output', 'resistance', 'speed', 'heart_rate']],
        name='Cadence',
        mode='lines+markers',
        hovertemplate="<b>Ride Interval</b>: %{x}s - %{customdata}s<br>"
                      "<b>Average Cadence</b>: %{y} rpm<br>"
                      "<b>Average Output</b>: %{customdata[1]} kJ<br>"
                      "<b>Average Resistance</b>: %{customdata[2]}<br>"
                      "<b>Average Speed</b>: %{customdata[3]} mph<br>"
                      "<b>Average Heart Rate</b>: %{customdata[4]} bpm"
                      "<extra></extra>"
    ))
    resistance_fig = go.Figure()
    resistance_fig.add_trace(go.Scatter(
        x=workout_time_series['interval_start'],
        y=workout_time_series['resistance'],
        customdata=workout_time_series[['interval_end', 'output', 'cadence', 'speed', 'heart_rate']],
        name='Resistance',
        mode='lines+markers',
        hovertemplate="<b>Ride Interval</b>: %{x}s - %{customdata}s<br>"
                      "<b>Average Resistance</b>: %{y}<br>"
                      "<b>Average Output</b>: %{customdata[1]} kJ<br>"
                      "<b>Average Cadence</b>: %{customdata[2]} rpm<br>"
                      "<b>Average Speed</b>: %{customdata[3]} mph<br>"
                      "<b>Average Heart Rate</b>: %{customdata[4]} bpm"
                      "<extra></extra>"
    ))
    speed_fig = go.Figure()
    speed_fig.add_trace(go.Scatter(
        x=workout_time_series['interval_start'],
        y=workout_time_series['speed'],
        customdata=workout_time_series[['interval_end', 'output', 'cadence', 'resistance', 'heart_rate']],
        name='Speed',
        mode='lines+markers',
        hovertemplate="<b>Ride Interval</b>: %{x}s - %{customdata}s<br>"
                      "<b>Average Speed</b>: %{y} mph<br>"
                      "<b>Average Output</b>: %{customdata[1]} kJ<br>"
                      "<b>Average Cadence</b>: %{customdata[2]} rpm<br>"
                      "<b>Average Resistance</b>: %{customdata[3]}<br>"
                      "<b>Average Heart Rate</b>: %{customdata[4]} bpm"
                      "<extra></extra>"
    ))

    output_fig.update_layout(
        xaxis={
            'type': 'category',
            'gridcolor': '#EEEEEE',
            'gridwidth': 2
        },
        yaxis={
            'range': [workout_time_series['output'].min()/2, workout_time_series['output'].max()*1.2]
        },
        title='Output',
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        plot_bgcolor='white'
    )
    cadence_fig.layout = output_fig.layout
    cadence_fig.update_layout(
        title='Cadence',
        yaxis={'range': [workout_time_series['cadence'].min()/2, workout_time_series['cadence'].max()*1.2]}
    )
    resistance_fig.layout = output_fig.layout
    resistance_fig.update_layout(
        title='Resistance',
        yaxis={'range': [workout_time_series['resistance'].min()/2, workout_time_series['resistance'].max()*1.2]}
    )
    speed_fig.layout = output_fig.layout
    speed_fig.update_layout(
        title='Speed',
        yaxis={'range': [workout_time_series['speed'].min()/2, workout_time_series['speed'].max()*1.2]}
    )

    if workout_time_series['heart_rate'].mean() == 0:
        heart_rate_fig = None
    else:
        heart_rate_fig = go.Figure()
        heart_rate_fig.add_trace(go.Scatter(
            x=workout_time_series['interval_start'],
            y=workout_time_series['heart_rate'],
            customdata=workout_time_series[['interval_end', 'output', 'cadence', 'resistance', 'speed']],
            name='Heart Rate',
            mode='lines+markers',
            hovertemplate="<b>Ride Interval</b>: %{x}s - %{customdata}s<br>"
                          "<b>Average Heart Rate</b>: %{y} bpm<br>"
                          "<b>Average Output</b>: %{customdata[1]} kJ<br>"
                          "<b>Average Cadence</b>: %{customdata[2]} rpm<br>"
                          "<b>Average Resistance</b>: %{customdata[3]}<br>"
                          "<b>Average Speed</b>: %{customdata[4]} mph"
                          "<extra></extra>"
        ))

        heart_rate_fig.layout = output_fig.layout
        heart_rate_fig.update_layout(
            title='Heart Rate',
            yaxis={'range': [workout_time_series['heart_rate'].min()/2, workout_time_series['heart_rate'].max()*1.2]}
        )

    if is_pz:
        for key in power_zones.keys():
            output_fig.add_hrect(
                y0=power_zones.get(key).get('min'), y1=power_zones.get(key).get('max'),
                fillcolor=power_zones.get(key).get('color'), opacity=0.65,
                layer="below", line_width=0,
            )

    ret = [
        dcc.Graph(id='output-line-chart', figure=output_fig),
        dcc.Graph(id='resistance-line-chart', figure=resistance_fig),
        None if heart_rate_fig is None else dcc.Graph(id='heart-rate-line-chart', figure=heart_rate_fig),
        dcc.Graph(id='cadence-line-chart', figure=cadence_fig),
        dcc.Graph(id='speed-line-chart', figure=speed_fig)
    ]

    return ret


def create_workouts_table(table_df):

    table_dff = table_df[
        [
            'peloton_id', 'created_at', 'name', 'class_title', 'instructor', 'instructor_spotify_playlist',
            'power_zone', 'total_work', 'is_total_work_personal_record', 'difficulty', 'leaderboard_rank',
            'total_leaderboard_users', 'leaderboard_pct_finish', 'distance', 'calories', 'max_power', 'avg_power',
            'max_cadence', 'avg_cadence', 'max_resistance', 'avg_resistance', 'max_speed', 'avg_speed',
            'max_heart_rate', 'avg_heart_rate'

        ]
    ]
    table_dff.columns = [
        'id', 'Ride Time', 'Workout Type', 'Title', 'Instructor', "Instructor's Personal Playlist",
        "Is Power Zone", 'Output (kJ)', 'Is PR', 'Difficulty', 'Rank', 'Total Users', 'Leaderboard % Rank',
        'Distance (mi)', 'Calories', 'Max Power', 'Avg Power', 'Max Cadence', 'Avg Cadence', 'Max Resistance',
        'Avg Resistance', 'Max Speed', 'Avg Speed', 'Max Heart Rate', 'Avg Heart Rate'
    ]

    table_dff.loc[:, 'Output (kJ)'] = np.round(table_dff.loc[:, 'Output (kJ)']/1000, 2)
    table_dff.loc[:, "Instructor's Personal Playlist"] = "[Link](" + table_dff.loc[:, "Instructor's Personal Playlist"] + ")"

    dt = dash_table.DataTable(
        id='workouts-table',
        columns=[
            {
                "name": i,
                "id": i,
                "presentation": "markdown" if i == "Instructor's Personal Playlist" else 'input',
                "hideable": True
            }
            for i in table_dff.columns if i != 'id'
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
        page_size=10,
        sort_action='native',
        style_table={'overflowX': 'auto'},
        row_selectable='single'
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
        Output("workouts-table-div", "children"),
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


@app.callback(
    [
        Output("workout-stats", "style"),
        Output("workout-output-text", "children"),
        Output("workout-distance-text", "children"),
        Output("workout-calories-text", "children"),
        Output("metrics-line-div-1", "children"),
        Output("metrics-line-div-2", "children")
    ],
    [
        Input('workouts-table', "selected_row_ids"),
    ]
)
def update_workout_stats(peloton_id):

    if peloton_id is not None:
        workout_id = df.loc[df['peloton_id'] == peloton_id[0], 'workout_id'].values.tolist()[0]

        div_display = {'display': 'none'} if workout_id is None else {'display': 'inline'}

        workout_metrics, metrics_dict = funs.get_workout_metrics(workout_id)

        workout_time_series = pd.DataFrame(
            {
                'interval_start': workout_metrics.get('seconds_since_pedaling_start'),
                'output': metrics_dict.get('output').get('values'),
                'cadence': metrics_dict.get('cadence').get('values'),
                'resistance': metrics_dict.get('resistance').get('values'),
                'speed': metrics_dict.get('speed').get('values')
            }
        )

        hr_zones = None

        if metrics_dict.get('heart_rate') is None:
            workout_time_series['heart_rate'] = 0
        else:
            if 'hr_zones' in metrics_dict['heart_rate'].keys():
                hr_zones = create_heart_rate_zone_bar_chart(metrics_dict['heart_rate']['hr_zones'])

            workout_time_series['heart_rate'] = metrics_dict.get('heart_rate').get('values')

        workout_time_series['interval_end'] = (workout_time_series['interval_start'].shift(-1) - 1).fillna(
            workout_time_series['interval_start'].max())

        indicators = [
            (
                metrics_dict.get(m).get('display_name'),
                metrics_dict.get(m).get('max'),
                metrics_dict.get(m).get('average')
            ) for m in metrics_dict.keys()
        ]

        segments = [
            (
                seg.get('icon_slug'),
                seg.get('start_time_offset'),
                seg.get('length')
            ) for seg in workout_metrics.get('segment_list')
        ]

        totals = workout_metrics.get('summaries')
        is_pz = df.loc[df['peloton_id'] == peloton_id[0], 'power_zone'].values.tolist()[0]
        time_series = create_metrics_line_charts(workout_time_series, segments, ftp, is_pz, power_zones)

        indicators = [t.get('value') for t in totals]

        ret = [
            div_display, indicators[0], indicators[1], indicators[2],
            [time_series[0], time_series[1], time_series[2]],
            [time_series[3], time_series[4], hr_zones]
        ]
    else:
        ret = [{'display': 'none'}, None, None, None, None, None]

    return ret
