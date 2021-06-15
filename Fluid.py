import pygame, math, random, time, Fluid_Particle, Slider

def main():
    pygame.init()
    game = True

    screen = (500, 200, 900)
    display = pygame.display.set_mode(screen[:2], flags = pygame.RESIZABLE)
    pygame.display.set_caption("Fluid Simulator 3D")

    background = (0, 0, 0)

    showParticles = True

    dimensions = (800, 1500, 800)

    sliders = []

    zoom = Slider.Slider(4000, 100, 200, (25, 125), (200, 200, 100), "Zoom", sliders)

    numParticles = 500
    particleSize = 75
    particleColour = [Slider.Slider(0, 255, 200, (25, 25), (200, 100, 100), "Red", sliders),\
                      Slider.Slider(0, 255, 200, (25, 50), (100, 200, 100), "Green", sliders),\
                      Slider.Slider(0, 255, 200, (25, 75), (100, 100, 200), "Blue", sliders)]
    
    gravity = Slider.Slider(0.0, 10.0, 200, (25, 150), (200, 200, 100), "Gravity", sliders)
    viscosity = Slider.Slider(0.9, 0.1, 200, (25, 175), (200, 200, 100), "Viscosity", sliders)

    mouseRange = 100**2

    lightSize = 100
    sizeRatio = lightSize / particleSize
    ceilSizeRatio = math.ceil(sizeRatio)

    smoothing = Slider.Slider(1.0, 10.0, 200, (25, 225), (100, 200, 200), "Light Smoothing", sliders)

    frameDelay = 0.0

    # The mouse position is used to introduce motion
    mousePos = [(0.0, 0.0), pygame.mouse.get_pos()]

    rotation = [0.0, 0.0]

    # Creating the cells array to contain the particles sorted by position
    cells = [[[[] for z in range(dimensions[2] // particleSize + 1)]\
              for y in range(dimensions[1] // particleSize + 1)]\
             for x in range(dimensions[0] // particleSize + 1)]

    # Creating the lights array to store the values at each grid point
    lights = [[[0 for z in range(dimensions[2] // lightSize)]\
               for y in range(dimensions[1] // lightSize)]
              for x in range(dimensions[0] // lightSize)]

    # Creating the particles list to contain the particles for easy access
    particles = [Fluid_Particle.Particle(particleSize, dimensions, cells) for i in range(numParticles)]

    while game:
        # Getting the mouse and key states
        mouse = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

        mousePos[0] = mousePos[1]
        mousePos[1] = pygame.mouse.get_pos()

        # Rotating the 3D view
        if mouse[2]:
            rotation[0] = max(-1, min(1, rotation[0] - (mousePos[1][1] - mousePos[0][1]) * 0.005))
            rotation[1] = max(-1, min(1, rotation[1] + (mousePos[1][0] - mousePos[0][0]) * 0.005))

        # Precomputing sines and cosines of the rotation for rendering
        sincos = [math.sin(rotation[i]) for i in range(2)] + [math.cos(rotation[i]) for i in range(2)]

        display.fill(background)

        # Updating the Sliders
        for slider in sliders: slider.draw(mousePos[1], mouse[0], display)

        # Moving the particles and drawing them
        for particle in particles:
            # Hold P to pause
            if not keys[pygame.K_p]:
                particle.checkCollisions(cells, viscosity.val)
                particle.move(dimensions, cells, gravity.val, viscosity.val)

            pos = project(particle.pos, sincos, dimensions, (0,0,zoom.val), screen)

            if showParticles:
                r = max(0, min(255, particleColour[0].val * pos[1]))
                g = max(0, min(255, particleColour[1].val * pos[1]))
                b = max(0, min(255, particleColour[2].val * pos[1]))

                pygame.draw.circle(display, (r, g, b), pos[0][:2], particleSize*0.5*pos[1])

            # Introducing motion with the mouse
            if mouse[0] and (pos[0][0]-mousePos[1][0])**2 + (pos[0][1]-mousePos[1][1])**2 < mouseRange and pos:
                particle.vel[0] += (mousePos[1][0] - mousePos[0][0])
                particle.vel[1] += (mousePos[0][1] - mousePos[1][1])

        # Drawing the grid points
        if not showParticles:
            for x in range(len(lights)):
                for y in range(len(lights[x])):
                    for z in range(len(lights[x][y]) - 1, -1, -1):
                        cell = [int(x * sizeRatio), int(y * sizeRatio), int(z * sizeRatio)]

                        density = 0

                        for i in range(ceilSizeRatio):
                            for j in range(ceilSizeRatio):
                                for k in range(ceilSizeRatio):
                                    density += len(cells[cell[0] + i][cell[1] + j][cell[2] + k])

                        lights[x][y][z] = (lights[x][y][z] * (smoothing.val - 1) + density) / smoothing.val

                        if lights[x][y][z] > 0.1:
                            pos = project((x*lightSize, y*lightSize, z*lightSize), sincos, dimensions, (0,0,zoom.val), screen)

                            r = max(0, min(255, particleColour[0].val * lights[x][y][z] * 0.25))
                            g = max(0, min(255, particleColour[1].val * lights[x][y][z] * 0.25))
                            b = max(0, min(255, particleColour[2].val * lights[x][y][z] * 0.25))

                            pygame.draw.circle(display, (r, g, b), pos[0][:2], lightSize*0.2*pos[1])

        pygame.display.update()

        time.sleep(frameDelay)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                game = False
            elif e.type == pygame.KEYDOWN and e.__dict__["key"] == 32:
                showParticles = not showParticles
            elif e.type == pygame.VIDEORESIZE:
                screen = display.get_size() + (screen[2],)

def project(point, sincos, offset1, offset2, screen):
    p = [point[i] - offset1[i] / 2 for i in range(3)]

    p[0], p[2] = p[0] * sincos[3] - p[2] * sincos[1], p[0] * sincos[1] + p[2] * sincos[3]
    p[1], p[2] = p[1] * sincos[2] - p[2] * sincos[0], p[1] * sincos[0] + p[2] * sincos[2]

    p[2] += offset2[2]

    if p[2] < 1: p[2] = 1
    ratio = screen[2] / p[2]

    p[0] *= ratio
    p[1] *= -ratio

    p[0] += offset2[0] + screen[0] * 0.5
    p[1] += offset2[1] + screen[1] * 0.5

    return (p, ratio)

main()
