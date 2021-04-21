from utils.libs import *


def explode_str(df, col, sep):
    s = df[col]
    i = np.arange(len(s)).repeat(s.str.count(sep) + 1)
    return df.iloc[i].assign(**{col: sep.join(s).split(sep)})


def get_data(update_all_data=0):
    USER = os.environ.get('PELOTON_USER')
    EMAIL = os.environ.get('PELOTON_EMAIL')
    PWD = os.environ.get('PELOTON_PWD')
    PAYLOAD = {
        'username_or_email': EMAIL,
        'password': PWD
    }
    BASE_URL = 'https://api.onepeloton.com'
    BASE_API_URL = f'{BASE_URL}/api'
    LOGIN_URL = f'{BASE_URL}/auth/login'
    USER_URL = f'{BASE_API_URL}/me'

    s = requests.Session()
    s.post(LOGIN_URL, json=PAYLOAD)
    me = s.get(USER_URL)

    total_workouts = me.json().get('total_workouts')
    pages = math.ceil(total_workouts / 20)
    userid = me.json().get('id')

    WORKOUTS_URL = f'{BASE_API_URL}/user/{userid}/workouts'

    workouts_df = pd.DataFrame()

    for i in range(pages):
        url = WORKOUTS_URL + '?page={}'.format(i)
        dat = s.get(url)
        dats = dat.json().get('data')
        workouts_df = pd.concat([workouts_df, pd.DataFrame(dats)], axis=0)

    workouts_df['created_at'] = pd.to_datetime(workouts_df['created_at'], unit='s')
    workouts_df['start_time'] = pd.to_datetime(workouts_df['start_time'], unit='s')
    workouts_df['created'] = pd.to_datetime(workouts_df['created'], unit='s')
    workouts_df['device_time_created_at'] = pd.to_datetime(workouts_df['device_time_created_at'], unit='s')

    workout_ids = list(pd.unique(workouts_df['id']))
    try:
        existing_data = pd.read_excel('data/{}_workouts.xlsx'.format(USER), sheet_name='workouts')
        existing_ids = existing_data['id'].values.tolist()
    except FileNotFoundError:
        update_all_data = 1

    WORKOUT_DETAILS_URL = f'{BASE_API_URL}/workout'
    INSTRUCTOR_URL = f'{BASE_API_URL}/instructor'
    METRICS = f'{WORKOUT_DETAILS_URL}/performance_graph'

    workout_info = pd.DataFrame()
    if len(existing_ids) > 0 or update_all_data:
        if update_all_data:
            new_ids = existing_ids
            print("Updating all data..")
        else:
            new_ids = [wid for wid in workout_ids if wid not in existing_ids]

        for wid in new_ids:
            workout_url = WORKOUT_DETAILS_URL + '/{}'.format(wid)
            metrics_url = workout_url + '/performance_graph'
            summary_url = workout_url + '/summary'
            workout = s.get(workout_url).json()
            summary = s.get(summary_url).json()
            #         metrics = s.get(metrics_url).json()
            d = {
                'workout_id': wid,
                'instructor_id': workout.get('ride').get('instructor_id'),
                'class_title': workout.get('ride').get('title'),
                'length': int(math.floor(round(workout.get('ride').get('pedaling_duration') / 60, 0) / 5) * 5),
                'difficulty': workout.get('ride').get('difficulty_rating_avg'),
                'leaderboard_rank': workout.get('leaderboard_rank'),
                'total_leaderboard_users': workout.get('total_leaderboard_users'),
                'max_power': [summary.get('max_power')],
                'avg_power': [summary.get('avg_power')],
                'max_cadence': [summary.get('max_cadence')],
                'avg_cadence': [summary.get('avg_cadence')],
                'max_resistance': [summary.get('max_resistance')],
                'avg_resistance': [summary.get('avg_resistance')],
                'max_speed': [summary.get('max_speed')],
                'avg_speed': [summary.get('avg_speed')],
                'max_heart_rate': [summary.get('max_heart_rate')],
                'avg_heart_rate': [summary.get('avg_heart_rate')],
                'distance': [summary.get('distance')],
                'calories': [summary.get('calories')]
            }
            df = pd.DataFrame(data=d)
            workout_info = pd.concat([workout_info, df], axis=0)

        instructor_ids = workout_info['instructor_id'].unique()
        instructors = pd.DataFrame(columns=['instructor_id', 'instructor', 'instructor_spotify_playlist'])
        for ins_id in instructor_ids:
            instructor_url = INSTRUCTOR_URL + '/{}'.format(ins_id)
            instructor_resp = s.get(instructor_url)
            instructor = instructor_resp.json()
            name = instructor.get('name')
            spotify_uri = instructor.get('spotify_playlist_uri')
            d = {'instructor_id': ins_id, 'instructor': [name], 'instructor_spotify_playlist': [spotify_uri]}
            df = pd.DataFrame(data=d)
            instructors = pd.concat([instructors, df], axis=0)

        new_workouts = workouts_df.merge(workout_info, left_on='id', right_on='workout_id').merge(instructors,
                                                                                                  on='instructor_id')
        all_workout_data = pd.concat([existing_data, new_workouts], axis=0, sort=False)

    else:
        all_workout_data = existing_data

    all_workout_data['leaderboard_rank_pct_of_total'] = np.where(
        pd.isna(all_workout_data['leaderboard_rank']) | pd.isna(all_workout_data['total_leaderboard_users']),
        0,
        all_workout_data['leaderboard_rank'] / all_workout_data['total_leaderboard_users']
    )

    all_workout_data['power_zone'] = all_workout_data['class_title'].str.contains('Power Zone').fillna(0).astype(int)

    with pd.ExcelWriter('data/{}_workouts.xlsx'.format(USER)) as writer:
        all_workout_data.to_excel(writer, sheet_name='workouts', index=False)

    return all_workout_data


def get_controls(controls_df, ser_name):
    ret_df = controls_df.assign(
        label=lambda row: row[ser_name],
        value=lambda row: row[ser_name]
    )[['label', 'value']].drop_duplicates()
    ret_df = ret_df.loc[~pd.isna(ret_df['label']), ]

    return ret_df.sort_values('label').to_dict(orient='records')
