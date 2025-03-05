import carla
import cv2
import numpy as np
import logging
import random
import queue

# Set up logging
logging.basicConfig(level=logging.INFO)

# Queue for V2V communication
communication_queue = queue.Queue()

# Initialize sensor data storage
sensor_data = [{'camera': None, 'radar': 'Radar: N/A', 'lidar': 'LiDAR: N/A'} for _ in range(3)]

# Initialize V2V communication data
v2v_data = [{'radar': 'Radar: N/A', 'lidar': 'LiDAR: N/A'} for _ in range(3)]


def main():
    # Connect to the simulator
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    
    # Load Town10HD map
    world = client.load_world('Town10HD')
    logging.info("Loaded Town10HD map.")

    # Get the blueprint library and set up the vehicle
    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
    
    # Get all available road spawn points
    all_spawn_points = world.get_map().get_spawn_points()

    vehicles = []
    cameras = []
    radars = []
    lidars = []

    # Use Traffic Manager to keep vehicles in the same lane
    traffic_manager = client.get_trafficmanager()
    traffic_manager.set_global_distance_to_leading_vehicle(5.0)
    traffic_manager.set_synchronous_mode(False)
    traffic_manager.set_hybrid_physics_mode(True)
    traffic_manager.set_hybrid_physics_radius(100.0)

    # Filter for valid straight road spawn points avoiding intersections
    straight_road_points = [sp for sp in all_spawn_points if abs(sp.rotation.yaw) < 5.0 and sp.location.z < 2.0]
    base_spawn_point = random.choice(straight_road_points)
    lane_width = 3.5  # Typical lane width in meters

    parallel_spawn_points = [
        carla.Transform(
            carla.Location(x=base_spawn_point.location.x, 
                           y=base_spawn_point.location.y - lane_width, 
                           z=base_spawn_point.location.z),
            base_spawn_point.rotation
        ),
        carla.Transform(
            carla.Location(x=base_spawn_point.location.x, 
                           y=base_spawn_point.location.y, 
                           z=base_spawn_point.location.z),
            base_spawn_point.rotation
        ),
        carla.Transform(
            carla.Location(x=base_spawn_point.location.x, 
                           y=base_spawn_point.location.y + lane_width, 
                           z=base_spawn_point.location.z),
            base_spawn_point.rotation
        )
    ]

    for i, spawn_point in enumerate(parallel_spawn_points):
        try:
            vehicle = world.spawn_actor(vehicle_bp, spawn_point)
            vehicles.append(vehicle)
            logging.info(f'Spawned vehicle {i+1} at {spawn_point.location}')
        except RuntimeError as e:
            logging.warning(f"Spawn failed at {spawn_point.location}. Skipping vehicle {i+1}.")

    # Enable autopilot for all vehicles
    for vehicle in vehicles:
        vehicle.set_autopilot(True, traffic_manager.get_port())

    # Add sensors to each vehicle
    for i, vehicle in enumerate(vehicles):
        # Add camera
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '400')
        camera_bp.set_attribute('image_size_y', '300')
        camera_bp.set_attribute('fov', '70')
        camera_bp.set_attribute('sensor_tick', '0.05')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        cameras.append(camera)

        # Add radar sensor
        radar_bp = blueprint_library.find('sensor.other.radar')
        radar_bp.set_attribute('horizontal_fov', '30')
        radar_bp.set_attribute('vertical_fov', '20')
        radar_bp.set_attribute('range', '50')
        radar_transform = carla.Transform(carla.Location(x=2.5, z=1.0))
        radar = world.spawn_actor(radar_bp, radar_transform, attach_to=vehicle)
        radars.append(radar)

        # Add LiDAR sensor
        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('range', '50')
        lidar_bp.set_attribute('rotation_frequency', '20')
        lidar_bp.set_attribute('channels', '32')
        lidar_transform = carla.Transform(carla.Location(x=0, z=2.5))
        lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)
        lidars.append(lidar)

        # Sensor callbacks with proper index binding
        camera.listen(lambda image, idx=i: communication_queue.put((idx, 'camera', image)))
        radar.listen(lambda radar_data, idx=i: communication_queue.put((idx, 'radar', radar_data)))
        lidar.listen(lambda lidar_data, idx=i: communication_queue.put((idx, 'lidar', lidar_data)))

    try:
        while True:
            if not communication_queue.empty():
                index, sensor_type, data = communication_queue.get()
                if sensor_type == 'camera':
                    image_data = np.frombuffer(data.raw_data, dtype=np.uint8)
                    image_data = image_data.reshape((data.height, data.width, 4))
                    image_bgr = image_data[:, :, :3].copy()
                    cv2.putText(image_bgr, f'Vehicle {index + 1}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(image_bgr, f"{sensor_data[index]['radar']} | {sensor_data[index]['lidar']}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(image_bgr, f"V2V: {v2v_data[index]['radar']} | {v2v_data[index]['lidar']}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    sensor_data[index]['camera'] = image_bgr
                elif sensor_type == 'radar':
                    sensor_data[index]['radar'] = f'Radar: {len(data)} detections'
                    v2v_data[index]['radar'] = f'V2V Radar: {len(data)} detections'
                elif sensor_type == 'lidar':
                    sensor_data[index]['lidar'] = f'LiDAR: {len(data)} points'
                    v2v_data[index]['lidar'] = f'V2V LiDAR: {len(data)} points'

            if all(sd['camera'] is not None for sd in sensor_data):
                combined_feed = np.hstack([sd['camera'] for sd in sensor_data])
                cv2.imshow('Carla Multi-Camera Feed with V2V Data', combined_feed)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except KeyboardInterrupt:
        logging.info("Simulation interrupted. Cleaning up...")
    finally:
        for actor in vehicles + cameras + radars + lidars:
            actor.destroy()
        logging.info('Destroyed all actors')

if __name__ == '__main__':
    main()
