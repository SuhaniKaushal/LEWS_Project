class Sensorinformation:
  def __init__(self,sensor_name,sensor_value,sensor_type,parent_value):
    self.sensor_name=sensor_name
    self.sensor_value=sensor_value
    self.sensor_type=sensor_type
    self.parent_value=parent_value
    
    
  def printvalue(self):
    print(self.sensor_name,' ',self.sensor_value,' ',self.sensor_type,' ',self.parent_value)
    