# Import required libraries

from utils.libs import *

from app import app

server = app.server

# get relative data folder
PATH = pathlib.Path(__file__).parent

# Load data
all_workouts, heart_rate_zones, ftp, weight = funs.get_data(PATH.parent)

df = all_workouts.loc[all_workouts['class_title'].str.contains('FTP Test'), ].sort_values('created_at')
df['total_work_prev'] = df.loc[:, 'total_work'].shift(1)
df['total_work_chg'] = df['total_work']-df['total_work_prev']
df['total_work_chg'].fillna(10000, inplace=True)
df['total_work_pct_chg'] = df['total_work_chg']/df['total_work_prev']
df['total_work_pct_chg'].fillna(0, inplace=True)
df['total_work_chg_str'] = np.where(
    df['total_work_chg'] > 0,
    '+'+np.round(df['total_work_chg']/1000, 2).astype(str),
    np.round(df['total_work_chg']/1000, 2)
)
df['ftp'] = (df['avg_power']*.95)
df['ftp_prev'] = df.loc[:, 'ftp'].shift(1)
df['ftp_chg'] = df['ftp']-df['ftp_prev']
df['ftp_chg'].fillna(10, inplace=True)
df['ftp_pct_chg'] = df['ftp_chg']/df['ftp_prev']
df['ftp_pct_chg'].fillna(0, inplace=True)
df['ftp_chg_str'] = np.where(
    df['ftp_chg'] > 0,
    '+'+np.round(df['ftp_chg'], 2).astype(str),
    np.round(df['ftp_chg'], 2)
)

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
                            html.Button("Reset All Filters", id="pz-reset-filters"),
                            html.Br(),
                            html.Br(),
                            html.P("Date Range Filter:", className="control_label"),
                            dcc.DatePickerRange(
                                id="pz-date-picker",
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
                                id="pz-instructor-dropdown",
                                options=INSTRUCTORS,
                                multi=True,
                                value=None,
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            ),
                            html.P("Weight:", className="control_label"),
                            dcc.Input(
                                type='number',
                                id="pz-weight-input",
                                debounce=True,
                                value=weight,
                                persistence=True,
                                persistence_type='session',
                                className="dcc_control"
                            )
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options-1"
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [html.H6(id="pz-ftp-text"), html.P("FTP")],
                                        id="output",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [
                                            html.H6(id="pz-ftp-improvement-text"),
                                            html.Span("FTP Improvement"),
                                            html.Br(),
                                            html.Span("*from first FTP ride", style={'font-size': '12px'})
                                        ],
                                        id="distance",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [
                                            html.H6(id="pz-pw-ratio-text"),
                                            html.A(
                                                "P/W Ratio",
                                                href='https://cdn-cyclingtips.pressidium.com/wp-content/uploads/2017/05/PowerProfile.png',
                                                target='blank'
                                            )
                                        ],
                                        id="calories",
                                        className="mini_container",
                                    )
                                ],
                                id="pz-info-container",
                                className="row container-display",
                            ),
                            dcc.Graph(id='ftp-waterfall-chart')
                        ],
                        className="pretty_container eight columns",
                        id="waterfall-container",
                    )
                ],
                className="row flex-display"
            )
        ],
        id="pz-mainContainer",
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


def create_ftp_waterfall(ftp_workouts, weight):

    init_measure = ['absolute']
    [init_measure.append(el) for el in ['relative'] * (len(ftp_workouts['created_at']) - 1)]
    init_ftp = round(float(ftp_workouts.loc[ftp_workouts['created_at'] == ftp_workouts['created_at'].min(), 'ftp']), 2)
    ftp_workouts['weight'] = weight
    ftp_workouts['p_w_ratio'] = ftp_workouts['ftp']/ftp_workouts['weight']
    fig = go.Figure()
    fig.add_trace(go.Waterfall(
        x=ftp_workouts['created_at'].dt.date,
        y=np.round(ftp_workouts['ftp_chg'], 2),
        text=[f'{el[0]} ({el[1]})' if el[1] != '+10.0' else init_ftp for el in
              zip(np.round(ftp_workouts['ftp'], 2).astype(str), ftp_workouts['ftp_chg_str'])],
        customdata=ftp_workouts[['avg_power', 'ftp_pct_chg', 'ftp', 'p_w_ratio', 'ftp_chg_str']],
        textposition='outside',
        base=(float(ftp_workouts.loc[ftp_workouts['created_at'] == ftp_workouts['created_at'].min(), 'ftp'])) - 10,
        measure=init_measure,
        hovertemplate="<b>Workout Date</b>: %{y}<br>"
                      "<b>FTP</b>: %{y: .2f}<br>"
                      "<b>P/W Ratio</b>: %{customdata[3]: .2f}<br>"
                      "<b>Average Output</b>: %{customdata[0]: .2f}<br>"
                      "<b>Absolute Change</b>: %{customdata[4]}<br>"
                      "<b>% Change</b>: %{customdata[1]: .2p}"
                      "<extra></extra>"
    ))
    fig.update_layout(
        xaxis={
            'type': 'category',
            'categoryorder': 'category ascending'
        },
        yaxis={
            'range': [
                ftp_workouts['ftp'].min()-10,
                ftp_workouts['ftp'].max()*1.1
            ]
        },
        title='FTP Progression',
        plot_bgcolor='white'
    )

    return fig


@app.callback(
    [
        Output("ftp-waterfall-chart", "figure"),
        Output("pz-ftp-text", "children"),
        Output("pz-ftp-improvement-text", "children"),
        Output("pz-pw-ratio-text", "children")
    ],
    [
        Input("pz-date-picker", "start_date"),
        Input("pz-date-picker", "end_date"),
        Input("pz-instructor-dropdown", "value"),
        Input("pz-weight-input", "value")
    ]
)
def update_widgets(
        start_date, end_date, instructors, weight
):

    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    kg = weight*0.4535924
    df['leaderboard_pct_finish'] = np.round(100*(df['leaderboard_rank'] / df['total_leaderboard_users']), 2)

    df_filtered = df.loc[
        (df['created_at'] >= start_date) &
        (df['created_at'] <= end_date)
    ]

    if instructors is not None:
        if len(instructors) > 0:
            df_filtered = df_filtered.loc[df_filtered['instructor'].isin(instructors), ]

    waterfall = create_ftp_waterfall(df, kg)
    ftp_abs_improvement = round(df_filtered.loc[df_filtered['created_at'] == end_date, 'ftp'].max() - df_filtered.loc[
        df_filtered['created_at'] == start_date, 'ftp'].min(), 2)
    ftp_pct_improvement = round(100 * (
        ftp_abs_improvement / df_filtered.loc[df_filtered['created_at'] == start_date, 'ftp'].min()), 2)
    sign = '+' if ftp_abs_improvement > 0 else ''
    ftp_improvement_text = f"{sign}{ftp_abs_improvement} ({sign}{ftp_pct_improvement}%)"
    pw_ratio = round(df_filtered.loc[df_filtered['created_at'] == end_date, 'ftp'].max()/kg, 2)
    # workouts_table = create_workouts_table(df_filtered)

    ret = [waterfall, ftp, ftp_improvement_text, pw_ratio]

    return ret


@app.callback(
    [
        Output("pz-stats", "style"),
        Output("pz-output-text", "children"),
        Output("pz-distance-text", "children"),
        Output("pz-calories-text", "children")
    ],
    [
        Input('pz-table', "selected_row_ids"),
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
        time_series = create_metrics_line_charts(workout_time_series, segments, ftp)

        indicators = [t.get('value') for t in totals]

        ret = [
            div_display, indicators[0], indicators[1], indicators[2]
        ]
    else:
        ret = [{'display': 'none'}, None, None, None]

    return ret
