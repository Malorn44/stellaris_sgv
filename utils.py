# File for storing custom classes

# Stores information associated with a solar system
class System:
    def __init__(self, system):
        self.name = system['name'][1:-1] # remove surrounding " "
        self.pos = (system['coordinate']['x'], system['coordinate']['y'])

        self.hyperlanes = []
        if 'hyperlane' in system:
            for connection in system['hyperlane']:
                self.hyperlanes.append(connection['to'])

        self.planets = []
        

        self.system = system



    def print(self):
        print(self.system)