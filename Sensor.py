
class sensor:
        
        #def main():
        
def __init__(self, sensor_id, sensor_type, sensor_data=None):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.sensor_data = sensor_data if sensor_data else {}

    def update_data(self, new_data):
        self.sensor_data.update(new_data)

       # main()
