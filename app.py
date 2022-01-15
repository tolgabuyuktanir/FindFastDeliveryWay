
import json
from flask import Flask, request
import create_routes
# create the Flask app
app = Flask(__name__)


@app.route('/create-routes-service', methods=['POST'])
def create_routes_service():
    input_json = request.get_json()
    vehicles = input_json['vehicles']
    jobs = input_json['jobs']
    distance_in_seconds = input_json['matrix']

    # create desired json template
    routes_json_template = create_routes.create_routes_json_template(vehicles)
    # distribute jobs to vehicles and create routes
    routes_json = create_routes.distribute_jobs(vehicles, jobs, distance_in_seconds, routes_json_template)
    return json.dumps(routes_json)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
