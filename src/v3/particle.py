import math, random

class Particle():
    idealDensity = 100
    compressability = 20
    restitution = 0.5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.xGuess = x
        self.yGuess = y

        self.dx = 0
        self.dy = 0

        self.dxGuess = 0
        self.dyGuess = 0

        self.ddx = 0
        self.ddy = 0

        # self.density = 1

    def update(self, bounds):
        self.dx += self.ddx
        self.dy += self.ddy

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

        self.dxGuess = self.dx + self.ddx
        self.dyGuess = self.dy + self.ddy

        self.ddx = 0
        self.ddy = 0

        # self.density = 1
    
    def accelerate(self, acceleration, dt):
        self.ddx += acceleration[0] * dt
        self.ddy += acceleration[1] * dt
    
    def applyForce(self, other, dt):
        force = self.evaluateForce(other)

        self.ddx -= force[0] * dt * Particle.restitution
        self.ddy -= force[1] * dt * Particle.restitution

        other.ddx += force[0] * dt * Particle.restitution
        other.ddy += force[1] * dt * Particle.restitution

    def evaluateForce(self, other):
        distance = self.relativeDistance(other)

        if (distance > Particle.idealDensity * 2):
            return (0, 0)

        position = self.relativePosition(other)

        if (distance == 0):
            angle = random.random() * 2 * math.pi
            position = (math.cos(angle), math.sin(angle))
        else:
            position = (position[0] / distance, position[1] / distance)

        force \
            = (Particle.idealDensity - distance) \
            * (Particle.idealDensity * 2 - distance) ** 2 \
            / Particle.idealDensity ** 3 \
            * Particle.compressability ** 2

        return (position[0] * force, position[1] * force)
    
    # def applyDensity(self, other):
    #     density = self.evaluateDensity(other)

    #     self.density += density
    #     other.density += density
    
    # def evaluateDensity(self, other):
    #     distance = self.relativeDistance(other)

    #     if (distance > Particle.idealDensity * 2):
    #         return 0

    #     density \
    #         = (Particle.idealDensity * 2 - distance) ** 2 \
    #         / Particle.idealDensity ** 2 \
    #         * Particle.compressability ** 2

    #     # density \
    #     #     = (Particle.idealDensity - distance) \
    #     #     * (Particle.idealDensity * 2 - distance) ** 2 \
    #     #     / Particle.idealDensity ** 3 \
    #     #     * Particle.compressability ** 2
        
    #     return density

    def relativePosition(self, other):
        return (other.xGuess - self.xGuess, other.yGuess - self.yGuess)

    def relativeVelocity(self, other):
        return (other.dxGuess - self.dxGuess, other.dyGuess - self.dyGuess)

    def relativeDistance(self, other):
        position = self.relativePosition(other)
        return math.sqrt(position[0] ** 2 + position[1] ** 2)

    def relativeSpeed(self, other):
        velocity = self.relativeVelocity(other)
        return math.sqrt(velocity[0] ** 2 + velocity[1] ** 2)

    def relativeVelocityApart(self, other):
        position = self.relativePosition(other)
        velocity = self.relativeVelocity(other)
        distance = self.relativeDistance(other)
        speed = self.relativeSpeed(other)

        speedApartOverDistance = speed / distance * (position[0] * velocity[0] + position[1] * velocity[1])

        return (position[0] * speedApartOverDistance, position[1] * speedApartOverDistance)

    def relativeSpeedApart(self, other):
        velocity = self.relativeVelocityApart(other)
        return math.sqrt(velocity[0] ** 2 + velocity[1] ** 2)
