import requests
import json
from math import ceil
import pandas as pd
import os

USER = os.environ.get('PELOTON_DISPLAY_NAME')
EMAIL = os.environ.get('PELOTON_EMAIL')
PWD = os.environ.get('PELOTON_PWD')
PAYLOAD = {'username_or_email': EMAIL, 'password':PWD}
LOGIN_URL = 'https://api.onepeloton.com/auth/login'
USER_URL = 'https://api.onepeloton.com/api/me'
WORKOUTS_URL = 'https://api.onepeloton.com/api/user/{}/workouts?page={}'
WORKOUT_DETAILS_URL = 'https://api.onepeloton.com/api/workout/{}'
INSTRUCTOR_URL = 'https://api.onepeloton.com/api/instructor/{}'

s = requests.Session()
s.post(LOGIN_URL, json=PAYLOAD)
me = s.get(USER_URL)

total_workouts = me.json().get('total_workouts')
pages = ceil(total_workouts/20)
userid = me.json().get('id')

workouts_df = pd.DataFrame()

for i in range(pages):
    url = WORKOUTS_URL.format(userid,i)
    dat = s.get(url)
    dats = dat.json().get('data')
    workouts_df = pd.concat([workouts_df, pd.DataFrame(dats)], axis=0)

workouts_df['created_at'] = pd.to_datetime(workouts_df['created_at'], unit='s')
workouts_df['start_time'] = pd.to_datetime(workouts_df['start_time'], unit='s')
workouts_df['created'] = pd.to_datetime(workouts_df['created'], unit='s')
workouts_df['device_time_created_at'] = pd.to_datetime(workouts_df['device_time_created_at'], unit='s')

workout_ids = list(pd.unique(workouts_df['id']))
existing_data = pd.read_excel('{}_workouts.xlsx'.format(USER))
existing_ids = existing_data['id'].values.tolist()
new_ids = [wid for wid in workout_ids if wid not in existing_ids]

if len(new_ids) > 0:
    workout_url = WORKOUT_DETAILS_URL.format(workout_ids[0])
    workout_resp = s.get(workout_url)
    workout = workout_resp.json()

    workout_info = pd.DataFrame()
    for wid in new_ids:
        workout_url = WORKOUT_DETAILS_URL.format(wid)
        workout_resp = s.get(workout_url)
        workout = workout_resp.json()
        class_title = workout.get('ride').get('title')
        length = workout.get('ride').get('pedaling_duration')/60
        difficulty = workout.get('ride').get('difficulty_rating_avg')
        instructor_id = workout.get('ride').get('instructor_id')
        d = {'workout_id': wid, 'instructor_id': instructor_id, 'class_title': [class_title], 'length': [length], 'difficulty': [difficulty]}
        df = pd.DataFrame(data=d)
        workout_info = pd.concat([workout_info, df], axis=0)

    instructor_ids = workout_info['instructor_id'].unique()
    instructors = pd.DataFrame(columns=['instructor_id','instructor','instructor_spotify_playlist'])
    for ins_id in instructor_ids:
        instructor_url = INSTRUCTOR_URL.format(ins_id)
        instructor_resp = s.get(instructor_url)
        instructor = instructor_resp.json()
        name = instructor.get('name')
        spotify_uri = instructor.get('spotify_playlist_uri')
        d = {'instructor_id': ins_id, 'instructor': [name], 'instructor_spotify_playlist': [spotify_uri]}
        df = pd.DataFrame(data=d)
        instructors = pd.concat([instructors, df], axis=0)

    new_workouts = workouts_df.merge(workout_info, left_on='id', right_on='workout_id').merge(instructors, on='instructor_id')
    all_workout_data = pd.concat([existing_data, new_workouts], axis=0)

else:
    all_workout_data = existing_data


with pd.ExcelWriter('{}_workouts.xlsx'.format(USER)) as writer:
    all_workout_data.to_excel(writer, sheet_name='workouts', index=False)


