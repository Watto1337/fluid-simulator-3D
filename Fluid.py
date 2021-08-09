import pygame, math, random, time, socket, Particle, Slider, Button

# lightSize is an integer that controls the distance between the lights in the array
# lightDimensions is a list of 3 integers stating the dimensions of the light array: [width, height, depth]
# numPalattes is the integer number of particle types
# numParticles is the number of particles simulated
# particleSize is the size of all the particles
def main(lightSize, lightDimensions, numPalattes, numParticles, particleSize):
    # Initializing the digital display
    pygame.init()
    screen = (500, 200, 900)
    background = (0, 0, 0)
    display = pygame.display.set_mode(screen[:2], flags = pygame.RESIZABLE)
    pygame.display.set_caption("Fluid Simulator 3D")

    sizeRatio = lightSize / particleSize
    ceilSizeRatio = math.ceil(sizeRatio)
    dimensions = [lightDimensions[i] * lightSize - 1 for i in range(3)]

    # All of the sliders and buttons are kept in lists for easy access
    sliders = []
    buttons = []
    palatte = [{} for i in range(numPalattes)]

    # Some buttons to control the particles directly
    # They can be controlled by the corresponding number pad keys or the mouse
    # To affect particles you need to hold down the number of that palatte while you press the buttons
    waveLeft   = Button.Button(60, (25,  290), (100, 150, 250), pygame.K_KP4, "Left", buttons)
    waveRight  = Button.Button(60, (165, 290), (100, 150, 250), pygame.K_KP6, "Right", buttons)
    waveUp     = Button.Button(60, (95,  250), (100, 150, 250), pygame.K_KP8, "Up", buttons)
    waveDown   = Button.Button(60, (95,  330), (100, 150, 250), pygame.K_KP2, "Down", buttons)
    waveCentre = Button.Button(60, (95,  290), (100, 150, 250), pygame.K_KP5, "Centre", buttons)

    flipGrav   = Button.Button(60, (25,  250), (250, 100, 150), pygame.K_KP7, "Reverse", buttons)

    # The force the buttons apply
    force = Slider.Slider(0.0, 25.0, 200, (25, 385), (100, 150, 250), "Force", sliders)

    # Creating a socket to send the data to the lights
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    # Setting the palatte properties
    for i in range(numPalattes):
        # The colour of the fluid
        palatte[i]["colour"] = [Slider.Slider(0, 255, 200, (25 + 300 * i, 25), (200, 100, 100), "Red", sliders),\
                                Slider.Slider(0, 255, 200, (25 + 300 * i, 50), (100, 200, 100), "Green", sliders),\
                                Slider.Slider(0, 255, 200, (25 + 300 * i, 75), (100, 100, 200), "Blue", sliders)]

        # The density of the fluid
        palatte[i]["density"] = Slider.Slider(1.0, 0.5, 200, (25 + 300 * i, 125), (200, 200, 100), "Density", sliders)

        # The point and force of gravity
        palatte[i]["gravity"] = [[Slider.Slider(-dimensions[j], dimensions[j]*2, 200, (25 + 300 * i, 175 + j * 25), (200, 100, 200), "Gravity " + chr(ord("X") + j), sliders) for j in range(3)],\
                                 Slider.Slider(-25.0, 25.0, 200, (25 + 300 * i, 150), (200, 200, 100), "Gravity", sliders)]

    brightness = Slider.Slider(0.0, 1.0, 200, (25, 435), (100, 200, 200), "Brightness", sliders)

    smoothing = Slider.Slider(1.0, 10.0, 200, (25, 460), (100, 200, 200), "Light Smoothing", sliders)

    frameDelay = Slider.Slider(0.1, 0.0, 200, (25, 485), (100, 200, 200), "Speed", sliders)
    frameDelay.set(0.0)

    zoom = Slider.Slider(4000, 100, 200, (25, 535), (200, 100, 200), "Zoom", sliders)

    # Creating the cells array to contain the particles sorted by position
    cells = [[[[] for z in range(dimensions[2] // particleSize + 1)]\
              for y in range(dimensions[1] // particleSize + 1)]\
             for x in range(dimensions[0] // particleSize + 1)]

    # Creating the lights array to store the values at each light point in the cube
    lights = [[[[0, 0, 0] for z in range(lightDimensions[2])]\
               for y in range(lightDimensions[1])]
              for x in range(lightDimensions[0])]

    # Creating the light cells array to store the particles near each light point in the cube
    lightCells = [[[[] for z in range(lightDimensions[2])]\
               for y in range(lightDimensions[1])]
              for x in range(lightDimensions[0])]

    # Creating the particles list to contain the particles for easy access
    particles = [Particle.Particle(random.randint(0, numPalattes - 1), dimensions, [cells, lightCells], [particleSize, lightSize]) for i in range(numParticles)]

    # The mouse is used to rotate the 3D view and control the sliders and buttons
    mousePos = [(0.0, 0.0), pygame.mouse.get_pos()]
    rotation = [0.0, 0.0]

    totalLights = math.prod(lightDimensions) * 3

    while True:
        # Getting the mouse and key states
        mouse = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

        # Tracking the last mouse position and the current to make the rotations smooth
        mousePos[0] = mousePos[1]
        mousePos[1] = pygame.mouse.get_pos()

        # Rotating the 3D view
        if mouse[2]:
            rotation[0] = max(-1, min(1, rotation[0] - (mousePos[1][1] - mousePos[0][1]) * 0.005))
            rotation[1] = max(-1, min(1, rotation[1] + (mousePos[1][0] - mousePos[0][0]) * 0.005))

        # Precomputing sines and cosines of the rotation for rendering
        sincos = [math.sin(rotation[i]) for i in range(2)] + [math.cos(rotation[i]) for i in range(2)]

        display.fill(background)

        # Updating the Sliders and Buttons
        for slider in sliders: slider.draw(mousePos[1], mouse[0], display)
        for button in buttons: button.draw(mousePos[1], mouse[0], keys, display)

        # Moving the particles
        for particle in particles:
            # Hold P to pause
            if not keys[pygame.K_p]:
                # Adding the effects from the buttons
                if keys[pygame.K_1 + particle.id]:
                    if waveLeft.val: particle.vel[0]  -= force.val
                    if waveRight.val: particle.vel[0] += force.val
                    if waveUp.val: particle.vel[1]    += force.val
                    if waveDown.val: particle.vel[1]  -= force.val

                    if waveCentre.val:
                         gravVect = [particle.pos[i] - dimensions[i] * 0.5 for i in range(3)]
                         if not (0 in gravVect):
                             gravLen = force.val / math.sqrt(gravVect[0]**2 + gravVect[1]**2 + gravVect[2]**2)
                             for i in range(3):
                                 particle.vel[i] -= gravVect[i] * gravLen

                    if flipGrav.val: palatte[particle.id]["gravity"][1].val = palatte[particle.id]["gravity"][1].n * -1

                particle.checkCollisions(cells, particleSize, palatte[particle.id]["density"].val)
                particle.move(dimensions, [cells, lightCells], [particleSize, lightSize], palatte[particle.id]["gravity"], palatte[particle.id]["density"].val)

        data = []

        # Drawing the lights and computing the data to send to the lights
        for x in range(lightDimensions[0]):
            for y in range(lightDimensions[1]):
                for z in range(lightDimensions[2]):
                    # The average colour of all the particles in the range of the light is stored here
                    colour = [0, 0, 0]

                    # Iterating through all of the particles near the light
                    for particle in lightCells[x][y][z]:
                        # Iterating through each colour channel in each particle and storing it
                        for i in range(3):
                            colour[i] += palatte[particle.id]["colour"][i].val

                    # Averaging it with the previous colour value of the light and storing the data
                    for i in range(3):
                        lights[x][y][z][i] = max(0, min(255, (lights[x][y][z][i] * (smoothing.val - 1) + colour[i]) / smoothing.val))
                        data.append(int(lights[x][y][z][i] * brightness.val))

                    # Projecting the light point and capping the colour before drawing it to the screen
                    if sum(lights[x][y][z]) > 0.3:
                        pos = project((x*lightSize, y*lightSize, z*lightSize), sincos, [dimensions[i]*0.5 for i in range(3)], (lightSize*0.25, lightSize*-0.25, zoom.val), screen)

                        r = lights[x][y][z][0] * brightness.val
                        g = lights[x][y][z][1] * brightness.val
                        b = lights[x][y][z][2] * brightness.val

                        pygame.draw.circle(display, (r, g, b), pos[0][:2], lightSize*0.2*pos[1])

        sock.sendto(getDDP(data), ("10.0.0.255", 4048))

        pygame.display.update()

        time.sleep(frameDelay.val)

        # Getting the pygame events to pause the simulation, change modes, and quit
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sock.sendto(getDDP([0 for i in range(totalLights)]), ("10.0.0.255", 4048))
                sock.close()
                pygame.quit()
                quit()
                break
            elif e.type == pygame.VIDEORESIZE:
                screen = display.get_size() + (screen[2],)

def getDDP(data):
    return bytearray([65, 0, 0, 1, 0, 0, 0, 3, len(data) >> 8, len(data) & 255] + data)

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
    p[0] = p[0] * ratio + offset[0] + screen[0] * 0.5
    p[1] = p[1] * -ratio + offset[1] + screen[1] * 0.5

    return (p, ratio)

if __name__ == "__main__": main(100, (8, 15, 8), 3, 1000, 25)
