import carla
import random
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
client.load_world('Town05')
