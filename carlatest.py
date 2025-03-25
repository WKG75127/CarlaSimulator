import carla
import random
min_distance = 5
def radar_react(data,vehicle)
    for detection in data
        distance = detection.depth
        if(distance<min_distance)
            control.throttle = min(1.0, control.throttle + 0.2)
        else
            control.throttle = max(0.0,control.throttle- 0.2)

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
client.load_world('Town05')
# Get the map's spawn points
spawn_points = world.get_map().get_spawn_points()
ego_bp = world.get_blueprint_library().find('vehicle.lincoln.mkz_2020')
ego_bp.set_attribute('role_name', 'hero')
ego_vehicle = world.spawn_actor(ego_bp, random.choice(spawn_points)
#attach radar to ego vehicle
radar_bp = world.get_blueprint_library().find('sensor.other.radar')
radar_bp.set_attribute('horizontal_fov', '30.0')
radar_bp.set_attribute('vertical_fov', '5.0')
radar_bp.set_attribute('range', '10.0')
transform = carla.Transform(carla.Location(x=-2.5, z=1.0))
radar = world.spawn_actor(radar_bp, transform, attach_to=ego_vehicle)
#react to radar data
radar.listen(lambda data: radar_react(data, ego_vehicle))
#create traffic manager
tm = client.get_trafficmanager()
tm.vehicle_percentage_speed_difference(ego_vehicle, 100) 
tm.distance_to_leading_vehicle(ego_vehicle, 5)
measurements, sensor_data = carla_client.read_data()
control = measurements.player_measurements.autopilot_control
# modify here control if wanted.
carla_client.send_control(control)
