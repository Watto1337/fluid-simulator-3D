import math, random

class Particle():
    density = 100
    compressability = 10
    restitution = 0.9
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.dx = 0
        self.dy = 0

        self.xGuess = x
        self.yGuess = y
    
    def update(self, bounds):
        self.x += self.dx
        self.y += self.dy

        if (self.x >= bounds[0]):
            self.x = bounds[0] - 1
            self.dx *= -Particle.restitution
        
        if (self.x < 0):
            self.x = 0
            self.dx *= -Particle.restitution

        if (self.y >= bounds[1]):
            self.y = bounds[1] - 1
            self.dy *= -Particle.restitution
        
        if (self.y < 0):
            self.y = 0
            self.dy *= -Particle.restitution
        
        self.xGuess = self.x + self.dx
        self.yGuess = self.y + self.dy
    
    def accelerate(self, acceleration, dt):
        self.dx += acceleration[0] * dt
        self.dy += acceleration[1] * dt
    
    def applyForce(self, other, dt):
        force = self.evaluateForce(other)

        self.dx -= force[0] * dt
        self.dy -= force[1] * dt

        other.dx += force[0] * dt
        other.dy += force[1] * dt

    def evaluateForce(self, other):
        dist = self.distance(other)

        if (dist > Particle.density * 2):
            return (0, 0)

        xDist = other.xGuess - self.xGuess
        yDist = other.yGuess - self.yGuess

        if (dist == 0):
            angle = random.random() * 2 * math.pi
            xDist = math.cos(angle)
            yDist = math.sin(angle)
        else:
            xDist /= dist
            yDist /= dist

        force \
            = (Particle.density - dist) \
            * (Particle.density * 2 - dist) ** 2 \
            / Particle.density ** 3 \
            * Particle.compressability ** 2 \
            * Particle.restitution

        return (xDist * force, yDist * force)

    def distance(self, other):
        return math.sqrt((self.xGuess - other.xGuess) ** 2 + (self.yGuess - other.yGuess) ** 2)
