from utils.libs import *


def explode_str(df, col, sep):
    s = df[col]
    i = np.arange(len(s)).repeat(s.str.count(sep) + 1)
    return df.iloc[i].assign(**{col: sep.join(s).split(sep)})


def api_login(BASE_URL, BASE_API_URL):
    EMAIL = os.environ.get('PELOTON_EMAIL')
    data_file_name = re.sub('[@.]', '_', EMAIL)
    PWD = os.environ.get('PELOTON_PWD')
    PAYLOAD = {
        'username_or_email': EMAIL,
        'password': PWD
    }
    LOGIN_URL = f'{BASE_URL}/auth/login'
    USER_URL = f'{BASE_API_URL}/me'

    s = requests.Session()
    s.post(LOGIN_URL, json=PAYLOAD)
    me = s.get(USER_URL)

    return s, me, data_file_name


def get_data(PATH, update_all_data=0):

    BASE_URL = 'https://api.onepeloton.com'
    BASE_API_URL = f'{BASE_URL}/api'

    s, me, data_file_name = api_login(BASE_URL, BASE_API_URL)

    heart_rate_zones = me.json().get('default_heart_rate_zones')
    ftp = me.json().get('cycling_workout_ftp')
    weight = me.json().get('weight')

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
        existing_data = pd.read_excel('{}/data/{}_workouts.xlsx'.format(PATH, data_file_name), sheet_name='workouts')
        existing_ids = existing_data['id'].values.tolist()
    except FileNotFoundError:
        existing_data = pd.DataFrame()
        existing_ids = []
        update_all_data = 1

    WORKOUT_DETAILS_URL = f'{BASE_API_URL}/workout'
    INSTRUCTOR_URL = f'{BASE_API_URL}/instructor'

    workout_info = pd.DataFrame()
    if update_all_data:
        print("Getting all of your data, this may take a few minutes..")
        new_ids = workout_ids
    else:
        new_ids = [wid for wid in workout_ids if wid not in existing_ids]

    if len(new_ids) > 0:
        for wid in new_ids:
            workout_url = WORKOUT_DETAILS_URL + '/{}'.format(wid)
            summary_url = workout_url + '/summary'
            workout = s.get(workout_url).json()
            summary = s.get(summary_url).json()
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

        try:
            all_workout_data['leaderboard_rank_pct_of_total'] = np.where(
                pd.isna(all_workout_data['leaderboard_rank']) | pd.isna(all_workout_data['total_leaderboard_users']),
                0,
                all_workout_data['leaderboard_rank'] / all_workout_data['total_leaderboard_users']
            )
        except ZeroDivisionError:
            all_workout_data['leaderboard_rank_pct_of_total'] = 0

        all_workout_data['power_zone'] = all_workout_data['class_title'].str.contains('Power Zone').fillna(0).astype(int)

    else:
        all_workout_data = existing_data

    with pd.ExcelWriter('{}/data/{}_workouts.xlsx'.format(PATH, data_file_name)) as writer:
        all_workout_data.to_excel(writer, sheet_name='workouts', index=False)

    return all_workout_data, heart_rate_zones, ftp, weight


def get_controls(controls_df, ser_name):
    ret_df = controls_df.assign(
        label=lambda row: row[ser_name],
        value=lambda row: row[ser_name]
    )[['label', 'value']].drop_duplicates()
    ret_df = ret_df.loc[~pd.isna(ret_df['label']), ]

    return ret_df.sort_values('label').to_dict(orient='records')


def get_workout_metrics(workout_id):
    BASE_URL = 'https://api.onepeloton.com'
    BASE_API_URL = f'{BASE_URL}/api'

    s, me, data_file_name = api_login(BASE_URL, BASE_API_URL)

    WORKOUT_DETAILS_URL = f'{BASE_API_URL}/workout'
    workout_url = WORKOUT_DETAILS_URL + '/{}'.format(workout_id)
    metrics_url = workout_url + '/performance_graph'

    workout = s.get(workout_url).json()
    workout_metrics = s.get(metrics_url).json()

    workout_segments = workout_metrics.get('segment_list')
    # [m.get('values') for m in workout_metrics.get('metrics')]
    metrics_dict = dict()
    for m in workout_metrics.get('metrics'):
        metrics_dict[m.get('slug')] = {
            'display_name': m.get('display_name'),
            'max': m.get('max_value'),
            'average': m.get('average_value'),
            'values': m.get('values')
        }

        if m.get('slug') == 'heart_rate':
            metrics_dict[m.get('slug')]['hr_zones'] = m.get('zones')

    return workout_metrics, metrics_dict

