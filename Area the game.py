#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import random
import time
import socket
import threading

import pygame

pygame.init()
pygame.font.init()
win = pygame.display.set_mode((800, 600), pygame.SRCALPHA)  # размеры X и Y
pygame.display.set_icon(pygame.image.load("ico.png"))
pygame.display.set_caption("Area")


class Rectangle:
    def __init__(self, color, pos1, size, text=None):
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


class Button:
    hover = False

    def __init__(self, pos1, pos2, target, color_reg, color_hov=None, text=None, text_color=None, font=None,
                 font_size=None, text_correct=(10, -2)):
        self.pos1 = pos1
        self.pos2 = pos2

        self.colors = (color_reg, color_hov if color_hov is not None else color_reg)
        self.target = target

        if text is not None and text_color is not None and font is not None and font_size is not None:
            self.text_obj = pygame.font.SysFont(font, font_size)
            self.font_size = font_size
            self.text_color = text_color
            self.text_correct = text_correct

        self.text = text

    def check_hover(self):
        mouse = pygame.mouse.get_pos()
        if (self.pos1[0] < mouse[0] < self.pos1[0] + self.pos2[0]) and (
                self.pos1[1] < mouse[1] < self.pos1[1] + self.pos2[1]):
            self.hover = True
        else:
            self.hover = False

    def get_draw(self):
        if self.text is not None:
            button_text = self.text_obj.render(self.text, 1, self.text_color, self.colors[self.hover])
            return [(pygame.draw.rect, (win, self.colors[self.hover], (self.pos1, self.pos2))),
                    (win.blit, (button_text, (math.floor(
                        self.pos1[0] + self.pos2[0] / 2 - len(self.text) * self.font_size / 2 + self.text_correct[0]),
                                              math.floor(self.pos1[1] + self.pos2[1] / 2 - self.font_size / 2 +
                                                         self.text_correct[1]))))]
        else:
            return pygame.draw.rect, (win, self.colors[self.hover], (self.pos1, self.pos2))

    def check_click(self):
        if self.target is not None:
            mouse = pygame.mouse.get_pos()
            if (self.pos1[0] < mouse[0] < self.pos1[0] + self.pos2[0]) and (
                    self.pos1[1] < mouse[1] < self.pos1[1] + self.pos2[1]) and (
                    pygame.mouse.get_pressed()[0]):
                if pygame.mouse.get_pressed()[0]:
                    self.target()

    def checker(self):
        self.check_hover()
        self.check_click()

    def draw(self):
        self.checker()
        pygame.draw.rect(win, self.colors[self.hover], (self.pos1, self.pos2))
        button_text = self.text_obj.render(self.text, 1, self.text_color, self.colors[self.hover])

        win.blit(button_text, (
            math.floor(self.pos1[0] + self.pos2[0] / 2 - len(self.text) * self.font_size / 2 + self.text_correct[0]),
            math.floor(self.pos1[1] + self.pos2[1] / 2 - self.font_size / 2 + self.text_correct[1])))


class Grid_of_game:
    def __init__(self, grid_pos, figure_size, grid_size, inlines=False, outlines=False):
        self.grid_pos = grid_pos

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

    def set_mouse_obj(self, mouse_coord, figure_size=None, color=pygame.Color(255, 255, 255)):

        if not self.is_mouse:
            if figure_size is None:
                self.mouse_figure_size = [random.randint(1, menu.game.max_sizes[0]),
                                          random.randint(1, menu.game.max_sizes[1])]

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
        x1, y1 = (self.mouse_pos[0] - self.grid_pos[0]) // self.cell_size[0], \
                 (self.mouse_pos[1] - self.grid_pos[1]) // self.cell_size[1]
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

        inside = []

        for i in range(self.mouse_figure_size[0]):
            for j in range(self.mouse_figure_size[1]):
                inside.append(self.raw_area[math.floor(x1 + i)][math.floor(y1 + j)])

        if (menu.game.step % 2 + 1 in contacts or (self.mouse_figure_size == (1, 1) and menu.game.alone_one)) \
                and not any(inside) and inside[0] == 0:

            self.area.append(Rectangle(colorsRGBA[menu.game.step % 2], (x1, y1),
                                       self.mouse_figure_size))

            for i in range(self.mouse_figure_size[0]):
                for j in range(self.mouse_figure_size[1]):
                    self.raw_area[math.floor(x1 + i)][math.floor(y1 + j)] = menu.game.step % 2 + 1

            global myText
            global myText2
            menu.game.scores[menu.game.step % 2] += self.mouse_figure_size[0] * self.mouse_figure_size[1]
            myText = menu.game.scores1.render(str(menu.game.scores[0]), 1, colorsRGBA[0])
            myText2 = menu.game.scores2.render(str(menu.game.scores[1]), 1, colorsRGBA[1])

            menu.game.grid.change_mouse(
                absolute=(random.randint(1, menu.game.max_sizes[0]), random.randint(1, menu.game.max_sizes[1])))

            menu.game.step += 1
            menu.game.get_current_player()

    def get_figure_draw(self, figure, *args):
        if isinstance(figure, Rectangle):
            x1 = figure.x1 * self.cell_size[0]
            y1 = figure.y1 * self.cell_size[1]
            size_x = figure.x2 * self.cell_size[0]
            size_y = figure.y2 * self.cell_size[1]
            if figure.x1 > -1 and figure.x1 + figure.x2 < self.column + 1:
                if figure.y1 > -1 and figure.y1 + figure.y2 < self.row + 1:
                    return [pygame.draw.rect, (
                        win, figure.color, (self.grid_pos[0] + math.floor(x1) + 1, math.floor(self.grid_pos[1] + y1),
                                            math.floor(size_x) + 1, math.floor(size_y) + 1))]

    def get_main_draw(self):
        instruction = []
        instructions = [[], []]

        if self.inlines:
            for i in range(1, self.column):
                instruction.append((pygame.draw.lines, (win, 0x888888, True, (
                    (math.floor(self.grid_pos[0] + self.cell_size[0] * i), self.grid_pos[1]),
                    (math.floor(self.grid_pos[0] + self.cell_size[0] * i), self.grid_pos[1] + self.figure_size[1])
                ))))
            for i in range(1, self.row):
                instruction.append((pygame.draw.lines, (win, 0x888888, True, (
                    (self.grid_pos[0], math.floor(self.grid_pos[1] + self.cell_size[1] * i)),
                    (self.grid_pos[0] + self.figure_size[0], math.floor(self.grid_pos[0] + self.cell_size[1] * i))))))

        for figure in self.area:
            draw = self.get_figure_draw(figure)
            if draw is not None:
                if figure.color == colorsRGBA[0]:
                    instructions[0].append(draw)
                elif figure.color == colorsRGBA[1]:
                    instructions[1].append(draw)
                else:
                    instructions[0].append(draw)

        for sub in instructions[0]:
            instruction.append(sub)

        for sub in instructions[1]:
            instruction.append(sub)

        if self.is_mouse:
            x1 = math.floor((self.cell_size[0]) * (self.mouse_pos[0] // self.cell_size[0]))
            y1 = math.floor((self.cell_size[1]) * (self.mouse_pos[1] // self.cell_size[1]))
            x2 = math.floor(self.mouse_figure_size[0] * self.cell_size[0])
            y2 = math.floor(self.mouse_figure_size[1] * self.cell_size[1])
            if x1 > -1 + self.grid_pos[0] and x1 + x2 < self.figure_size[0] + 1 + self.grid_pos[0]:
                if y1 > -1 + self.grid_pos[1] and y1 + y2 < self.figure_size[1] + 1 + self.grid_pos[1]:
                    instruction.append((pygame.draw.rect, (
                        win, self.mouse_figure_color,
                        (x1 + 1, y1, x2 + 1, y2 + 1))))

        if self.outlines:
            instruction.append((pygame.draw.lines, (
                win, 0x888888, True, (self.grid_pos, (self.grid_pos[0] + self.figure_size[0], self.grid_pos[1]),
                                      (self.grid_pos[0] + self.figure_size[0], self.grid_pos[1] + self.figure_size[1]),
                                      (self.grid_pos[0], self.grid_pos[1] + self.figure_size[1])))))

            instruction.append((pygame.draw.lines, (
                win, 0, True, ((self.grid_pos[0] - 1, self.grid_pos[1] - 1),
                               (self.grid_pos[0] + self.figure_size[0] + 1, self.grid_pos[1] - 1),
                               (self.grid_pos[0] + self.figure_size[0] + 1, self.grid_pos[1] + self.figure_size[1] + 1),
                               (self.grid_pos[0] - 1, self.grid_pos[1] + self.figure_size[1] + 1)))))

        return instruction


class Game:
    alone_one = True
    play = True
    end_game = False

    scores1 = pygame.font.SysFont("Gouranga Cyrillic", 32)

    scores2 = pygame.font.SysFont("Gouranga Cyrillic", 32)

    keys = {pygame.K_ESCAPE: False, pygame.K_r: False}
    mouse_keys = [False, False, False]

    fps = 60
    clock = pygame.time.Clock()

    def __init__(self, players, grid_pos, grid_size, gws, max_sizes, player_colors, inlines, outlines):
        self.players = players
        self.step = 0
        self.current_player = self.players[self.step % 2]

        self.is_first_player_step = True
        self.grid = Grid_of_game(grid_pos, gws, grid_size, inlines, outlines)

        self.grid.area = [Rectangle(player_colors[0], (0, 0), (1, 1)),
                          Rectangle(player_colors[1], (self.grid.column - 1, self.grid.row - 1), (1, 1))]

        self.grid.raw_area[0][0] = 1
        self.grid.raw_area[self.grid.column - 1][self.grid.row - 1] = 2

        self.max_sizes = max_sizes

        self.player_colors = player_colors

        self.scores = [1, 1]

        self.status_bar = self.setup_status_bar((620, 390), (20, 20), (True, True))

    def get_current_player(self):
        self.current_player = self.players[self.step % 2]

    def mainloop(self):
        self.back = self.gen_bg()
        quit_ = False
        click_delay = 20
        can_click = False

        while self.play:
            self.back()

            if self.current_player.get_mouse_focus():
                self.grid.set_mouse_obj(self.current_player.get_mouse_pos(), color=colorsRGBA[self.step % 2])

            self.score_text()

            if can_click:
                self.keyboard()
            else:
                if click_delay > 0:
                    click_delay -= 1
                else:
                    can_click = True

            if not self.end_game:

                instr = self.grid.get_main_draw()
                instr += self.status_bar()

                for i in instr:
                    i[0](*i[1])

                pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.play = False
                    quit_ = True
                    break
                else:
                    pass

            if quit_:
                break

            self.clock.tick(self.fps)

        else:
            self.show_end_msg()

    def setup_status_bar(self, pos, cell_size, lines):
        bar_size = list((ci + 2 for ci in self.max_sizes))
        figure_size = list((bar_size[ci] * cell_size[ci] for ci in range(2)))

        def get_instr():
            nonlocal lines
            nonlocal figure_size
            nonlocal bar_size

            instruction = [[pygame.draw.rect, (win, 0, (pos, figure_size))]]
            if lines[1]:
                instruction.append((pygame.draw.lines, (
                    win, 0x888888, True, (pos, (pos[0] + figure_size[0], pos[1]),
                                          (pos[0] + figure_size[0],
                                           pos[1] + figure_size[1]),
                                          (pos[0], pos[1] + figure_size[1])))))

                instruction.append((pygame.draw.lines, (
                    win, 0, True, ((pos[0] - 1, pos[1] - 1),
                                   (pos[0] + figure_size[0] + 1, pos[1] - 1),
                                   (pos[0] + figure_size[0] + 1,
                                    pos[1] + figure_size[1] + 1),
                                   (pos[0] - 1, pos[1] + figure_size[1] + 1)))))

            if lines[0]:
                for i in range(1, bar_size[0]):
                    instruction.append((pygame.draw.lines, (win, 0x888888, True, (
                        (math.floor(pos[0] + cell_size[0] * i), pos[1]),
                        (math.floor(pos[0] + cell_size[0] * i), pos[1] + figure_size[1])
                    ))))
                for i in range(1, bar_size[1]):
                    instruction.append((pygame.draw.lines, (win, 0x888888, True, (
                        (pos[0], math.floor(pos[1] + cell_size[1] * i)),
                        (pos[0] + figure_size[0], math.floor(pos[1] + cell_size[1] * i))))))

            if self.grid.is_mouse:
                instruction.append((pygame.draw.rect,
                                    (win, colorsRGBA[self.step % 2], ((pos[0] + cell_size[0], pos[1] + cell_size[1]), (
                                        cell_size[0] * (self.grid.mouse_figure_size[0]),
                                        cell_size[1] * (self.grid.mouse_figure_size[1]))))))

            return instruction

        return get_instr

    def show_end_msg(self):
        self.end_msg = True

        def go_to_menu():
            self.end_msg = False
            menu.gaming = False
            menu.start_new_game()

        restart_button = Button((200, 350), (200, 32), self.end_this_game_and_start_new, pygame.Color(255, 255, 255),
                                pygame.Color(0, 200, 0),
                                "Restart", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (70, 6))

        end_button = Button((350, 400), (200, 32), quit, pygame.Color(255, 255, 255), pygame.Color(200, 50, 50),
                            "Quit", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (40, 6))

        menu_button = Button((55, 400), (200, 32), go_to_menu, pygame.Color(255, 255, 255), pygame.Color(100, 100, 255),
                             "Back to menu", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (120, 6))

        end_window = ((20, 150), (555, 300))
        shadow = ((25, 155), (555, 300))

        title = 'The end'
        description = 'Thanks for play'

        end_title_font = pygame.font.SysFont("Gouranga Cyrillic", 32)
        end_desc_font = pygame.font.SysFont("Gouranga Cyrillic", 16)

        title_text = end_title_font.render(title, 1, pygame.Color(200, 200, 200), pygame.Color(88, 88, 88))
        des_text = end_desc_font.render(description, 1, pygame.Color(200, 200, 200), pygame.Color(88, 88, 88))

        instr = self.grid.get_main_draw()
        for i in instr:
            i[0](*i[1])
        pygame.display.update()

        while self.end_msg:
            pygame.draw.rect(win, pygame.Color(20, 20, 20), shadow)
            pygame.draw.rect(win, pygame.Color(88, 88, 88), end_window)

            win.blit(title_text, (60, 180))
            win.blit(des_text, (60, 220))
            # win.blit(end_description, (302,200))

            restart_button.draw()
            end_button.draw()
            menu_button.draw()

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                else:
                    pass
            self.clock.tick(self.fps)

    def plus1score(self, player_id):
        self.scores[player_id] += 1

    def draw_proto_figure(self):
        pass

    def score_text(self):
        myText = self.scores1.render(str(self.scores[0]), 1, colorsRGBA[0], pygame.Color(64, 64, 64))
        myText2 = self.scores2.render(str(self.scores[1]), 1, colorsRGBA[1], pygame.Color(64, 64, 64))

        if self.scores[0] >= self.scores[1]:
            self.scores1.set_bold(True)
        else:
            self.scores1.set_bold(False)

        if self.scores[0] <= self.scores[1]:
            self.scores2.set_bold(True)
        else:
            self.scores2.set_bold(False)

        win.blit(myText, (650, 50))
        win.blit(myText2, (650, 100))

    def keyboard(self):
        def esc():
            self.grid.change_mouse(absolute=(random.randint(1, 6), random.randint(1, 6)))
            self.step += 1
            self.get_current_player()

        def rotate():
            self.grid.change_mouse(absolute=(self.grid.mouse_figure_size[1], self.grid.mouse_figure_size[0]))

        def set_figure():
            self.grid.save_mouse_figure()

        key_binds = {pygame.K_ESCAPE: esc, pygame.K_r: rotate, pygame.K_F12: self.fill}
        mouse_binds = [set_figure, None, rotate]

        for key, func in key_binds.items():
            if self.current_player.get_keyboard()[key]:
                if not self.keys[key]:
                    func()
                    self.keys[key] = True
            else:
                self.keys[key] = False

        for button_id in range(len(mouse_binds)):
            if self.current_player.get_mouse_keys()[button_id]:
                if not self.mouse_keys[button_id]:
                    mouse_binds[button_id]()
                    self.mouse_keys[button_id] = True
            else:
                self.mouse_keys[button_id] = False

    def fill(self):
        self.grid.is_mouse = False

        def get_empty():
            _empty_cells = []
            for i in range(len(self.grid.raw_area)):
                for j in range(len(self.grid.raw_area[i])):
                    if self.grid.raw_area[i][j] == 0:
                        cell = (i, j)
                        sides = [0 if cell[0] == grid_size[0] - 1 else self.grid.raw_area[cell[0] + 1][cell[1]],
                                 0 if cell[0] == 0 else self.grid.raw_area[cell[0] - 1][cell[1]],
                                 0 if cell[1] == grid_size[1] - 1 else self.grid.raw_area[cell[0]][cell[1] + 1],
                                 0 if cell[1] == 0 else self.grid.raw_area[cell[0]][cell[1] - 1]]
                        if any(sides):
                            _empty_cells.append((i, j, sides))
            return _empty_cells

        empty_cells = get_empty()
        if empty_cells:
            while len(empty_cells) != 0:
                empty_cells_count = len(empty_cells)
                cell_id = random.randint(0, empty_cells_count - 1)
                cell = empty_cells[cell_id]
                global grid_size
                sides = [0 if cell[0] == grid_size[0] - 1 else self.grid.raw_area[cell[0] + 1][cell[1]],
                         0 if cell[0] == 0 else self.grid.raw_area[cell[0] - 1][cell[1]],
                         0 if cell[1] == grid_size[1] - 1 else self.grid.raw_area[cell[0]][cell[1] + 1],
                         0 if cell[1] == 0 else self.grid.raw_area[cell[0]][cell[1] - 1]]

                # sides = [random.randint(1,2),random.randint(1,2),random.randint(1,2),random.randint(1,2)]

                if any(sides):
                    players = [side for side in sides if side]
                    self.grid.area.append(Rectangle(colorsRGBA[players[0] - 1], cell, (1, 1)))
                    self.grid.raw_area[cell[0]][cell[1]] = players[0]
                    self.plus1score(players[0] - 1)

                    self.score_text()

                    instr = self.grid.get_main_draw()

                    for i in instr:
                        i[0](*i[1])

                    pygame.display.update()

                    empty_cells = get_empty()
                pygame.event.get()
            else:
                time.sleep(2)
        self.end_game = True
        self.play = False

    def end_this_game_and_start_new(self):
        self.play = False
        self.end_game = False
        self.end_msg = False
        menu.start_new_game()

    @staticmethod
    def gen_bg():

        def draw_bg():
            win.fill(0)
            pygame.draw.polygon(win, colorsRGBA[0], ((0, 0), (0, 600), (600, 0)))
            pygame.draw.polygon(win, colorsRGBA[1], ((600, 600), (0, 600), (600, 0)))
            pygame.draw.rect(win, 0, ((49, 49), (503, 503)))

            pygame.draw.rect(win, 0x404040, ((grid_widget_size[0] + grid_pos[0] * 2, 0), (800, 600)))

        return draw_bg


class MainMenu:
    fps = 60
    clock = pygame.time.Clock()

    def __init__(self, settings):
        self.setting = settings

    def mainloop(self):
        def show_online_menu():
            nonlocal showed_menu
            start_server_button = Button((240, 140), (200, 32), self.server_loop, pygame.Color(255, 255, 255),
                                         pygame.Color(0, 255, 0),
                                         "Start Server", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (105, 6))

            start_client_button = Button((460, 140), (200, 32), self.client_loop, pygame.Color(255, 255, 255),
                                         pygame.Color(0, 255, 0),
                                         "Start Client", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (105, 6))

            showed_menu = [start_server_button, start_client_button]

        def show_settings():
            nonlocal showed_menu
            showed_menu = []

        game_title_text = '"Area" the game'.upper()
        game_title_font = pygame.font.SysFont("Gouranga Cyrillic", 32)
        game_title = game_title_font.render(game_title_text, 1, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))

        play_offline_button = Button((20, 100), (200, 32), self.game_loop, pygame.Color(255, 255, 255),
                                     pygame.Color(0, 255, 0),
                                     "Play Offline", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (105, 6))

        play_online_button = Button((20, 140), (200, 32), show_online_menu, pygame.Color(255, 255, 255),
                                    pygame.Color(15, 192, 252),
                                    "Play Online", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (90, 6))

        setting_button = Button((20, 180), (200, 32), show_settings, pygame.Color(255, 255, 255),
                                pygame.Color(102, 221, 170),
                                "Settings", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (40, 6))

        quit_button = Button((20, 220), (200, 32), quit, pygame.Color(255, 255, 255), pygame.Color(255, 8, 0),
                             "Quit", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (-25, 6))

        buttons = [play_offline_button,
                   play_online_button,
                   setting_button,
                   quit_button]

        showed_menu = []

        while True:
            win.fill(0)
            win.blit(game_title, (300, 50))

            # pygame.draw.rect(win, pygame.Color(0, 0, 0), ((20, 100), (200, 40 * 3 + 32)))
            for button in buttons:
                button.draw()

            for item in showed_menu:
                if isinstance(item, Button):
                    item.draw()
                else:
                    item[0](*item[1], **item[2])

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                else:
                    pass

    def server_loop(self):
        connecting = True
        start_game = False

        def stop():
            nonlocal connecting
            connecting = False

        net_player = NetServer()

        abort_button = Button((580, 548), (200, 32), stop, pygame.Color(255, 255, 255), pygame.Color(255, 8, 0),
                              "Abort", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (-10, 6))

        accept_thread = threading.Thread(target=net_player.accept)

        font = pygame.font.SysFont("Gouranga Cyrillic", 32)
        time_div = 0
        time_div2 = 0

        accept_thread.start()
        while connecting:
            win.fill(0)

            if not net_player.connected:

                waiting_text = font.render(f"Waiting{'.' * (time_div // 60)}", 1, pygame.Color(255, 255, 255),
                                           pygame.Color(0, 0, 0))
                win.blit(waiting_text, (350, 278))
                abort_button.draw()
                time_div += 1

            else:
                waiting_text = font.render(f"Successful", 1, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))
                win.blit(waiting_text, (350, 278))
                time_div2 += 1
                if time_div2 >= 120:
                    connecting = False
                    start_game = True

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    connecting = False
                    break
                else:
                    pass

            if time_div >= 240:
                time_div = 0

            self.clock.tick(self.fps)
        else:
            if start_game:
                self.setting[0] = (Player(), net_player)
                net_player.working()
                self.game_loop()

    def client_loop(self):
        connecting = True

        def stop():
            nonlocal connecting
            connecting = False

        abort_button = Button((580, 548), (200, 32), stop, pygame.Color(255, 255, 255), pygame.Color(255, 8, 0),
                              "Abort", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (-10, 6))

        font = pygame.font.SysFont("Gouranga Cyrillic", 32)
        ip_font = pygame.font.SysFont("Gouranga Cyrillic", 32)
        ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        time_div = 0
        while connecting:
            win.fill(0)
            ip_text = ip_font.render(ip, 1, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))
            waiting_text = font.render(f"Connecting{'.' * (time_div // 60)}", 1, pygame.Color(255, 255, 255),
                                       pygame.Color(0, 0, 0))

            win.blit(waiting_text, (320, 278))
            win.blit(ip_text, (10, 569))

            abort_button.draw()

            time_div += 1
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    connecting = False
                    break
                else:
                    pass

            if time_div >= 240:
                time_div = 0

            self.clock.tick(self.fps)

    def game_loop(self):
        self.start_new_game()
        self.gaming = True

        while self.gaming:
            self.game.mainloop()

    def start_new_game(self):
        self.game = Game(*self.setting)


class Player:

    @staticmethod
    def get_mouse_pos():
        return pygame.mouse.get_pos()

    @staticmethod
    def get_keyboard():
        return pygame.key.get_pressed()

    @staticmethod
    def get_mouse_keys():
        return pygame.mouse.get_pressed()

    @staticmethod
    def get_mouse_focus():
        return pygame.mouse.get_focused()


class NetServer:
    connected = False
    work = False
    last_message = ''

    fps = 60
    clock = pygame.time.Clock()

    def __init__(self):
        self.sock = socket.socket()

    def accept(self):
        self.sock.bind(('', 9090))
        self.sock.listen(1)
        self.conn, addr = self.sock.accept()
        self.connected = True
        print('connected:', addr)

    def working(self):
        def data_tunnel(self):
            while self.working:
                data = self.conn.recv(1024 * 8)
                if data == b'quit':
                    self.stop()
                self.last_message = data.decode("utf-8")
                if pygame.key.get_pressed()[pygame.K_F11]:
                    print('\r' + str(data), end='')

        tunnel_thread = threading.Thread(target=data_tunnel, args=[self])
        tunnel_thread.start()

    def stop(self):
        self.conn.send(b'quit')

        self.conn.close()
        self.sock.close()

    def get_mouse_pos(self):
        return eval(self.last_message)['mouse'][0]

    def get_keyboard(self):
        return eval(self.last_message)['keyboard']

    def get_mouse_keys(self):
        return eval(self.last_message)['mouse'][1]

    def get_mouse_focus(self):
        return eval(self.last_message)['mouse'][2]


class NetClient:
    @staticmethod
    def get_mouse_pos():
        return pygame.mouse.get_pos()

    @staticmethod
    def get_keyboard():
        return pygame.key.get_pressed()

    @staticmethod
    def get_mouse_keys():
        return pygame.mouse.get_pressed()

    @staticmethod
    def get_mouse_focus():
        return pygame.mouse.get_focused()


def start_music():
    music_list = [r"Music\1.mp3", r"Music\2.mp3", r"Music\3.mp3", r"Music\4.mp3"]
    music_volume = [.2, .2, .2, .2]

    music_id = random.randint(0, 3)
    music_file = music_list[music_id]
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(music_volume[music_id])
    pygame.mixer.music.play(-1)


colorsRGBA = [pygame.Color(255, 160, 0, 1), pygame.Color(165, 45, 45, 1)]

grid_widget_size = (500, 500)
grid_size = (50, 50)
grid_pos = (50, 50)
lines = (False, True)
players = (Player(), Player())
max_figure_size = (6, 6)

settings = [players, grid_pos, grid_size, grid_widget_size, max_figure_size, colorsRGBA, *lines]

if __name__ == '__main__':
    menu = MainMenu(settings)
    start_music()
    while True:
        menu.mainloop()
