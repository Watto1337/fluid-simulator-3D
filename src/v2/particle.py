import math, random

class Particle():
    density = 200
    compressability = 15
    restitution = 0.5
    wallForce = 1
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0
    
    def move(self, bounds, acceleration):
        self.x += self.vx
        self.y += self.vy

        self.vx += acceleration[0]
        self.vy += acceleration[1]

        if (self.x >= bounds[0]):
            self.x = bounds[0] - 1
            self.vx *= -Particle.restitution
        
        if (self.x < 0):
            self.x = 0
            self.vx *= -Particle.restitution

        if (self.y >= bounds[1]):
            self.y = bounds[1] - 1
            self.vy *= -Particle.restitution
        
        if (self.y < 0):
            self.y = 0
            self.vy *= -Particle.restitution
    
    def applyForce(self, other, dt):
        force = self.evaluateForce(other)

        self.vx -= force[0] * dt
        self.vy -= force[1] * dt

        other.vx += force[0] * dt
        other.vy += force[1] * dt
    
    def applyWallForce(self, bounds, dt):
        if (self.x < Particle.density):
            self.applyForce(Particle(-1, self.y + self.vy), dt * Particle.wallForce)

        if (self.y < Particle.density):
            self.applyForce(Particle(self.x + self.vx, -1), dt * Particle.wallForce)

        if (bounds[0] - 1 - self.x < Particle.density):
            self.applyForce(Particle(bounds[0], self.y + self.vy), dt * Particle.wallForce)

        if (bounds[1] - 1 - self.y < Particle.density):
            self.applyForce(Particle(self.x + self.vx, bounds[1]), dt * Particle.wallForce)

    def evaluateForce(self, other):
        self.x += self.vx
        self.y += self.vy
        other.x += other.vx
        other.y += other.vy

        dist = self.distance(other)

        if (dist > Particle.density * Particle.compressability):
            return (0, 0)

        dx = (other.x - self.x)
        dy = (other.y - self.y)

        if (dist == 0):
            angle = random.random() * 2 * math.pi
            dx = math.sin(angle)
            dx = math.cos(angle)
        else:
            dx /= dist
            dy /= dist

        force \
            = (Particle.density - dist) ** 2 \
            * (Particle.density * Particle.compressability - dist) ** 2 \
            / Particle.density ** 4

        if (dist > Particle.density):
            force *= -1

        self.x -= self.vx
        self.y -= self.vy
        other.x -= other.vx
        other.y -= other.vy

        return (dx * force * Particle.restitution, dy * force * Particle.restitution)

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
