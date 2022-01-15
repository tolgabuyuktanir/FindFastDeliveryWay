import json
import numpy as np


def get_input(filename):
    """
    This method gets input file path and returns vehicles object, jobs objects and  distance in seconds between
    locations of its.

    Parameters
    ----------
    filename: string
    The input file path to be read.

    Returns
    ----------
    vehicles: object
    jobs: object
    distance_in_seconds: object
    This object is a 2D-Array and includes distance in seconds between locations of vehicles and costumers.
    """

    with open(filename, 'r') as f:
        input_json = json.load(f)
        vehicles = input_json['vehicles']
        jobs = input_json['jobs']
        distance_in_seconds = input_json['matrix']
    return vehicles, jobs, distance_in_seconds


def create_routes_json_template(vehicles):
    """
    This function creates a json template to project routes.
    Parameters
    ----------
    vehicles: object
    This object includes vehicles information read from input json file.

    Returns
    ----------
    routes_json_template:object
    The template of desired output format.
    """

    # prepare json template
    routes_json_template = {
        "total_delivery_duration": 0,
        "routes": {
        }
    }
    for vehicle in vehicles:
        routes_json_template['routes'].update({str(vehicle['id']): {'jobs': [], 'delivery_duration': 0}})
    return routes_json_template


def distribute_jobs(vehicles, jobs, distance_in_seconds, routes):
    """
    This function calculates route and jobs of vehicles.

    Algorithm:
    1- Calculate total delivery and capacity of vehicles, and plan according to smaller.
    2- Get vehicles locations.
    3- Iterate jobs.
    4- Find the closest vehicle, which has enough capacity, to the delivery location.
    4- Assign delivery to the closest vehicle.
    5- Update the vehicle location with delivery location.
    6- Update routes_json.
    7- Go to 3.

    Parameters
    ----------
    vehicles: object
    The information of vehicles obtained from input json file.

    jobs: object
    The information of jobs obtained from input json file.

    distance_in_seconds: object
    This object is a 2D-Array and includes distance in seconds between locations of vehicles and costumers.

    routes: object
    The template of desired output format.

    Returns
    ----------
    routes: object
    The template of desired output format.
    """
    # calculate carboy capacity of available vehicles
    total_capacity = 0
    [total_capacity := total_capacity + i['capacity'][0] for i in vehicles]

    # calculate total carboy delivery
    total_delivery = 0
    [total_delivery := total_delivery + i['delivery'][0] for i in jobs]

    # distance in seconds
    distance_in_seconds = np.array(distance_in_seconds)

    # compare capacity and delivery and distribute according to smaller
    for distribution in range(len(jobs) if total_delivery < total_capacity else total_capacity):
        min_distance_in_seconds = np.iinfo(np.int32).max
        index_of_minimum = -1
        delivery_vehicle = -1
        # find minimum distance in order to add to vehicle
        for v in range(len(vehicles)):
            if min(distance_in_seconds[vehicles[v]['start_index']][len(vehicles[v]):]) < min_distance_in_seconds \
                    and vehicles[v]['capacity'] >= jobs[distribution]['delivery']:
                min_distance_in_seconds = min(distance_in_seconds[vehicles[v]['start_index']][len(vehicles[v]):])
                index_of_minimum = len(vehicles) + \
                                   list(distance_in_seconds[vehicles[v]['start_index']][len(vehicles[v]):]).index(
                                       min_distance_in_seconds)
                delivery_vehicle = v
        # find the closest vehicle, which has enough capacity, to the delivery location.
        vehicles[delivery_vehicle]['capacity'] = [
            vehicles[delivery_vehicle]['capacity'][0] - jobs[distribution]['delivery'][0]]
        vehicles[delivery_vehicle]['start_index'] = index_of_minimum

        # replace distance of handled delivery with maximum integer
        distance_in_seconds[:, index_of_minimum] = np.iinfo(np.int32).max

        # assign calculated routes to json file.
        routes['total_delivery_duration'] = routes['total_delivery_duration'] + int(min_distance_in_seconds)
        routes['routes'][str(delivery_vehicle + 1)]['jobs'].append(index_of_minimum)
        routes['routes'][str(delivery_vehicle + 1)]['delivery_duration'] = \
            routes['routes'][str(delivery_vehicle + 1)]['delivery_duration'] + int(min_distance_in_seconds)
    return routes


def main():
    vehicles, jobs, distance_in_seconds = get_input('data/input.json')
    routes_json_template = create_routes_json_template(vehicles)
    routes_json = distribute_jobs(vehicles, jobs, distance_in_seconds, routes_json_template)
    print(json.dumps(routes_json))


if __name__ == '__main__':
    main()
