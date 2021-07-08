from pygame import draw, font
font.init()

class Button():
    text = font.SysFont("timesnewroman", 15)

    def __init__(self, width, pos, colour, key, name, array = None):
        self.width = width
        self.pos = pos

        self.colour = colour

        self.name = Button.text.render(name, True, colour, (0,0,0))
        self.centre = (self.name.get_rect().width // 2 - self.width // 2, 6)

        self.key = key

        self.val = False

        if array != None: array.append(self)

    def draw(self, mousePos, mouseDown, keys, display):
        if (mouseDown and mousePos[0] > self.pos[0] and mousePos[1] > self.pos[1] and mousePos[0] < self.pos[0] + self.width and mousePos[1] < self.pos[1] + 30) or keys[self.key]:
            colour = (self.colour[0] * 0.5, self.colour[1] * 0.5, self.colour[2] * 0.5)
            self.val = True
        else:
            colour = self.colour
            self.val = False

        draw.rect(display, colour, (self.pos[0], self.pos[1], self.width, 30), 1)
        display.blit(self.name, (self.pos[0] - self.centre[0], self.pos[1] + self.centre[1]))
