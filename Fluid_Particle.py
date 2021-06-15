import math, random

# The Particle class has all of the necessary functions for moving and interacting the particles
class Particle():
    def __init__(self, size, dimensions, cells):
        self.size = size

        # Giving the particle a random position and finding the cell it should be in
        self.pos = [random.randint(0, dimensions[i]) for i in range(3)]
        self.cell = [int(self.pos[i] / self.size) for i in range(3)]

        self.vel = [0.0, 0.0, 0.0]

        # Putting itself in the correct cell
        cells[self.cell[0]][self.cell[1]][self.cell[2]].append(self)

    def checkCollisions(self, cells, viscosity):
        # The number of particles in each cell's "neighborhood" influences collision speeds
        density = 1

        # Checking each of the nine closest cells for other particles
        for x in range(-1, 2):
            if self.cell[0] + x < 0 or self.cell[0] + x >= len(cells): continue

            for y in range(-1, 2):
                if self.cell[1] + y < 0 or self.cell[1] + y >= len(cells[x]): continue

                for z in range(-1, 2):
                    if self.cell[2] + z < 0 or self.cell[2] + z >= len(cells[x][y]) or \
                       len(cells[self.cell[0] + x][self.cell[1] + y][self.cell[2] + z]) == 0: continue

                    for particle in cells[self.cell[0] + x][self.cell[1] + y][self.cell[2] + z]:
                        # Eliminate zero-division errors and collisions with self
                        if self.pos[0] == particle.pos[0] and \
                           self.pos[1] == particle.pos[1] and \
                           self.pos[2] == particle.pos[2]: continue

                        # Getting the relative distance and velocity vectors
                        distVect = [self.pos[i] - particle.pos[i] for i in range(3)]
                        velVect  = [self.vel[i] - particle.vel[i] for i in range(3)]

                        dist = math.sqrt(distVect[0]**2 + distVect[1]**2 + distVect[2]**2)

                        # Don't bounce them if it's not actually a collision
                        if dist > self.size * 2: continue

                        # Incrementing the density for each seen particle to accelerate them faster
                        if density < 2: density += 0.1

                        # Normalizing the length vector and modifying with density
                        length = viscosity * density / dist
                        for i in range(3):
                            distVect[i] *= length

                        # The dot product of positions and velocities
                        dot = velVect[0]*distVect[0] + velVect[1]*distVect[1] + velVect[2]*distVect[2]

                        # The amount of overlap
                        #jump = self.size * 2 - dist

                        for i in range(3):
                            # Moving and accelerating the particles away from each other
                            self.pos[i]     += self.size * distVect[i]
                            particle.pos[i] -= self.size * distVect[i]

                            self.vel[i]     -= dot  * distVect[i]
                            particle.vel[i] += dot  * distVect[i]

    def move(self, dimensions, cells, gravity, viscosity):
        self.vel[1] -= gravity

        # Removing it from its current cell
        cells[self.cell[0]][self.cell[1]][self.cell[2]].remove(self)

        for i in range(3):
            self.vel[i] = max(-100, min(100, self.vel[i]))

            # Moving the particle and bouncing it off walls
            self.pos[i] += self.vel[i]

            if self.pos[i] < 0 or self.pos[i] > dimensions[i]:
                self.pos[i] = max(0, min(dimensions[i], self.pos[i]))
                self.vel[i] *= -viscosity

            # Putting it in the right cell
            self.cell[i] = int(self.pos[i] / self.size)

        cells[self.cell[0]][self.cell[1]][self.cell[2]].append(self)
