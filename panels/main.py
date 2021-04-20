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
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Button("Reset All Filters", id="main-reset-filters"),
                            html.Br(),
                            html.Br(),
                            html.P("Date Range Filter:", className="control_label"),
                            dcc.DatePickerRange(
                                id="date-picker",
                                min_date_allowed=df['created_at'].min(),
                                max_date_allowed=df['created_at'].max(),
                                start_date=df['created_at'].min(),
                                end_date=df['created_at'].max(),
                                persistence=True,
                                persistence_type='session',
                                className='dcc_control',
                                day_size=49
                            ),
                            html.P("Filter by Instructor:", className="control_label"),
                            dcc.Dropdown(
                                id="instructor-dropdown",
                                options=INSTRUCTORS,
                                multi=True,
                                value=None,
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                            html.P("Filter by Class Length:", className="control_label"),
                            dcc.Dropdown(
                                id="class-length-dropdown",
                                options=CLASS_LENGTH,
                                multi=True,
                                value=None,
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                            html.P("Filter by Fitness Discipline:", className="control_label"),
                            dcc.Dropdown(
                                id="discipline-dropdown",
                                options=DISCIPLINE,
                                multi=True,
                                value=None,
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [html.H6(id="workouts-text"), html.P("# of Workouts")],
                                        id="workouts",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="output-text"), html.P("Total Output")],
                                        id="output",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="calories-text"), html.P("Total Calories Burned")],
                                        id="calories",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="distance-text"), html.P("Total Miles Traveled")],
                                        id="distance",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="avg-leaderboard-pct-finish-text"), html.P("Avg Finish")],
                                        id="leaderboard-finish",
                                        className="mini_container",
                                    )
                                ],
                                id="info-container",
                                className="row container-display",
                            ),
                            html.Div(
                                id="hours-per-month-bar",
                                className="pretty_container"
                            ),
                        ],
                        id="right-column",
                        className="eight columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [html.H6(id="pr-15-text"), html.P("PR - 15 Min")],
                        id="pr-15",
                        className="mini_container",
                    ),
                    html.Div(
                        [html.H6(id="pr-20-text"), html.P("PR - 20 Min")],
                        id="pr-20",
                        className="mini_container",
                    ),
                    html.Div(
                        [html.H6(id="pr-30-text"), html.P("PR - 30 Min")],
                        id="pr-30",
                        className="mini_container",
                    ),
                    html.Div(
                        [html.H6(id="pr-45-text"), html.P("PR - 45 Min")],
                        id="pr-45",
                        className="mini_container",
                    ),
                    html.Div(
                        [html.H6(id="pr-60-text"), html.P("PR - 60 Min")],
                        id="pr-60",
                        className="mini_container",
                    )
                ],
                id="pr-container",
                className="row container-display",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="top-instructors-bar")],
                        className="pretty_container six columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="workouts-per-length-bar")],
                        className="pretty_container six columns",
                    )
                ],
                className="row flex-display",
            ),
            dcc.Dropdown(
                id="histogram-measure-dropdown",
                options=[
                    {'label': 'Output', 'value': 'total_work'},
                    {'label': 'Calories', 'value': 'calories'},
                    {'label': 'Distance', 'value': 'distance'},
                    {'label': 'Difficulty', 'value': 'difficulty'},
                    {'label': 'Leaderboard Rank', 'value': 'leaderboard_pct_finish'},
                ],
                multi=False,
                value='total_work',
                persistence=True,
                persistence_type='session',
                className="dcc_control two columns"
            ),
            html.Div(
                [dcc.Graph("output-histogram")],
                className="pretty_container",
            )
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"}
    )
]

# Helper functions for filters


def parse_date(raw_date):

    if isinstance(raw_date, list):
        ret_date = parse(raw_date[0])
    else:
        ret_date = parse(raw_date)

    return ret_date

# Helper functions to create figures


def create_hours_per_month_bar(monthly_hours_df):
    monthly_hours_df['created_ym'] = monthly_hours_df['created_at'].dt.strftime('%Y-%m')
    hours_agg = monthly_hours_df.groupby('created_ym').agg({
        'id': 'nunique',
        'length': 'sum'
    }).reset_index()

    monthly_hours_fig = go.Figure(
        data=go.Bar(
            x=hours_agg['created_ym'],
            y=hours_agg['length']/60,
            customdata=hours_agg['id'],
            hovertemplate="<b>%{x}</b><br>"
                          "Hours of Exercise: %{y: .2f}<br>"
                          "# of Workouts: %{customdata}"
                          "<extra></extra>"
        )
    )

    monthly_hours_fig.update_layout(
        xaxis={
            'type': 'category'
        },
        title='Hours of Exercise Per Month',
        showlegend=False,
        plot_bgcolor='white'
    )

    return monthly_hours_fig


def create_top_instructors_bar(instructor_df):

    instructor_agg = instructor_df.groupby('instructor').agg({
        'id': 'count',
        'total_work': ['mean', 'max']
    }).reset_index()
    instructor_agg.columns = ['_'.join(col) if col[1] != '' else col[0] for col in instructor_agg.columns]
    instructor_agg.columns = ['instructor', 'workouts', 'mean_output', 'pr']
    instructor_agg = instructor_agg.sort_values('workouts', ascending=False).head(10)

    instructor_fig = go.Figure(
        data=go.Bar(
            x=instructor_agg['instructor'],
            y=instructor_agg['workouts'],
            customdata=instructor_agg[['mean_output', 'pr']],
            hovertemplate="<b>%{x}</b><br># of Workouts: %{y}<br>"
                          "Average Output: %{customdata[0]: .2f}<br>"
                          "Best Output: %{customdata}[1]: .2f}"
                          "<extra></extra>"
        )
    )

    instructor_fig.update_layout(
        xaxis={
            'categoryorder': 'total descending',
        },
        title='Top 10 Instructors',
        showlegend=False,
        plot_bgcolor='white'
    )

    return instructor_fig


def create_workouts_per_length_bar(workouts_df):

    workouts_agg = workouts_df.assign(
        length=lambda row: np.round(row['length'], 0)
    ).groupby('length').agg({
        'id': 'nunique',
        'total_work': 'mean'
    }).reset_index()
    workouts_agg = workouts_agg.loc[workouts_agg['total_work'] > 0, ]

    workout_length_fig = go.Figure(
        data=go.Bar(
            x=workouts_agg['length'],
            y=workouts_agg['id'],
            customdata=workouts_agg['total_work']/1000,
            hovertemplate="<b>%{x}</b><br># of Workouts: %{y}<br>"
                          "Average Output: %{customdata: .2f}"
                          "<extra></extra>"
        )
    )

    workout_length_fig.update_layout(
        xaxis={
            'type': 'category',
            'categoryorder': 'array',
            'categoryarray': ['5', '10', '15', '20', '30', '45', '60', '75', '90']
        },
        title='Workouts per Class Length',
        showlegend=False,
        plot_bgcolor='white'
    )

    return workout_length_fig


def create_measure_histogram(hist_df, ser_name):

    hist_dff = hist_df.loc[hist_df[ser_name] > 0, ]

    if ser_name == 'total_work':
        hist_dff.loc[:, ser_name] = hist_dff.loc[:, ser_name]/1000
        xstart = hist_dff.loc[:, ser_name].min()
        xend = hist_dff.loc[:, ser_name].max()
        xbinsize = (hist_dff.loc[:, ser_name].max()-hist_dff.loc[:, ser_name].min())/100
    elif ser_name == 'leaderboard_pct_finish':
        hist_dff.loc[:, ser_name] = hist_dff.loc[:, ser_name]*100
        xstart = 0
        xend = 100
        xbinsize = 1
    elif ser_name == 'difficulty':
        xstart = 0
        xend = 10
        xbinsize = .1
    else:
        xstart = hist_dff.loc[:, ser_name].min()
        xend = hist_dff.loc[:, ser_name].max()
        xbinsize = (hist_dff.loc[:, ser_name].max()-hist_dff.loc[:, ser_name].min())/100

    hist_fig = go.Figure(go.Histogram(
        x=hist_dff[ser_name],
        xbins={
            'start': xstart,
            'end': xend,
            'size': xbinsize
        }
    ))

    hist_fig.update_layout(
        title=f'{ser_name.replace("_", " ").capitalize()} Distribution',
        showlegend=False,
        plot_bgcolor='white',
        xaxis={
            'range': [xstart, xend]
        }
    )

    return hist_fig


# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")],
)


@app.callback(
    [
        Output("date-picker", "start_date"),
        Output("date-picker", "end_date"),
        Output("instructor-dropdown", "value"),
        Output("class-length-dropdown", "value"),
        Output("discipline-dropdown", "value")
    ],
    [
        Input("main-reset-filters", "n_clicks_timestamp"),
        Input("workouts-session-filters", "data"),
        Input("workouts-session-filters", "modified_timestamp")
    ],
    [
        State("main-session-filters", "data"),
    ]
)
def update_filters(reset, workouts_filters, workouts_ts, main_filters):
    reset = -1 if reset is None else reset
    if reset > workouts_ts:
        ret = [
            df['created_at'].min(), df['created_at'].max(), None, None, None
        ]
    else:
        if workouts_ts == -1:
            ret = [
                df['created_at'].min(), df['created_at'].max(), None, None, None
            ]
        else:
            ret = [
                workouts_filters.get('start_date'),
                workouts_filters.get('end_date'),
                workouts_filters.get('instructor'),
                workouts_filters.get('length'),
                main_filters.get('discipline')
            ]

    return ret


@app.callback(
    [
        Output("workouts-text", "children"),
        Output("output-text", "children"),
        Output("calories-text", "children"),
        Output("distance-text", "children"),
        Output("avg-leaderboard-pct-finish-text", "children"),
        Output("hours-per-month-bar", "children"),
        Output("pr-15-text", "children"),
        Output("pr-20-text", "children"),
        Output("pr-30-text", "children"),
        Output("pr-45-text", "children"),
        Output("pr-60-text", "children"),
        Output("top-instructors-bar", "figure"),
        Output("workouts-per-length-bar", "figure"),
        Output("output-histogram", "figure"),
        Output("main-session-filters", "data")
    ],
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("instructor-dropdown", "value"),
        Input("class-length-dropdown", "value"),
        Input("discipline-dropdown", "value"),
        Input("histogram-measure-dropdown", "value"),
        Input("main-session-filters", "data")
    ]
)
def update_widgets(
        start_date, end_date, instructors, class_lengths, disciplines, hist_measure, filters
):

    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    df_filtered = df.loc[
        (df['created_at'] >= start_date) &
        (df['created_at'] <= end_date) &
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

    df_filtered['leaderboard_pct_finish'] = df_filtered['leaderboard_rank']/df_filtered['total_leaderboard_users']

    # START INDICATORS
    workouts = len(df_filtered['id'].unique())
    output = round(df_filtered['total_work'].sum()/1000, 0)
    calories = round(df_filtered['calories'].sum(), 0)
    distance = round(df_filtered['distance'].sum(), 0)
    leaderboard_rank = df_filtered.loc[
        df_filtered['total_leaderboard_users'] != 0,
        'leaderboard_rank'
    ].sum()
    total_leaderboard_users = df_filtered.loc[
        df_filtered['total_leaderboard_users'] != 0,
        'total_leaderboard_users'
    ].sum()
    leaderboard_pct_finish = str(round(100*(leaderboard_rank/total_leaderboard_users), 2)) + '%'

    cycling_prs = df_filtered.loc[
        df_filtered['fitness_discipline'] == 'cycling',
    ].groupby('length').agg(
        {
            'total_work': ['max', 'mean'],
            'id': 'count'
        }
    ).reset_index()
    cycling_prs.columns = ['_'.join(col) for col in cycling_prs.columns]
    cycling_prs.columns = ['class_length', 'personal_record', 'average_output', 'rides']

    pr_15 = round(cycling_prs.loc[cycling_prs['class_length'] == 15, 'personal_record']/1000, 1)
    pr_20 = round(cycling_prs.loc[cycling_prs['class_length'] == 20, 'personal_record'] / 1000, 1)
    pr_30 = round(cycling_prs.loc[cycling_prs['class_length'] == 30, 'personal_record'] / 1000, 1)
    pr_45 = round(cycling_prs.loc[cycling_prs['class_length'] == 45, 'personal_record'] / 1000, 1)
    pr_60 = round(cycling_prs.loc[cycling_prs['class_length'] == 60, 'personal_record'] / 1000, 1)

    # END INDICATORS
    measure_hist_fig = create_measure_histogram(df_filtered, hist_measure)
    hours_per_month_fig = create_hours_per_month_bar(df_filtered)
    instructors_fig = create_top_instructors_bar(df_filtered)
    workouts_per_length_fig = create_workouts_per_length_bar(df_filtered)

    filters = {} if filters is None else filters

    filters['start_date'] = start_date
    filters['end_date'] = end_date
    filters['instructor'] = instructors
    filters['length'] = class_lengths
    filters['discipline'] = disciplines

    ret = [
        workouts, output, calories, distance, leaderboard_pct_finish,
        dcc.Graph(figure=hours_per_month_fig),
        pr_15, pr_20, pr_30, pr_45, pr_60,
        instructors_fig, workouts_per_length_fig, measure_hist_fig,
        filters
    ]

    return ret

