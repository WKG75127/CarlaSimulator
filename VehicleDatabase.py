class VehicleDatabase:
    
    def __init__(self):
        self.vehicles = {}

    def add_vehicle(self, vehicle):
        self.vehicles[vehicle.vehicle_id] = vehicle

    def get_vehicle(self, vehicle_id):
        return self.vehicles.get(vehicle_id, None)

    def add_sensor_to_vehicle(self, vehicle_id, sensor):
        vehicle = self.get_vehicle(vehicle_id)
        if vehicle:
            vehicle.add_sensor(sensor)
        else:
            print(f"Vehicle {vehicle_id} not found!")

    def get_vehicle_sensors(self, vehicle_id):
        vehicle = self.get_vehicle(vehicle_id)
        if vehicle:
            return vehicle.get_sensor_data()
        else:
            return None
