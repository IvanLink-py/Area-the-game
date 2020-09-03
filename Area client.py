import math
import random

import pygame

pygame.init()
pygame.font.init()
win = pygame.display.set_mode((192 * 5, 108 * 5))  # размеры X и Y
icon = pygame.image.load("Game icon.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Area")


class Rectangle:
    def __init__(self, color, pos1, size, text='None'):
        self.x1 = pos1[0]
        self.y1 = pos1[1]

        self.x2 = size[0]
        self.y2 = size[1]

        if text:
            self.text = text

        self.color = color

    def draw(self, grid):
        return grid.get_figure_draw((self.x1, self.y1), (self.x2, self.y2), self.color)

    def true_draw(self):
        pygame.draw.rect(win, 0xFFFFFF, (self.x1, self.y1, self.x2, self.y2))


class Grid:
    def __init__(self, figure_size, grid_size, inlines=False, outlines=False):
        self.figure_size = figure_size
        self.pix_height = figure_size[0]
        self.pix_width = figure_size[1]

        self.grid_size = grid_size
        self.row = grid_size[0]
        self.column = grid_size[1]

        self.cell_size = (self.pix_width / self.column, self.pix_height / self.row)
        self.is_mouse = False

        self.inlines = inlines
        self.outlines = outlines

        self.area = []
        self.raw_area = [[0 for _ in range(grid_size[0])] for _ in range(grid_size[1])]

    def set_mouse_obj(self, mouse_coord, figure_size=None, color=0xFFFFFF):

        if not self.is_mouse:
            if figure_size is None:
                self.mouse_figure_size = [random.randint(1, 6), random.randint(1, 6)]

        self.is_mouse = True
        self.mouse_pos = mouse_coord

        self.mouse_figure_color = color

    def change_mouse(self, absolute=None, relatively=None):
        if self.is_mouse == True:
            if absolute is not None:
                self.mouse_figure_size = absolute

            elif relatively is not None:
                self.mouse_figure_size[0] += relatively[0]
                self.mouse_figure_size[1] += relatively[1]
            else:
                raise NotImplemented

    def del_mouse_obj(self):
        self.is_mouse = False

    def save_mouse_figure(self):
        x1, y1 = self.mouse_pos[0] // self.cell_size[0], self.mouse_pos[1] // self.cell_size[1]
        contacts = []
        for i in range(self.mouse_figure_size[0]):
            try:
                contacts.append(self.raw_area[math.floor(x1 + i)][math.floor(y1 - 1)])
            except IndexError:
                contacts.append(0)
            try:
                contacts.append(self.raw_area[math.floor(x1 + i)][math.floor(y1 + self.mouse_figure_size[1])])
            except IndexError:
                contacts.append(0)

        for i in range(self.mouse_figure_size[1]):
            try:
                contacts.append(self.raw_area[math.floor(x1 - 1)][math.floor(y1 + i)])
            except IndexError:
                contacts.append(0)
            try:
                contacts.append(self.raw_area[math.floor(x1 + self.mouse_figure_size[0])][math.floor(y1 + i)])
            except IndexError:
                contacts.append(0)

        # print(f"{contacts}", end="\n")

        incontinent = []

        for i in range(self.mouse_figure_size[0]):
            for j in range(self.mouse_figure_size[1]):
                incontinent.append(self.raw_area[math.floor(x1 + i)][math.floor(y1 + j)])

        if game.step % 2 + 1 in contacts and not any(incontinent) and incontinent[0] == 0:
            # if True:
            self.area.append(Rectangle(colors[game.step % 2], (x1, y1),
                                       self.mouse_figure_size))

            for i in range(self.mouse_figure_size[0]):
                for j in range(self.mouse_figure_size[1]):
                    self.raw_area[math.floor(x1 + i)][math.floor(y1 + j)] = game.step % 2 + 1

            global myText
            global myText2
            # print(self.mouse_figure_size[0], self.mouse_figure_size[1])
            game.scores[game.step % 2] += self.mouse_figure_size[0] * self.mouse_figure_size[1]
            myText = scores1.render(str(game.scores[0]), 1, colorsRGBA[0])
            myText2 = scores2.render(str(game.scores[1]), 1, colorsRGBA[1])

            game.grid.change_mouse(absolute=(random.randint(1, 6), random.randint(1, 6)))

            game.step += 1

    def get_figure_draw(self, figure, *args):
        if isinstance(figure, Rectangle):
            x1 = figure.x1 * self.cell_size[0]
            y1 = figure.y1 * self.cell_size[1]
            size_x = figure.x2 * self.cell_size[0]
            size_y = figure.y2 * self.cell_size[1]
            if figure.x1 > -1 and figure.x1 + figure.x2 < self.column + 1:
                if figure.y1 > -1 and figure.y1 + figure.y2 < self.row + 1:
                    return [pygame.draw.rect, (win, figure.color, (math.floor(x1) + 1, math.floor(y1),
                                                                   math.floor(size_x) + 1, math.floor(size_y) + 1))]

    def get_main_draw(self):
        instruction = []
        subinstructions = [[], []]

        for figure in self.area:
            draw = self.get_figure_draw(figure)
            if draw is not None:
                if figure.color == colors[0]:
                    subinstructions[0].append(draw)
                elif figure.color == colors[1]:
                    subinstructions[1].append(draw)
                else:
                    subinstructions[0].append(draw)

        for sub in subinstructions[0]:
            instruction.append(sub)

        for sub in subinstructions[1]:
            instruction.append(sub)

        if self.is_mouse:
            x1 = math.floor((self.cell_size[0]) * (self.mouse_pos[0] // self.cell_size[0]))
            y1 = math.floor((self.cell_size[1]) * (self.mouse_pos[1] // self.cell_size[1]))
            x2 = math.floor(self.mouse_figure_size[0] * self.cell_size[0])
            y2 = math.floor(self.mouse_figure_size[1] * self.cell_size[1])
            if x1 > -1 and x1 + x2 < 500 + 1:
                if y1 > -1 and y1 + y2 < 500 + 1:
                    instruction.append((pygame.draw.rect, (win, self.mouse_figure_color, (x1 + 1, y1, x2 + 1, y2 + 1))))

        if self.outlines:
            instruction.append((pygame.draw.lines, (
                win, 0x888888, True, ((0, 0), (self.figure_size[0], 0), self.figure_size, (0, self.figure_size[1])))))

        if self.inlines:
            for i in range(1, self.column):
                instruction.append((pygame.draw.lines, (win, 0x888888, True, (
                    (math.floor(self.cell_size[0] * i), 0),
                    (math.floor(self.cell_size[0] * i), self.figure_size[1])
                ))))
            for i in range(1, self.row):
                instruction.append((pygame.draw.lines, (win, 0x888888, True, (
                    (0, math.floor(self.cell_size[1] * i)),
                    (self.figure_size[0], math.floor(self.cell_size[1] * i))))))

        return instruction


class Game:
    def __init__(self, grid_size, gws, player_colors, inlines, outlines):
        self.is_first_player_step = True
        self.step = 0
        self.grid = Grid(gws, grid_size, inlines, outlines)

        self.grid.area = [Rectangle(player_colors[0], (0, 0), (1, 1)),
                          Rectangle(player_colors[1], (self.grid.column - 1, self.grid.row - 1), (1, 1))]

        self.grid.raw_area[0][0] = 1
        self.grid.raw_area[self.grid.column - 1][self.grid.row - 1] = 2

        self.player_colors = player_colors

        self.scores = [1, 1]

    def plus1score(self, player_id):
        self.scores[player_id] += 1


def score_text():
    myText = scores1.render(str(game.scores[0]), 1, colorsRGBA[0], pygame.Color(0, 0, 0, 1))
    myText2 = scores2.render(str(game.scores[1]), 1, colorsRGBA[1], pygame.Color(0, 0, 0, 1))

    win.blit(myText, (550, 50))
    win.blit(myText2, (580, 50))


def keyboard():
    global keys
    global mouse_keys

    def esc():
        game.grid.change_mouse(absolute=(random.randint(1, 6), random.randint(1, 6)))
        game.step += 1

    def rotate():
        game.grid.change_mouse(absolute=(game.grid.mouse_figure_size[1], game.grid.mouse_figure_size[0]))

    def set_figure():
        game.grid.save_mouse_figure()

    key_binds = {pygame.K_ESCAPE: esc, pygame.K_r: rotate, pygame.K_F12: fill}
    mouse_binds = [set_figure, None, rotate]

    for key, func in key_binds.items():
        if pygame.key.get_pressed()[key]:
            if not keys[key]:
                func()
                keys[key] = True
        else:
            keys[key] = False

    for button_id in range(len(mouse_binds)):
        if pygame.mouse.get_pressed()[button_id]:
            if not mouse_keys[button_id]:
                mouse_binds[button_id]()
                mouse_keys[button_id] = True
        else:
            mouse_keys[button_id] = False


def fill():
    game.grid.is_mouse = False

    def get_empty():
        _empty_cells = []
        for i in range(len(game.grid.raw_area)):
            for j in range(len(game.grid.raw_area[i])):
                if game.grid.raw_area[i][j] == 0:
                    cell = (i, j)
                    sides = [0 if cell[0] == grid_size[0] - 1 else game.grid.raw_area[cell[0] + 1][cell[1]],
                             0 if cell[0] == 0 else game.grid.raw_area[cell[0] - 1][cell[1]],
                             0 if cell[1] == grid_size[1] - 1 else game.grid.raw_area[cell[0]][cell[1] + 1],
                             0 if cell[1] == 0 else game.grid.raw_area[cell[0]][cell[1] - 1]]
                    if any(sides):
                        _empty_cells.append((i, j, sides))
        return _empty_cells

    empty_cells = get_empty()
    while len(empty_cells) != 0:
        empty_cells_count = len(empty_cells)
        cell_id = random.randint(0, empty_cells_count - 1)
        cell = empty_cells[cell_id]
        global grid_size
        sides = [0 if cell[0] == grid_size[0] - 1 else game.grid.raw_area[cell[0] + 1][cell[1]],
                 0 if cell[0] == 0 else game.grid.raw_area[cell[0] - 1][cell[1]],
                 0 if cell[1] == grid_size[1] - 1 else game.grid.raw_area[cell[0]][cell[1] + 1],
                 0 if cell[1] == 0 else game.grid.raw_area[cell[0]][cell[1] - 1]]

        if any(sides):
            print("\r" + str(sides) + "  " + str(len(empty_cells)) + "  " + str(game.scores), end='')
            players = [side for side in sides if side]
            game.grid.area.append(Rectangle(colors[players[0] - 1], cell, (1, 1)))
            game.grid.raw_area[cell[0]][cell[1]] = players[0]
            game.plus1score(players[0] - 1)

            score_text()

            instr = game.grid.get_main_draw()

            for i in instr:
                i[0](*i[1])

            pygame.display.update()

            empty_cells = get_empty()


colors = (0xFFA000, 0xA52A2A)
colorsRGBA = [pygame.Color(255, 160, 0, 1), pygame.Color(165, 45, 45, 1)]

grid_widget_size = (500, 500)
grid_size = (40, 40)
lines = (False, True)
game = Game(grid_size, grid_widget_size, colors, *lines)

scores1 = pygame.font.SysFont("Arial", 16)

scores2 = pygame.font.SysFont("Arial", 16)

keys = {pygame.K_ESCAPE: False, pygame.K_r: False}
mouse_keys = [False, False, False]

fps = 60
clock = pygame.time.Clock()

run = True

while run:
    win.fill(0)

    if pygame.mouse.get_focused():
        game.grid.set_mouse_obj(pygame.mouse.get_pos(), color=colors[game.step % 2])

    keyboard()

    score_text()

    instr = game.grid.get_main_draw()

    for i in instr:
        i[0](*i[1])

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        else:
            pass

    clock.tick(fps)

pygame.quit()
quit()
