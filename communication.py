import carla
import cv2
import numpy as np
import logging
import random
import queue
import sqlite3
import os
import ctypes
import pygame
from pygame.locals import *

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
r = 0
m = ""
ti = "title"
cX = 0
cY = 0
cZ = 0
min_distance = 5
pygame.font.init()
display_surface = pygame.display.set_mode((250, 300), pygame.NOFRAME)
hwnd = pygame.display.get_wm_info()['window']

def radar_react(data,vehicle):
    for detection in data:
        distance = detection.depth
        if(distance<min_distance):
            control.throttle = min(1.0, control.throttle + 0.2)
	else:
            control.throttle = max(0.0,control.throttle- 0.2)
# Set up logging
logging.basicConfig(level=logging.INFO)

# Queue for V2V communication
communication_queue = queue.Queue()

# Initialize sensor data storage
sensor_data = [{'camera': None, 'radar': 'Radar: N/A', 'lidar': 'LiDAR: N/A'} for _ in range(3)]

# Initialize V2V communication data
v2v_data = [{'radar': 'Radar: N/A', 'lidar': 'LiDAR: N/A'} for _ in range(3)]

# SQLite Database Setup
conn = sqlite3.connect('carla_data.db')
cursor = conn.cursor()
# Create tables for vehicles and sensors
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT UNIQUE,
        vehicle_type TEXT,
        location_x REAL,
        location_y REAL,
        location_z REAL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id TEXT UNIQUE,
        sensor_type TEXT,
        vehicle_id TEXT,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
    )
''')
conn.commit()
def add_vehicle_to_db(vehicle):
    """Store vehicle details in the database."""
    cursor.execute('''
        INSERT INTO vehicles (vehicle_id, vehicle_type, location_x, location_y, location_z)
        VALUES (?, ?, ?, ?, ?)
    ''', (vehicle.id, vehicle.type_id, vehicle.get_location().x, vehicle.get_location().y,
vehicle.get_location().z))
    conn.commit()
def add_sensor_to_db(sensor, sensor_type, vehicle):
    """Store sensor details in the database, linked to a vehicle."""
    cursor.execute('''
        INSERT INTO sensors (sensor_id, sensor_type, vehicle_id)
        VALUES (?, ?, ?)
    ''', (sensor.id, sensor_type, vehicle.id))
    conn.commit()


def createDisplay():

	# creates font variables with font file and size
	font1 = pygame.font.SysFont('chalkduster.ttf', 40)
	font2 = pygame.font.SysFont('freesanbold.ttf', 30)
 
	# renders the text displays
	title = font1.render(f'{ti}', True, (0, 255, 0))
	rmp = font2.render(f'RMP: {r}', True, (0, 255, 0))
	model = font2.render(f'Car Model: {m}', True, (0, 255, 0))
	location = font2.render(f'Location: {cX}, {cY}, {cZ}', True, (0, 255, 0))
 
	# creates text surface objects
	tRect = title.get_rect()
	mRect = model.get_rect()
	rRect = rmp.get_rect()
	lRect = location.get_rect()

 
	# setting the tilte center
	tRect.center = (125, 15)
 
	# setting the model midleft
	mRect.midleft = (5, 75)

	# setting the speed midleft
	rRect.midleft = (5, 125)
 
	# setting the throttle midleft
	lRect.midleft = (5, 175)

	display_surface.set_alpha(0)   

	display_surface.blit(title, tRect)
	display_surface.blit(model, mRect)
	display_surface.blit(location, lRect)
	display_surface.blit(rmp, rRect) 

def keep_top_window(hwnd):
	ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0003)

def get_Ana(vehicle):
	ti = vehicle.id
	m = vehicle.type_id 
	cX = vehicle.get_location().x
	cY= vehicle.get_location().y
	cZ = vehicle.get_location().z
	spLim = vehicle.get_speed_limit()
	velocity = vehicle.get_velocity()
	r = math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)
    pygame.display.flip()
    
    


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
    traffic_manager.set_global_percentage_speed_difference
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
        get_Ana(vehicle)
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
        add_sensor_to_db(camera, 'camera', vehicle)

        # Add radar sensor
        radar_bp = blueprint_library.find('sensor.other.radar')
        radar_bp.set_attribute('horizontal_fov', '30')
        radar_bp.set_attribute('vertical_fov', '20')
        radar_bp.set_attribute('range', '50')
        radar_transform = carla.Transform(carla.Location(x=2.5, z=1.0))
        radar = world.spawn_actor(radar_bp, radar_transform, attach_to=vehicle)
        radars.append(radar)
        add_sensor_to_db(radar, 'radar', vehicle)

        # Add LiDAR sensor
        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('range', '50')
        lidar_bp.set_attribute('rotation_frequency', '20')
        lidar_bp.set_attribute('channels', '32')
        lidar_transform = carla.Transform(carla.Location(x=0, z=2.5))
        lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)
        lidars.append(lidar)
        add_sensor_to_db(lidar, 'lidar', vehicle)

        # Sensor callbacks with proper index binding
        camera.listen(lambda image, idx=i: communication_queue.put((idx, 'camera', image)))
        radar.listen(lambda radar_data, idx=i: communication_queue.put((idx, 'radar', radar_data)))
        lidar.listen(lambda lidar_data, idx=i: communication_queue.put((idx, 'lidar', lidar_data)))

    try:
        while True:

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            keep_top_window(hwnd)
            
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
            for detections:
                cursor.execute(
                    "SELECT vehicle_id FROM sensors where sensor_id = %s;", (radar_id,)))
                )
                vehicle = cursor.fetchone()
                radar.listen(lambda data: radar_react(data, vehicle))
    except KeyboardInterrupt:
        logging.info("Simulation interrupted. Cleaning up...")
    finally:
        for actor in vehicles + cameras + radars + lidars:
            actor.destroy()
        logging.info('Destroyed all actors')

if __name__ == '__main__':
    
    main()
    createDisplay()
    
