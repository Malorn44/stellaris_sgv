import sys

# File for storing custom classes

# update to update which resources are gathered
resources = ['minerals', 'energy', 'physics', 'society', 'engineering']

# Stores information associated with a galaxy
class Galaxy:
    def __init__(self, systems, resources=resources):
        self.systems = systems

        self.resources = resources

        # max amounts per system
        self.max_resources = [0] * len(self.resources)

        # min amounts per system
        self.min_resources = [sys.maxsize] * len(self.resources)

        # average amounts per system
        self.avg_resources = [0] * len(self.resources)

        for s in self.systems:
            for i in range(len(self.resources)):
                self.avg_resources[i] += s.resources[i]
                self.max_resources[i] = max(self.max_resources[i], s.resources[i])
                self.min_resources[i] = min(self.min_resources[i], s.resources[i])
        
        for i in range(len(self.resources)):
            self.avg_resources[i] /= len(self.systems)

    def print_stats(self):
        print('There are', len(self.systems), 'in the galaxy')
        for i in range(len(self.resources)):
            print('avg_' + self.resources[i] + ":", self.avg_resources[i])
        for i in range(len(self.resources)):
            print('max_' + self.resources[i] + ":", self.max_resources[i])
        for i in range(len(self.resources)):
            print('min_' + self.resources[i] + ":", self.min_resources[i])

# Stores information associated with a solar system
class System:
    def __init__(self, system):
        self.name = system['name'][1:-1] # remove surrounding " "
        self.type = system['type'] # probably only 'star' type
        self.pos = (-1*system['coordinate']['x'], system['coordinate']['y'])

        self.hyperlanes = []
        if 'hyperlane' in system:
            for connection in system['hyperlane']:
                self.hyperlanes.append(connection['to'])

        self.planet_ids = []
        if 'planet' in system:
            if '__dupkeys__' in system:
                for key in system['__dupkeys__']['planet']:
                    self.planet_ids.append(system[key])
            else:
                self.planet_ids.append(system['planet'])
        
        self.planets = []

        self.resources = [0] * len(resources)

    def addPlanet(self, planet):
        self.planets.append(planet)

        for i in range(len(resources)):
            self.resources[i] += planet.resources[i]

    def toString(self):
        ret = ''
        
        ret += 'SYSTEM [ ' + self.name + ' ]\n'
        ret += 'coords: (' + str(self.pos[0]) + ', ' + str(self.pos[1]) + ')\n'
        for i in range(len(resources)):
            ret += resources[i] + ':', self.resources[i] + '\n'
        ret += 'hyperlanes: { '
        for lane in self.hyperlanes:
            ret += str(lane) + ' '
        ret += '}\n'  
        ret += 'planets: {\n'
        for planet in self.planets:
            p_str = "\t" + planet.toString().replace("\n", "\n\t")
            ret += p_str + '\n'
        ret += '}'
        return ret


# Stores information associated with a planet
class Planet:
    def __init__(self, planet):
        self.name = planet['name'][1:-1]
        self.type = planet['planet_class'][1:-1]

        self.deposit_ids = []
        if 'deposits' in planet:
            for ID in planet['deposits']:
                self.deposit_ids.append(ID)

        self.deposits = []

        self.resources = [0] * len(resources)

    def addDeposit(self, deposit):
        self.deposits.append(deposit)

        # Add any resources to list of resources
        end_str = deposit.type.split('_')[-1]
        for i in range(len(resources)):
            if resources[i] in deposit.type:
                self.resources[i] += int(end_str)

    def toString(self):
        ret = ''

        ret += 'PLANET [ ' + self.name + ' ]\n'
        ret += 'type: ' + self.type + '\n'
        for i in range(len(resources)):
            ret += resources[i] + ':', self.resources[i] + '\n'
        ret += 'deposits: {\n'
        for deposit in self.deposits:
            d_str = "\t" + deposit.toString().replace("\n", "\n\t")
            ret += d_str + '\n' 
        ret += '}'      
        return ret


# Stores information associated with a deposit
class Deposit:
    def __init__(self, deposit):
        self.type = deposit['type'][1:-1]
        
        self.swap_type = None
        if 'swap_type' in deposit:
            self.swap_type = deposit['swap_type'][1:-1]

    def toString(self):
        ret = ''

        ret += self.type
        if self.swap_type != None:
            ret += "\n" + self.swap_type
        return ret
