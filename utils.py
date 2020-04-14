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

        self.planet_ids = []
        if 'planet' in system:
            if '__dupkeys__' in system:
                for key in system['__dupkeys__']['planet']:
                    self.planet_ids.append(system[key])
            else:
                self.planet_ids.append(system['planet'])
        
        self.planets = []

        self.system = system

    def addPlanet(self, planet):
        self.planets.append(planet)

    def toString(self):
        ret = ''
        
        ret += 'SYSTEM [ ' + self.name + ' ]\n'
        ret += 'coords: (' + str(self.pos[0]) + ', ' + str(self.pos[1]) + ')\n'
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

    def addDeposit(self, deposit):
        self.deposits.append(deposit)

    def toString(self):
        ret = ''

        ret += 'PLANET [ ' + self.name + ' ]\n'
        ret += 'type: ' + self.type + '\n'
        ret += 'deposits: {\n'
        for deposit in self.deposits:
            d_str = "\t" + deposit.toString().replace("\n", "\n\t")
            ret += d_str + '\n' 
        ret += '}'
        return ret


# Stores information associated with a deposit
class Deposit:
    def __init__(self, deposit):
        self.type = deposit['type']
        
        self.swap_type = None
        if 'swap_type' in deposit:
            self.swap_type = deposit['swap_type']

    def toString(self):
        ret = ''

        ret += self.type
        if self.swap_type != None:
            ret += "\n" + self.swap_type
        return ret
