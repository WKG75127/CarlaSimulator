
class Vehicle:
    def __init__(self, vehicle_id, model):
        self.vehicle_id = vehicle_id
        self.model = model
        self.sensors = {}

    def add_sensor(self, sensor):
        self.sensors[sensor.sensor_id] = sensor

    def get_sensor(self, sensor_id):
        return self.sensors.get(sensor_id, None)

    def get_sensor_data(self):
        sensor_data = {}
        for sensor in self.sensors.values():
            sensor_data[sensor.sensor_id] = sensor.sensor_data
        return sensor_data
