import carla
import random
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
client.load_world('Town05')
# Get the map's spawn points
spawn_points = world.get_map().get_spawn_points()
ego_bp = world.get_blueprint_library().find('vehicle.lincoln.mkz_2020')
ego_bp.set_attribute('role_name', 'hero')
ego_vehicle = world.spawn_actor(ego_bp, random.choice(spawn_points)
tm = client.get_trafficmanager()
tm.vehicle_percentage_speed_difference(ego_vehicle, 100) 
tm.distance_to_leading_vehicle(ego_vehicle, 5)
measurements, sensor_data = carla_client.read_data()
control = measurements.player_measurements.autopilot_control
# modify here control if wanted.
carla_client.send_control(control)
