__author__ = 'Ciuv'

import os
from django.shortcuts import *
from django.http import HttpResponse
from django.conf import settings
import json
import math
from wind_map.libs.wind_barb_svg_generator import wind_barb_svg_generator


def wind_map(request):
    # files reading
    u_wind_data_file = open(os.path.join(settings.BASE_PATH, 'wind_map/static/docs/u-component.csv'))
    v_wind_data_file = open(os.path.join(settings.BASE_PATH, 'wind_map/static/docs/v-component.csv'))
    try:
        wind_data_input = {'u_component': u_wind_data_file.read(), 'v_component': v_wind_data_file.read()}
    finally:
        u_wind_data_file.close()
        v_wind_data_file.close()

    # making matrix, for example: [[-9.4, -9.1, -8.8,..],[-5.1, -4.8, -4.5,..],..] -> x[lat][lon]
    wind_data = {
        'u_data': [split_section[360:] + split_section[:360] for split_section in
                   [split_part.split(',') for split_part in wind_data_input['u_component'].splitlines()]],
        'v_data': [split_section[360:] + split_section[:360] for split_section in
                   [split_part.split(',') for split_part in wind_data_input['v_component'].splitlines()]]
    }
    # len([[x, y,..],[x, y,..],..]) = 361 = lat axis(90,0,-90); len([x, y,..]) = 720 = lon axis(0,180,-179.5,-0.5)

    if request.method == 'POST':
        map_data = json.loads(request.body)
        # start point = top-left corner
        start_point = {'latitude': float(map_data['top']), 'longitude': float(map_data['left'])}
        # end point = bottom-right corner
        end_point = {'latitude': float(map_data['bot']), 'longitude': float(map_data['right'])}
        # distance between left and right edges of the map in longitudes
        lat_dist = int(round(float(map_data['lat_dist'])))
        # distance between top and bottom edges of the map in latitudes
        lon_dist = int(round(float(map_data['lon_dist'])))
        # zoom level in google maps
        zoom_level = int(map_data['zoom'])
        # post count, for drawing only last post request
        post_count = (map_data['post_count'])

        # here we dynamic make distance between points(how often we need to display markers), for better perception
        lat_step = 1+int(round(float(float(lat_dist)/(8+zoom_level*2))))*2  # between longitudes
        lon_step = 1+int(round(float(float(lon_dist)/(4+zoom_level*3))))*2  # between latitudes

        # converting latitude and longitude of start point to our matrix format.
        if start_point['latitude'] >= 0:
            start_point_lat = int(round(180-start_point['latitude']*2))-2
            end_point_lat = int(round(180-end_point['latitude']*2))
        else:
            start_point_lat = int(round(180-start_point['latitude']*2))-2
            end_point_lat = int(round(180-end_point['latitude']*2))
        if start_point['longitude'] >= 0:
            start_point_lon = int(round(360+start_point['longitude']*2))-4
            end_point_lon = int(round(360+end_point['longitude']*2))
        else:
            start_point_lon = int(round(360+start_point['longitude']*2))-4
            end_point_lon = int(round(360+end_point['longitude']*2))

        # filling array with needed points. 40x40 - max array of points, that must be displayed on map.
        selected_points_list = []
        temp_lat = start_point_lat
        for i in range(40):
            if temp_lat > end_point_lat:
                break
            temp_lon = start_point_lon
            continue_state = True
            if start_point['longitude'] > end_point['longitude']:
                continue_state = False
            for j in range(40):
                if temp_lon > 719 and continue_state is False:
                    temp_lon = 0+(temp_lon-719)
                    continue_state = True
                    continue
                if temp_lon > end_point_lon and continue_state is True:
                    break
                selected_points_list.append([temp_lat, temp_lon])
                temp_lon += lat_step
            temp_lat += lon_step

        # making list of wind barbs data, for future displaying it on map via google api.
        data = []
        for point in selected_points_list:
            latitude_iterator = point[0]
            longitude_iterator = point[1]
            if 0 > latitude_iterator or latitude_iterator > 360 or 0 > longitude_iterator or longitude_iterator > 719:
                continue

            u_data = float(wind_data['u_data'][latitude_iterator][longitude_iterator])
            v_data = float(wind_data['v_data'][latitude_iterator][longitude_iterator])
            result = round(math.sqrt(math.pow(u_data, 2) + math.pow(v_data, 2)), 5)
            knots = round(float(result)/0.514)
            path = wind_barb_svg_generator(knots)

            # finding direction(rotation) of wind barb in second and fourth quarter of trigonometry
            if ((u_data <= 0) and (v_data > 0)) or ((u_data >= 0) and (v_data < 0)):
                sin_data = float(abs(u_data)) / abs(result) * (180.0/math.pi)
                direction = 360-sin_data if (u_data < 0) and (v_data > 0) else 180-sin_data
            # and in first and third quarter of trigonometry
            else:
                sin_data = float(abs(v_data)) / abs(result) * (180.0/math.pi)
                direction = 270-sin_data if (u_data < 0) and (v_data < 0) else 90-sin_data

            # assigning coordinates for our obtained points
            if longitude_iterator < 360:
                longitude = float(longitude_iterator)/2 - 180
            else:
                longitude = float(longitude_iterator)/2 - 180

            if latitude_iterator <= 180:
                latitude = 90-float(latitude_iterator)/2
            else:
                latitude = -1*(float(latitude_iterator)/2-90)

            data.append({
                'latitude': latitude,
                'longitude': longitude,
                'knots': knots,
                'path': path,
                'direction': direction,
            })

        return HttpResponse(json.dumps({'response': 'OK', 'data': data, 'post_count': post_count},
                                       indent=4, separators=(',', ': '),
                                       encoding='utf-8'), content_type="application/json")

    return render_to_response('wind_map.html')