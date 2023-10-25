import pygame, particle, random, time, slider

def main():
    pygame.init()

    screenSize = (500, 500)
    display = pygame.display.set_mode(screenSize, flags = pygame.RESIZABLE)

    particles = [
        particle.Particle(random.randint(0, screenSize[0] - 1), random.randint(0, screenSize[1] - 1))
        for i in range(100)
    ]

    dt = 0.01

    density = slider.Slider(10, 500, 200, (10, 10), (0, 0, 0), "Density")
    compressability = slider.Slider(5, 50, 200, (10, 30), (0, 0, 0), "Compressability")

    density.set(particle.Particle.density)
    compressability.set(particle.Particle.compressability)

    while True:
        pygame.display.update()
        display.fill((255, 255, 255))
        time.sleep(dt)

        particle.Particle.density = density.val
        particle.Particle.compressability = compressability.val
        density.draw(display, pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])
        compressability.draw(display, pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])

        for i in range(len(particles)):
            for j in range(i + 1, len(particles)):
                particles[i].applyForce(particles[j], dt)

        for p in particles:
            p.applyWallForce(screenSize, dt)
            p.move(screenSize, (0, 1))
            pygame.draw.circle(display, (0, 0, 0), (p.x, p.y), 10)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            elif e.type == pygame.VIDEORESIZE:
                screenSize = display.get_size()

if __name__ == "__main__":
    main()
