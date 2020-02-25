from __future__ import unicode_literals

from django.shortcuts import render

from ema.views import NUMBER_OF_EMA
from user.models import Participant
from user.models import AppPackageToCategoryMap
from ema.models import Response
from sensor_data import models as sensorModels
import sensor_data.views as sensor_views
from user import views
import csv
import datetime

import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import HTTPError

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from Tools import RES_BAD_REQUEST

cat_list = pd.read_csv('Cat_group.csv')


def index(request):
    participants = Participant.objects.order_by('heartbeat_smartphone')[:200]
    context = {
        'participants': participants
    }
    return render(request=request, template_name='index.html', context=context)


@csrf_exempt
def extract_features(request, exportCSV):
    if exportCSV:
        try:
            if 'id' in request.POST:
                if not views.user_exists(request.POST['id']):
                    return JsonResponse(data={'result': 'User does NOT exist'})
                else:
                    username = request.POST['id']
                    participant = Participant.objects.get(id=username)
                    try:
                        response = HttpResponse(content_type='text/csv')
                        writer = csv.DictWriter(response, fieldnames=['User id',
                                                                      'Stress lvl',
                                                                      'Day',
                                                                      'EMA order',
                                                                      'Unlock duration',
                                                                      'Phonecall duration',
                                                                      'Phonecall number',
                                                                      'Phonecall ratio',
                                                                      'Duration STILL',
                                                                      'Duration WALKING',
                                                                      'Duration RUNNING',
                                                                      'Duration BICYCLE',
                                                                      'Duration VEHICLE',
                                                                      'Duration ON_FOOT',
                                                                      'Duration TILTING',
                                                                      'Duration UNKNOWN',
                                                                      'Freq. STILL',
                                                                      'Freq. WALKING',
                                                                      'Freq. RUNNING',
                                                                      'Freq. BICYCLE',
                                                                      'Freq. VEHICLE',
                                                                      'Freq. ON_FOOT',
                                                                      'Freq. TILTING',
                                                                      'Freq. UNKNOWN',
                                                                      'Audio min.',
                                                                      'Audio max.',
                                                                      'Audio mean',
                                                                      'Total distance',
                                                                      'Num. of places',
                                                                      'Max. distance',
                                                                      'Gyration',
                                                                      'Max. dist.(HOME)',
                                                                      'Duration(HOME)',
                                                                      'Unlock dur.(HOME)',
                                                                      'Entertainment & Music',
                                                                      'Utilities',
                                                                      'Shopping',
                                                                      'Games & Comics',
                                                                      'Others',
                                                                      'Health & Wellness',
                                                                      'Social & Communication',
                                                                      'Education',
                                                                      'Travel',
                                                                      'Art & Design & Photo',
                                                                      'News & Magazine',
                                                                      'Food & Drink',
                                                                      'Unknown & Background',
                                                                      'Sleep dur.',
                                                                      'Phonecall audio min.',
                                                                      'Phonecall audio max.',
                                                                      'Phonecall audio mean'])

                        response['Content-Disposition'] = 'attachment;filename=features(%s).csv' % username
                        writer.writeheader()

                        ema_responses = Response.objects.filter(username=participant).order_by('day_num', 'ema_order')
                        ema_length = ema_responses.__len__()
                        for index, ema_res in enumerate(ema_responses):
                            end_time = ema_res.time_responded
                            start_time = end_time - 10800  # 10800sec = 3min before each EMA
                            if start_time < 0:
                                continue
                            unlock_data = get_unlock_result(participant, start_time, end_time)
                            phonecall_data = get_phonecall_result(participant, start_time, end_time)
                            activities_total_dur = get_activities_dur_result(participant, start_time, end_time)
                            dif_activities = get_num_of_dif_activities_result(participant, start_time, end_time)
                            audio_data = get_audio_data_result(participant, start_time, end_time)
                            total_dist_data = get_total_distance_result(participant, start_time, end_time)
                            max_dist = get_max_dis_result(participant, start_time, end_time)
                            gyration = get_radius_of_gyration_result(participant, start_time, end_time)
                            max_home = get_max_dist_from_home_result(participant, start_time, end_time)
                            num_places = get_num_of_places_result(participant, start_time, end_time)
                            time_at = get_time_at_location(participant, start_time, end_time, sensor_views.LOCATION_HOME)
                            unlock_at = get_unlock_duration_at_location(participant, start_time, end_time, sensor_views.LOCATION_HOME)
                            app_usage = get_app_category_usage(participant, start_time, end_time)
                            sleep_duration = 0
                            pc_audio_data = get_pc_audio_data_result(participant, start_time, end_time)

                            if index >= NUMBER_OF_EMA and index + 6 < ema_length:  # index >= NUMBER_OF_EMA (start from second day)
                                start_hour = 18
                                end_day_hour = 10
                                date_start = datetime.datetime.fromtimestamp(ema_responses[index - 6].time_expected)
                                date_start = date_start.replace(hour=start_hour, minute=0, second=0)
                                date_end = datetime.datetime.fromtimestamp(ema_res.time_expected)
                                date_end = date_end.replace(hour=end_day_hour, minute=0, second=0)

                                sleep_duration = get_sleep_duration(participant, date_start.timestamp(), date_end.timestamp())

                            writer.writerow({'User id': participant.id,
                                             'Stress lvl': ema_res.answer1 + ema_res.answer2 + ema_res.answer3 + ema_res.answer4,
                                             'Day': ema_res.day_num,
                                             'EMA order': ema_res.ema_order,
                                             'Unlock duration': unlock_data,
                                             'Phonecall duration': phonecall_data["phone_calls_total_dur"],
                                             'Phonecall number': phonecall_data["phone_calls_total_number"],
                                             'Phonecall ratio': phonecall_data["phone_calls_ratio_in_out"],
                                             'Duration STILL': activities_total_dur["still"],
                                             'Duration WALKING': activities_total_dur["walking"],
                                             'Duration RUNNING': activities_total_dur["running"],
                                             'Duration BICYCLE': activities_total_dur["on_bicycle"],
                                             'Duration VEHICLE': activities_total_dur["in_vehicle"],
                                             'Duration ON_FOOT': activities_total_dur["on_foot"],
                                             'Duration TILTING': activities_total_dur["tilting"],
                                             'Duration UNKNOWN': activities_total_dur["unknown"],
                                             'Freq. STILL': dif_activities["still"],
                                             'Freq. WALKING': dif_activities["walking"],
                                             'Freq. RUNNING': dif_activities["running"],
                                             'Freq. BICYCLE': dif_activities["on_bicycle"],
                                             'Freq. VEHICLE': dif_activities["in_vehicle"],
                                             'Freq. ON_FOOT': dif_activities["on_foot"],
                                             'Freq. TILTING': dif_activities["tilting"],
                                             'Freq. UNKNOWN': dif_activities["unknown"],
                                             'Audio min.': audio_data['minimum'],
                                             'Audio max.': audio_data['maximum'],
                                             'Audio mean': audio_data['mean'],
                                             'Total distance': total_dist_data,
                                             'Num. of places': num_places,
                                             'Max. distance': max_dist,
                                             'Gyration': gyration,
                                             'Max. dist.(HOME)': max_home,
                                             'Duration(HOME)': time_at,
                                             'Unlock dur.(HOME)': unlock_at,
                                             'Entertainment & Music': app_usage['Entertainment & Music'],
                                             'Utilities': app_usage['Utilities'],
                                             'Shopping': app_usage['Shopping'],
                                             'Games & Comics': app_usage['Games & Comics'],
                                             'Others': app_usage['Others'],
                                             'Health & Wellness': app_usage['Health & Wellness'],
                                             'Social & Communication': app_usage['Social & Communication'],
                                             'Education': app_usage['Education'],
                                             'Travel': app_usage['Travel'],
                                             'Art & Design & Photo': app_usage['Art & Design & Photo'],
                                             'News & Magazine': app_usage['News & Magazine'],
                                             'Food & Drink': app_usage['Food & Drink'],
                                             'Unknown & Background': app_usage['Unknown & Background'],
                                             'Sleep dur.': sleep_duration,
                                             'Phonecall audio min.': pc_audio_data['minimum'],
                                             'Phonecall audio max.': pc_audio_data['maximum'],
                                             'Phonecall audio mean': pc_audio_data['mean']})

                        return response
                    except Exception as ex:
                        print(type(ex))
                    pass
            else:
                return JsonResponse(data={'result': 'This user does not exist'})
        except ValueError as e:
            print(str(e))
            return JsonResponse(data={'result': RES_BAD_REQUEST, 'reason': 'user id was not passed as a POST argument!'})
    else:
        return render(request=request, template_name='data_extractor.html')


def ema_per_person(request, user_id):
    participant = Participant.objects.get(id=user_id)
    ema_responses = Response.objects.filter(username=user_id).order_by('day_num', 'ema_order')[:400]
    context = {
        'id': user_id,
        'day_num': participant.current_day_num(),
        'name': participant.name,
        'ema_responses': ema_responses
    }
    return render(request=request, template_name='ema-per-person.html', context=context)


@csrf_exempt
def feature_extract(request):
    participants = Participant.objects.all()
    print("Name,"
          "Stress,"
          "Day,"
          "EMA,"
          "Unlock_dur,"
          "PhoneCall_dur,"
          "PhoneCall_number,"
          "PhoneCall_ratio,"
          "duration_still,"
          "duration_walking,"
          "duration_running,"
          "duration_bicycle,"
          "duration_vehicle,"
          "duration_on_foot,"
          "duration_tilting,"
          "duration_unknown,"
          "number_still,"
          "number_walking,"
          "number_running,"
          "number_bicycle,"
          "number_vehicle,"
          "number_on_foot,"
          "number_tilting,"
          "number_unknown,"
          "audio_min,"
          "audio_max,"
          "audio_mean,"
          "total_dist,"
          "num_places,"
          "max_dist,"
          "gyration,"
          "dist_home,"
          "time_at_home,"
          "unlock_at_home,"
          # "Entertainment & Music,"
          # "Utilities,"
          # "Shopping,"
          # "Games & Comics,"
          # "Others,"
          # "Health & Wellness,"
          # "Social & Communication,"
          # "Education,"
          # "Travel,"
          # "Art & Design & Photo,"
          # "News & Magazine,"
          # "Food & Drink,"
          # "Unknown & Background,"
          "sleep_dur,"
          "pc_audio_min,"
          "pc_audio_max,"
          "pc_audio_mean")

    for participant in participants:
        ema_responses = Response.objects.filter(username=participant).order_by('day_num', 'ema_order')
        ema_length = ema_responses.__len__()
        for index, ema_res in enumerate(ema_responses):
            end_time = ema_res.time_responded
            start_time = end_time - 10800  # 10800sec = 3min before each EMA

            unlock_data = get_unlock_result(participant, start_time, end_time)
            phonecall_data = get_phonecall_result(participant, start_time, end_time)
            activities_total_dur = get_activities_dur_result(participant, start_time, end_time)
            dif_activities = get_num_of_dif_activities_result(participant, start_time, end_time)
            audio_data = get_audio_data_result(participant, start_time, end_time)
            total_dist_data = get_total_distance_result(participant, ema_res.day_num, ema_res.ema_order)
            max_dist = get_max_dis_result(participant, ema_res.day_num, ema_res.ema_order)
            gyration = get_radius_of_gyration_result(participant, ema_res.day_num, ema_res.ema_order)
            max_home = get_max_dist_from_home_result(participant, ema_res.day_num, ema_res.ema_order)
            num_places = get_num_of_places_result(participant, ema_res.day_num, ema_res.ema_order)
            time_at = get_time_at_location(participant, start_time, end_time, sensor_views.LOCATION_HOME)
            unlock_at = get_unlock_duration_at_location(participant, start_time, end_time, sensor_views.LOCATION_HOME)
            # app_usage = get_app_category_usage(participant, start_time, end_time)
            sleep_duration = 0
            pc_audio_data = get_pc_audio_data_result(participant, start_time, end_time)

            if index >= NUMBER_OF_EMA and index + 6 < ema_length:  # index >= NUMBER_OF_EMA (start from second day)
                start_hour = 18
                end_day_hour = 10
                date_start = datetime.datetime.fromtimestamp(ema_responses[index - 6].time_expected)
                date_start = date_start.replace(hour=start_hour, minute=0, second=0)
                date_end = datetime.datetime.fromtimestamp(ema_res.time_expected)
                date_end = date_end.replace(hour=end_day_hour, minute=0, second=0)

                sleep_duration = get_sleep_duration(participant, date_start.timestamp(), date_end.timestamp())

            print(participant.name, ',',
                  ema_res.answer1, ',',
                  ema_res.day_num, ',',
                  ema_res.ema_order, ',',
                  unlock_data, ',',
                  phonecall_data["phone_calls_total_dur"], ',',
                  phonecall_data["phone_calls_total_number"], ',',
                  phonecall_data["phone_calls_ratio_in_out"], ',',
                  activities_total_dur["still"], ',',
                  activities_total_dur["walking"], ',',
                  activities_total_dur["running"], ',',
                  activities_total_dur["on_bicycle"], ',',
                  activities_total_dur["in_vehicle"], ',',
                  activities_total_dur["on_foot"], ',',
                  activities_total_dur["tilting"], ',',
                  activities_total_dur["unknown"], ',',
                  dif_activities["still"], ',',
                  dif_activities["walking"], ',',
                  dif_activities["running"], ',',
                  dif_activities["on_bicycle"], ',',
                  dif_activities["in_vehicle"], ',',
                  dif_activities["on_foot"], ',',
                  dif_activities["tilting"], ',',
                  dif_activities["unknown"], ',',
                  audio_data['minimum'], ',',
                  audio_data['maximum'], ',',
                  audio_data['mean'], ',',
                  total_dist_data, ',',
                  num_places, ',',
                  max_dist, ',',
                  gyration, ',',
                  max_home, ',',
                  time_at, ',',
                  unlock_at, ',',
                  # app_usage['Entertainment & Music'], ',',
                  # app_usage['Utilities'], ',',
                  # app_usage['Shopping'], ',',
                  # app_usage['Games & Comics'], ',',
                  # app_usage['Others'], ',',
                  # app_usage['Health & Wellness'], ',',
                  # app_usage['Social & Communication'], ',',
                  # app_usage['Education'], ',',
                  # app_usage['Travel'], ',',
                  # app_usage['Art & Design & Photo'], ',',
                  # app_usage['News & Magazine'], ',',
                  # app_usage['Food & Drink'], ',',
                  # app_usage['Unknown & Background'], ',',
                  sleep_duration, ',',
                  pc_audio_data['minimum'], ',',
                  pc_audio_data['maximum'], ',',
                  pc_audio_data['mean'])

            '''print("Name: {0};\t"
                  "Stress: {1};\t"
                  "Day: {2};\t"
                  "EMA: {3};\t"
                  "Unlock_dur: {4};\t"
                  "PhoneCall_dur: {5};\t"
                  "PhoneCall_number: {6};\t"
                  "PhoneCall_ratio: {7};\t"
                  "duration_still: {6};\t"
                  "duration_walking: {7};\t"
                  "duration_running: {8};\t"
                  "duration_bicycle: {9};\t"
                  "duration_vehicle: {10};\t"
                  "duration_on_foot: {11};\t"
                  "duration_tilting: {12};\t"
                  "duration_unknown: {13};\t"
                  "number_still: {14};\t"
                  "number_walking: {15};\t"
                  "number_running: {16};\t"
                  "number_bicycle: {17};\t"
                  "number_vehicle: {18};\t"
                  "number_on_foot: {19};\t"
                  "number_tilting: {20};\t"
                  "number_unknown: {21};\t"
                  "audio_min: {22};\t"
                  "audio_max: {23};\t"
                  "audio_mean: {24};\t"
                  "total_dist: {25};\t"
                  "num_places: {26};\t"
                  "max_dist: {27};\t"
                  "gyration: {28};\t"
                  "dist_home: {29};\t"
                  "time_at_home: {30};\t"
                  "unlock_at_home: {31};\t".format(participant.name,
                                                   ema_res.answer1,
                                                   ema_res.day_num,
                                                   ema_res.ema_order,
                                                   unlock_data,
                                                   phonecall_data["phone_calls_total_dur"],
                                                   phonecall_data["phone_calls_total_number"],
                                                   phonecall_data["phone_calls_ratio_in_out"],
                                                   activities_total_dur["still"],
                                                   activities_total_dur["walking"],
                                                   activities_total_dur["running"],
                                                   activities_total_dur["on_bicycle"],
                                                   activities_total_dur["in_vehicle"],
                                                   activities_total_dur["on_foot"],
                                                   activities_total_dur["tilting"],
                                                   activities_total_dur["unknown"],
                                                   dif_activities["still"],
                                                   dif_activities["walking"],
                                                   dif_activities["running"],
                                                   dif_activities["on_bicycle"],
                                                   dif_activities["in_vehicle"],
                                                   dif_activities["on_foot"],
                                                   dif_activities["tilting"],
                                                   dif_activities["unknown"],
                                                   audio_data['minimum'],
                                                   audio_data['maximum'],
                                                   audio_data['mean'],
                                                   total_dist_data,
                                                   num_places,
                                                   max_dist,
                                                   gyuration,
                                                   max_home,
                                                   time_at,
                                                   unlock_at))
                                                   '''

    return render(request=request, template_name='data_extractor.html')


def get_phonecall_result(participant, start_time, end_time):
    result = {
        "phone_calls_total_dur": 0,
        "phone_calls_total_number": 0,
        "phone_calls_ratio_in_out": 0
    }

    total_in = 0
    total_out = 0
    phone_calls_data = sensorModels.phone_calls.objects.filter(username=participant, timestamp_start__range=[start_time * 1000, end_time * 1000], timestamp_end__range=[start_time * 1000, end_time * 1000])
    for f2 in phone_calls_data:
        result["phone_calls_total_dur"] += f2.duration
        if f2.call_type == "IN":
            total_in += 1
        elif f2.call_type == "OUT":
            total_out += 1

    if result["phone_calls_total_dur"] > 0:
        result["phone_calls_total_number"] = total_in + total_out
        result["phone_calls_ratio_in_out"] = total_in / total_out if total_out > 0 else "-"
    else:
        result["phone_calls_total_dur"] = "-"
        result["phone_calls_total_number"] = "-"
        result["phone_calls_ratio_in_out"] = "-"

    return result


def get_unlock_result(participant, start_time, end_time):
    result = 0
    unlock_data = sensorModels.unlocked_dur.objects.filter(username=participant, timestamp_start__range=[start_time * 1000, end_time * 1000], timestamp_end__range=[start_time * 1000, end_time * 1000])
    for f1 in unlock_data:
        result += f1.duration

    return result if result > 0 else "-"


def get_activities_dur_result(participant, start_time, end_time):
    result = {
        "still": 0,
        "walking": 0,
        "running": 0,
        "on_bicycle": 0,
        "in_vehicle": 0,
        "on_foot": 0,
        "tilting": 0,
        "unknown": 0
    }

    activities_dur_data = sensorModels.activity_duration.objects.filter(username=participant, timestamp_start__range=[start_time * 1000, end_time * 1000], timestamp_end__range=[start_time * 1000, end_time * 1000])
    for f3 in activities_dur_data:
        if f3.activity_type == 'STILL':
            result['still'] += f3.duration
        elif f3.activity_type == 'WALKING':
            result['walking'] += f3.duration
        elif f3.activity_type == 'RUNNING':
            result['running'] += f3.duration
        elif f3.activity_type == 'ON_BICYCLE':
            result['on_bicycle'] += f3.duration
        elif f3.activity_type == 'IN_VEHICLE':
            result['in_vehicle'] += f3.duration
        elif f3.activity_type == 'ON_FOOT':
            result['on_foot'] += f3.duration
        elif f3.activity_type == 'TILTING':
            result['tilting'] += f3.duration
        elif f3.activity_type == 'UNKNOWN':
            result['unknown'] += f3.duration

    if result['still'] == 0:
        result['still'] = "-"
    if result['walking'] == 0:
        result['walking'] = "-"
    if result['running'] == 0:
        result['running'] = "-"
    if result['on_bicycle'] == 0:
        result['on_bicycle'] = "-"
    if result['in_vehicle'] == 0:
        result['in_vehicle'] = "-"
    if result['on_foot'] == 0:
        result['on_foot'] = "-"
    if result['tilting'] == 0:
        result['tilting'] = "-"
    if result['unknown'] == 0:
        result['unknown'] = "-"

    return result


def get_num_of_dif_activities_result(participant, start_time, end_time):
    result = {
        "still": 0,
        "walking": 0,
        "running": 0,
        "on_bicycle": 0,
        "in_vehicle": 0,
        "on_foot": 0,
        "tilting": 0,
        "unknown": 0
    }

    activities_data = sensorModels.activities.objects.filter(username=participant, timestamp__range=[start_time * 1000, end_time * 1000])
    for data in activities_data:
        if data.activity_type == 'STILL':
            result['still'] += 1
        elif data.activity_type == 'WALKING':
            result['walking'] += 1
        elif data.activity_type == 'RUNNING':
            result['running'] += 1
        elif data.activity_type == 'ON_BICYCLE':
            result['on_bicycle'] += 1
        elif data.activity_type == 'IN_VEHICLE':
            result['in_vehicle'] += 1
        elif data.activity_type == 'ON_FOOT':
            result['on_foot'] += 1
        elif data.activity_type == 'TILTING':
            result['tilting'] += 1
        elif data.activity_type == 'UNKNOWN':
            result['unknown'] += 1

    if result['still'] == 0:
        result['still'] = "-"
    if result['walking'] == 0:
        result['walking'] = "-"
    if result['running'] == 0:
        result['running'] = "-"
    if result['on_bicycle'] == 0:
        result['on_bicycle'] = "-"
    if result['in_vehicle'] == 0:
        result['in_vehicle'] = "-"
    if result['on_foot'] == 0:
        result['on_foot'] = "-"
    if result['tilting'] == 0:
        result['tilting'] = "-"
    if result['unknown'] == 0:
        result['unknown'] = "-"

    return result


def get_audio_data_result(participant, start_time, end_time):
    result = {
        "minimum": 0,
        "maximum": 0,
        "mean": 0
    }

    audio_data = sensorModels.audio_loudness.objects.values_list('value', flat=True).filter(username=participant, timestamp__range=[start_time * 1000, end_time * 1000])
    total_samples = audio_data.__len__()
    result['minimum'] = min(audio_data) if total_samples > 0 else "-"
    result['maximum'] = max(audio_data) if total_samples > 0 else "-"
    result['mean'] = sum(audio_data) / total_samples if total_samples > 0 else "-"

    return result


def get_total_distance_result(participant, start_time, end_time):
    result = sensorModels.total_dist_covered.objects.values_list("value", flat=True).filter(username=participant, timestamp_start__range=[start_time * 1000, end_time * 1000])
    return result[0] if result else "-"


def get_max_dis_result(participant, start_time, end_time):
    result = sensorModels.max_dist_two_locations.objects.values_list("value", flat=True).filter(username=participant, timestamp_start__range=[start_time * 1000, end_time * 1000])
    return result[0] if result else "-"


def get_radius_of_gyration_result(participant, start_time, end_time):
    result = sensorModels.radius_of_gyration.objects.values_list("value", flat=True).filter(username=participant, timestamp_start__range=[start_time * 1000, end_time * 1000])
    return result[0] if result else "-"


def get_max_dist_from_home_result(participant, start_time, end_time):
    result = sensorModels.max_dist_from_home.objects.values_list("value", flat=True).filter(username=participant, timestamp_start__range=[start_time * 1000, end_time * 1000])
    return result[0] if result else "-"


def get_num_of_places_result(participant, start_time, end_time):
    result = sensorModels.num_of_dif_places.objects.values_list("value", flat=True).filter(username=participant, timestamp_start__range=[start_time * 1000, end_time * 1000])
    return result[0] if result else "-"


def get_time_at_location(participant, enter_time, exit_time, location_name):
    result = 0
    geofencing_data = sensorModels.geofencing.objects.filter(username=participant, timestamp_enter__range=[enter_time * 1000, exit_time * 1000], timestamp_exit__range=[enter_time * 1000, exit_time * 1000], location=location_name)
    for data in geofencing_data:
        result += (data.timestamp_exit - data.timestamp_enter) / 1000
    return result if result > 0 else "-"


def get_unlock_duration_at_location(participant, enter_time, exit_time, location_name):
    result = 0

    geofencing_data = sensorModels.geofencing.objects.filter(username=participant, timestamp_enter__range=[enter_time * 1000, exit_time * 1000], timestamp_exit__range=[enter_time * 1000, exit_time * 1000], location=location_name)
    for data in geofencing_data:
        start = data.timestamp_enter
        end = data.timestamp_exit
        unlock_data = sensorModels.unlocked_dur.objects.filter(username=participant, timestamp_start__range=[start, end], timestamp_end__range=[start, end])
        for unl in unlock_data:
            result += unl.duration

    return result if result > 0 else "-"


def get_app_category_usage(participant, start_time, end_time):
    result = {
        "Entertainment & Music": 0,
        "Utilities": 0,
        "Shopping": 0,
        "Games & Comics": 0,
        "Others": 0,
        "Health & Wellness": 0,
        "Social & Communication": 0,
        "Education": 0,
        "Travel": 0,
        "Art & Design & Photo": 0,
        "News & Magazine": 0,
        "Food & Drink": 0,
        "Unknown & Background": 0
    }

    app_usage_data = sensorModels.app_usage_stats.objects.filter(username=participant, start_timestamp__range=[start_time, end_time], end_timestamp__range=[start_time, end_time])
    for data in app_usage_data:

        app_package, created = AppPackageToCategoryMap.objects.get_or_create(package_name=data.package_name)
        if created:
            category = getGoogleCategory(data.package_name)
            app_package.category = category
            app_package.save()
        else:
            print("Duplicate package name", app_package.package_name)
            category = app_package.category

        if category == "Entertainment & Music":
            result['Entertainment & Music'] += data.total_time_in_foreground
        elif category == "Utilities":
            result['Utilities'] += data.total_time_in_foreground
        elif category == "Shopping":
            result['Shopping'] += data.total_time_in_foreground
        elif category == "Games & Comics":
            result['Games & Comics'] += data.total_time_in_foreground
        elif category == "Others":
            result['Others'] += data.total_time_in_foreground
        elif category == "Health & Wellness":
            result['Health & Wellness'] += data.total_time_in_foreground
        elif category == "Social & Communication":
            result['Social & Communication'] += data.total_time_in_foreground
        elif category == "Education":
            result['Education'] += data.total_time_in_foreground
        elif category == "Travel":
            result['Travel'] += data.total_time_in_foreground
        elif category == "Art & Design & Photo":
            result['Art & Design & Photo'] += data.total_time_in_foreground
        elif category == "News & Magazine":
            result['News & Magazine'] += data.total_time_in_foreground
        elif category == "Food & Drink":
            result['Food & Drink'] += data.total_time_in_foreground
        elif category == "Unknown & Background":
            result['Unknown & Background'] += data.total_time_in_foreground

    if result['Entertainment & Music'] == 0:
        result['Entertainment & Music'] = "-"
    if result['Utilities'] == 0:
        result['Utilities'] = "-"
    if result['Shopping'] == 0:
        result['Shopping'] = "-"
    if result['Games & Comics'] == 0:
        result['Games & Comics'] = "-"
    if result['Others'] == 0:
        result['Others'] = "-"
    if result['Health & Wellness'] == 0:
        result['Health & Wellness'] = "-"
    if result['Social & Communication'] == 0:
        result['Social & Communication'] = "-"
    if result['Education'] == 0:
        result['Education'] = "-"
    if result['Travel'] == 0:
        result['Travel'] = "-"
    if result['Art & Design & Photo'] == 0:
        result['Art & Design & Photo'] = "-"
    if result['News & Magazine'] == 0:
        result['News & Magazine'] = "-"
    if result['Food & Drink'] == 0:
        result['Food & Drink'] = "-"
    if result['Unknown & Background'] == 0:
        result['Unknown & Background'] = "-"

    return result


def get_sleep_duration(participant, start_time, end_time):
    result = 0
    durations = []
    screen_on_data = sensorModels.screen_on_dur.objects.filter(username=participant, timestamp_start__range=[start_time * 1000, end_time * 1000])
    length = screen_on_data.__len__()
    for index, obj in enumerate(screen_on_data):
        if index + 1 < length:
            durations.append((screen_on_data[index + 1].timestamp_start - obj.timestamp_end) / 1000)
    if durations:
        result = max(durations)
    return result if result > 0 else "-"


# audio features during phone calls
def get_pc_audio_data_result(participant, start_time, end_time):
    result = {
        "minimum": 0,
        "maximum": 0,
        "mean": 0
    }

    print("start1: ", start_time, "   end1: ", end_time)
    phone_calls_data = sensorModels.phone_calls.objects.filter(username=participant, timestamp_start__range=[start_time * 1000, end_time * 1000], timestamp_end__range=[start_time * 1000, end_time * 1000])
    if phone_calls_data.__len__() > 0:
        for pc in phone_calls_data:
            print("start: ", pc.timestamp_start, "   end: ", pc.timestamp_end)
            audio_data = sensorModels.audio_loudness.objects.values_list('value', flat=True).filter(username=participant, timestamp__range=[pc.timestamp_start, pc.timestamp_end])
            total_samples = audio_data.__len__()
            result['minimum'] = min(audio_data) if total_samples > 0 else "-"
            result['maximum'] = max(audio_data) if total_samples > 0 else "-"
            result['mean'] = sum(audio_data) / total_samples if total_samples > 0 else "-"
    else:
        result['minimum'] = "-"
        result['maximum'] = "-"
        result['mean'] = "-"

    return result


def getGoogleCategory(App):
    url = "https://play.google.com/store/apps/details?id=" + App
    grouped_Category = ""
    try:
        html = urlopen(url)
        source = html.read()
        html.close()

        soup = BeautifulSoup(source, 'html.parser')
        table = soup.find_all("a", {'itemprop': 'genre'})

        genre = table[0].get_text()

        grouped = cat_list[cat_list['App Category'] == genre]['Grouped Category'].values
        # print(grouped)

        if len(grouped) > 0:
            grouped_Category = grouped[0]
        else:
            grouped_Category = 'NotMapped'
    except HTTPError as e:
        grouped_Category = 'Unknown or Background'

    finally:
        print("Pckg: ", App, ";   Category: ", grouped_Category)
        return grouped_Category
