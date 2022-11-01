import math, random

# The Particle class has all of the necessary functions for moving and interacting the particles
class Particle():
    def __init__(self, typeID, dimensions, cellArrays, cellSizes): # The first array of cells must be the collision array
        # Different particles can use different physics and colours determined by the id
        self.id = typeID

        # Initializing the particle's position and velocity
        self.pos = [random.randint(0, dimensions[i]) for i in range(3)]
        self.vel = [0.0, 0.0, 0.0]

        self.cells = []

        for i in range(len(cellArrays)):
            # Finding the cell it should be in
            self.cells.append([int(self.pos[j] / cellSizes[i]) for j in range(3)])

            # Putting itself in the correct cell
            try: cellArrays[i][self.cells[i][0]][self.cells[i][1]][self.cells[i][2]].append(self)
            except: print(self.pos, self.cells, cellSizes, len(cellArrays[i]), len(cellArrays[i][0]), len(cellArrays[i][0][0]))

    def checkCollisions(self, cells, size, density):
        # The number of particles in each cell's "neighborhood" influences collision speeds
        numParts = 1

        # Checking each of the nine closest cells for other particles
        for x in range(-1, 2):
            if self.cells[0][0] + x < 0 or self.cells[0][0] + x >= len(cells): continue

            for y in range(-1, 2):
                if self.cells[0][1] + y < 0 or self.cells[0][1] + y >= len(cells[x]): continue

                for z in range(-1, 2):
                    if self.cells[0][2] + z < 0 or self.cells[0][2] + z >= len(cells[x][y]) or \
                       len(cells[self.cells[0][0] + x][self.cells[0][1] + y][self.cells[0][2] + z]) == 0: continue

                    for particle in cells[self.cells[0][0] + x][self.cells[0][1] + y][self.cells[0][2] + z]:
                        # Eliminate zero-division errors and collisions with self
                        if self.pos[0] == particle.pos[0] and \
                           self.pos[1] == particle.pos[1] and \
                           self.pos[2] == particle.pos[2]: continue

                        # Getting the relative distance and velocity vectors
                        distVect = [self.pos[i] - particle.pos[i] for i in range(3)]
                        velVect  = [self.vel[i] - particle.vel[i] for i in range(3)]

                        dist = math.sqrt(distVect[0]**2 + distVect[1]**2 + distVect[2]**2)

                        # Don't bounce them if it's not actually a collision
                        if dist > size * 2: continue

                        # Incrementing the density for each seen particle to accelerate them faster
                        if numParts < 2: numParts += 0.1

                        # Normalizing the length vector and modifying with numParts
                        length = density * numParts / dist
                        for i in range(3):
                            distVect[i] *= length

                        # The dot product of positions and velocities
                        dot = velVect[0]*distVect[0] + velVect[1]*distVect[1] + velVect[2]*distVect[2]

                        for i in range(3):
                            # Moving and accelerating the particles away from each other
                            self.pos[i]     += size * distVect[i]
                            particle.pos[i] -= size * distVect[i]

                            self.vel[i]     -= dot  * distVect[i]
                            particle.vel[i] += dot  * distVect[i]

    def move(self, dimensions, cellArrays, cellSizes, gravity, density):
        # Removing it from its current cell
        for i in range(len(cellArrays)):
            cellArrays[i][self.cells[i][0]][self.cells[i][1]][self.cells[i][2]].remove(self)

        # A vector to the gravity point
        gravVect = [self.pos[i] - gravity[0][i].val for i in range(3)]

        # The inverse length of the gravity vector
        gravLen = math.sqrt(gravVect[0]**2 + gravVect[1]**2 + gravVect[2]**2)
        if gravLen: gravLen = gravity[1].val / gravLen

        for i in range(3):
            # Applying gravity and roughly capping the speed
            self.vel[i] = max(-100, min(100, self.vel[i] - gravVect[i] * gravLen))

            # Moving the particle and bouncing it off walls
            self.pos[i] += self.vel[i]

            if self.pos[i] < 0 or self.pos[i] > dimensions[i]:
                self.pos[i] = max(0, min(dimensions[i], self.pos[i]))
                self.vel[i] *= -density

        for i in range(len(cellArrays)):
            self.cells[i] = [int(self.pos[j] / cellSizes[i]) for j in range(3)]

            cellArrays[i][self.cells[i][0]][self.cells[i][1]][self.cells[i][2]].append(self)
