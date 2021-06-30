import pygame, math, random, time, Fluid_Particle, Slider

def main():
    # Initializing
    pygame.init()
    game = True
    screen = (500, 200, 900)
    display = pygame.display.set_mode(screen[:2], flags = pygame.RESIZABLE)
    pygame.display.set_caption("Fluid Simulator 3D")

    background = (0, 0, 0)

    # When showParticles is False, the light cube display is shown
    # When showParticles is True, the individual particles are shown
    showParticles = False

    # The size of the space the fluid exists in
    dimensions = (700, 1400, 700)

    numParticles = 1000
    particleSize = 50

    # The width of the light cube lights (in pixels) and precomputed relevant ratios
    lightSize = 100
    sizeRatio = lightSize / particleSize
    ceilSizeRatio = math.ceil(sizeRatio)

    # Palattes are used to give particles different colours and properties
    numPalattes = 3
    palatte = [{} for i in range(numPalattes)]

    # All of the sliders are kept in this list for easy access
    sliders = []

    zoom = Slider.Slider(4000, 100, 200, (25, 375), (200, 100, 200), "Zoom", sliders)                   # The zoom level of the 3D render

    brightness = Slider.Slider(0.0, 1.0, 200, (25, 275), (100, 200, 200), "Brightness", sliders)        # The brightness of the lights

    smoothing = Slider.Slider(1.0, 10.0, 200, (25, 300), (100, 200, 200), "Light Smoothing", sliders)   # The amount of smoothing on the lights

    frameDelay = Slider.Slider(0.1, 0.0, 200, (25, 325), (100, 200, 200), "Speed", sliders)             # The delay between frames
    frameDelay.adjust((225, 325))

    # Setting the palatte properties
    for i in range(numPalattes):
        palatte[i]["colour"] = [Slider.Slider(0, 255, 200, (25 + 300 * i, 25), (200, 100, 100), "Red", sliders),\
                                Slider.Slider(0, 255, 200, (25 + 300 * i, 50), (100, 200, 100), "Green", sliders),\
                                Slider.Slider(0, 255, 200, (25 + 300 * i, 75), (100, 100, 200), "Blue", sliders)]           # The colour of the fluid
        
        palatte[i]["density"] = Slider.Slider(0.9, 0.1, 200, (25 + 300 * i, 125), (200, 200, 100), "Density", sliders)      # The density of the fluid
        palatte[i]["gravity"] = [[Slider.Slider(-dimensions[j]*0.5, dimensions[j]*1.5, 200, (25 + 300 * i, 175 + j * 25), (200, 100, 200), "Gravity " + chr(ord("X") + j), sliders) for j in range(3)],\
                                 Slider.Slider(-10.0, 10.0, 200, (25 + 300 * i, 150), (200, 200, 100), "Gravity", sliders)] # The point and force of gravity

    # Creating the cells array to contain the particles sorted by position
    cells = [[[[] for z in range(dimensions[2] // particleSize + 1)]\
              for y in range(dimensions[1] // particleSize + 1)]\
             for x in range(dimensions[0] // particleSize + 1)]

    # Creating the lights array to store the values at each light point in the cube
    lights = [[[[0, 0, 0] for z in range(dimensions[2] // lightSize + 1)]\
               for y in range(dimensions[1] // lightSize + 1)]
              for x in range(dimensions[0] // lightSize + 1)]

    # Creating the light cells array to store the particles near each light point in the cube
    lightCells = [[[[] for z in range(len(lights[x][y]))]\
               for y in range(len(lights[x]))]
              for x in range(len(lights))]

    # Creating the particles list to contain the particles for easy access
    particles = [Fluid_Particle.Particle(random.randint(0, numPalattes - 1), dimensions, [cells, lightCells], [particleSize, lightSize]) for i in range(numParticles)]

    # The mouse is used to move the particles within a certain range and rotate the screen
    mouseRange = 15000
    mousePos = [(0.0, 0.0), pygame.mouse.get_pos()]
    rotation = [0.0, 0.0]

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
                particle.checkCollisions(cells, particleSize, palatte[particle.id]["density"].val)
                particle.move(dimensions, [cells, lightCells], [particleSize, lightSize], palatte[particle.id]["gravity"], palatte[particle.id]["density"].val)

            # Finding the position of the particle on the screen
            pos = project(particle.pos, sincos, [dimensions[i]*0.5 for i in range(3)], (0, 0, zoom.val), screen)

            if showParticles:
                r = max(0, min(255, palatte[particle.id]["colour"][0].val * pos[1]))
                g = max(0, min(255, palatte[particle.id]["colour"][1].val * pos[1]))
                b = max(0, min(255, palatte[particle.id]["colour"][2].val * pos[1]))

                pygame.draw.circle(display, (r, g, b), pos[0][:2], particleSize*0.5*pos[1])

            # Introducing motion with the mouse
            if mouse[0] and (pos[0][0]-mousePos[1][0])**2 + (pos[0][1]-mousePos[1][1])**2 < mouseRange and pos:
                particle.vel[0] += (mousePos[1][0] - mousePos[0][0])
                particle.vel[1] += (mousePos[0][1] - mousePos[1][1])

        # Drawing the lights
        if not showParticles:
            dataStr = ""

            # Iterating through each light in the cube
            for x in range(len(lights)):
                for y in range(len(lights[x])):
                    for z in range(len(lights[x][y])):
                        # The average colour of all the particles in the range of the light is stored here
                        colour = [0, 0, 0]

                        # Iterating through all of the particles near the light
                        for particle in lightCells[x][y][z]:
                            # Iterating through each colour channel in each particle and storing it
                            for i in range(3):
                                colour[i] += palatte[particle.id]["colour"][i].val

                        # Averaging it with the previous colour value of the light
                        for i in range(3):
                            lights[x][y][z][i] = (lights[x][y][z][i] * (smoothing.val - 1) + colour[i]) / smoothing.val

                        dataStr += " " + bin(int(lights[x][y][z][0]))[2:].zfill(8) + " " + bin(int(lights[x][y][z][1]))[2:].zfill(8) + " " + bin(int(lights[x][y][z][2]))[2:].zfill(8)

                        # Projecting the light point and capping the colour before drawing it to the screen
                        if sum(lights[x][y][z]) > 0.3:
                            pos = project((x*lightSize, y*lightSize, z*lightSize), sincos, [dimensions[i]*0.5 for i in range(3)], (lightSize*0.25, lightSize*-0.25, zoom.val), screen)

                            r = max(0, min(255, lights[x][y][z][0] * brightness.val))
                            g = max(0, min(255, lights[x][y][z][1] * brightness.val))
                            b = max(0, min(255, lights[x][y][z][2] * brightness.val))

                            pygame.draw.circle(display, (r, g, b), pos[0][:2], lightSize*0.2*pos[1])

            if keys[pygame.K_l]: print(getDDP(dataStr))

        pygame.display.update()

        time.sleep(frameDelay.val)

        # Getting the pygame events to pause the simulation, change modes, and quit
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                game = False
            elif e.type == pygame.KEYDOWN and e.__dict__["key"] == 32:
                showParticles = not showParticles
            elif e.type == pygame.VIDEORESIZE:
                screen = display.get_size() + (screen[2],)

def getDDP(data):
    length = bin(len(data) // 8)[2:].zfill(16)

    return "01000001 00000000 00000000 00000001 00000000 00000000 00000000 00000011 " + length[:8] + " " + length[8:] + data

# A function to rotate and project a point in 3D space to a 2D screen
def project(point, sincos, origin, offset, screen):
    # Offsetting the point to the rotation origin
    p = [point[i] - origin[i] for i in range(3)]

    p[2] *= -1

    # Rotating the point around the x and y axes
    p[0], p[2] = p[0] * sincos[3] - p[2] * sincos[1], p[0] * sincos[1] + p[2] * sincos[3]
    p[1], p[2] = p[1] * sincos[2] - p[2] * sincos[0], p[1] * sincos[0] + p[2] * sincos[2]

    # Offsetting the Z coordinate of the point
    p[2] += offset[2]

    # Cutting out points behind or too close to the screen and then getting the ratio
    if p[2] < 1: p[2] = 1
    ratio = screen[2] / p[2]

    # Projecting the X and Y coordinates by the ratio and adding the offset
    p[0] *= ratio
    p[1] *= -ratio

    p[0] += offset[0] + screen[0] * 0.5
    p[1] += offset[1] + screen[1] * 0.5

    return (p, ratio)

main()
