#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import random
import time
import socket
import threading
import sys
from ast import literal_eval

import pygame

# Идеи уменьшить шанс ввпадения еденичкии в начале игры
# Если добавим игру в стим, добавить достижение "Победидель по жизни", при выпении еденички в первом шаге

pygame.init()
pygame.font.init()


class SettingParameter:
    boxes = [pygame.image.load(r'Images/Settings menu/Checkbox/00.png'),
             pygame.image.load(r'Images/Settings menu/Checkbox/01.png')]

    hover = False

    def __init__(self, surface, pos, file, functions=(None, None), args=((), ()), state=False):
        self.surface = surface
        self.pos = pos
        self.image = pygame.image.load(file)
        self.fuctions = functions
        self.args = args
        self.state = state

    def draw(self):
        self.surface.blit(self.boxes[1 if self.state else 0], self.pos)
        self.surface.blit(self.image, self.pos)

    def check(self):
        mouse = pygame.mouse.get_pos()
        if True:
            if self.pos[0] < mouse[0] < self.pos[0] + 36 and self.pos[1] < mouse[1] < self.pos[1] + 36:
                self.hover = True
            else:
                self.hover = False

    def check_event(self, event):
        self.check()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            if self.fuctions[self.state] is not None:
                self.fuctions[self.state](self.args[self.state])

            self.state = not self.state


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
        return grid.get_figure_draw(self)

    def true_draw(self):
        pygame.draw.rect(win, 0xFFFFFF, (self.x1, self.y1, self.x2, self.y2))


class Button:
    hover = False
    pressed = False
    button_sound = pygame.mixer.Sound(r'Sounds/Effects/Button/Hover/03.wav')

    def __init__(self, pos1, pos2, target, color_reg, color_hov=None, text=None, text_color=None, font=None,
                 font_size=None, text_correct=(10, -2), args=(), texture=None):
        self.pos1 = pos1
        self.pos2 = pos2

        self.colors = (color_reg, color_hov if color_hov is not None else color_reg)
        self.target = target
        self.args = args

        if text is not None and text_color is not None and font is not None and font_size is not None:
            self.text_obj = pygame.font.SysFont(font, font_size)
            self.font_size = font_size
            self.text_color = text_color
            self.text_correct = text_correct

        self.text = text

        self.texture = texture

    def check_hover(self):
        mouse = pygame.mouse.get_pos()
        if (self.pos1[0] < mouse[0] < self.pos1[0] + self.pos2[0]) and (
                self.pos1[1] < mouse[1] < self.pos1[1] + self.pos2[1]):
            if sounds and not self.hover:
                self.button_sound.play()
            self.hover = True
        else:
            self.hover = False

    def get_draw(self):
        if self.texture is not None:
            return win.blit, (self.texture, self.pos1)

        elif self.text is not None:
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
            if pygame.mouse.get_pressed()[0]:
                if (self.pos1[0] < mouse[0] < self.pos1[0] + self.pos2[0]) and (
                        self.pos1[1] < mouse[1] < self.pos1[1] + self.pos2[1]) and not self.pressed:
                    self.target(*self.args)
                self.pressed = True
            else:
                self.pressed = False

    def checker(self):
        self.check_hover()
        self.check_click()

    def draw(self):
        self.checker()

        if self.texture is not None:
            if self.hover:
                return win.blit(self.texture, (self.pos1[0] - 5, self.pos1[1] - 5))
            else:
                return win.blit(self.texture, self.pos1)

        else:
            pygame.draw.rect(win, self.colors[self.hover], (self.pos1, self.pos2))
            button_text = self.text_obj.render(self.text, 1, self.text_color, self.colors[self.hover])

            win.blit(button_text, (
                math.floor(
                    self.pos1[0] + self.pos2[0] / 2 - len(self.text) * self.font_size / 2 + self.text_correct[0]),
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
        self.is_mouse = True

        self.inlines = inlines
        self.outlines = outlines

        self.area = []

        if lights:
            self.area_timers = []

        self.raw_area = [[0 for _ in range(grid_size[0])] for _ in range(grid_size[1])]

    def new_figure(self, figure: Rectangle, player_id):
        self.area.append(figure)
        self.area_timers.append(0)

        for x in range(figure.x1, figure.x1 + figure.x2):
            for y in range(figure.y1, figure.y1 + figure.y2):
                self.raw_area[x][y] = 1 + player_id

    def get_figure_draw(self, figure, *args):
        if isinstance(figure, Rectangle):
            x1 = figure.x1 * self.cell_size[0]
            y1 = figure.y1 * self.cell_size[1]
            size_x = figure.x2 * self.cell_size[0]
            size_y = figure.y2 * self.cell_size[1]
            if figure.x1 > -1 and figure.x1 + figure.x2 < self.column + 1:
                if figure.y1 > -1 and figure.y1 + figure.y2 < self.row + 1:
                    return [pygame.draw.rect, [
                        win, figure.color, (self.grid_pos[0] + math.floor(x1) + 1, math.floor(self.grid_pos[1] + y1),
                                            math.floor(size_x) + 1, math.floor(size_y) + 1)]]

    def get_figure_draw_by_id(self, id):
        draw = self.get_figure_draw(self.area[id])
        if lights:
            div = draw[1][1].r, draw[1][1].g, draw[1][1].b
            draw[1][1] = tuple(
                (math.floor(draw[1][1][c] - div[c] * (1 - self.area_timers[id] / 30)) for c in range(3))) if \
                self.area_timers[id] < 30 else draw[1][1]
        return draw

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

        for figure_id in range(len(self.area)):
            figure = self.area[figure_id]
            draw = self.get_figure_draw_by_id(figure_id)
            if draw is not None:
                if figure.color == colorsRGBA[0]:
                    instructions[0].append(draw)
                elif figure.color == colorsRGBA[1]:
                    instructions[1].append(draw)
                else:
                    instructions[0].append(draw)

        if lights:
            for figure in range(len(self.area_timers)):
                self.area_timers[figure] += 1

        for sub in instructions[0]:
            instruction.append(sub)

        for sub in instructions[1]:
            instruction.append(sub)

        if self.is_mouse:
            if ghosts:
                if menu.game.current_player.can_draw():
                    mouse_object_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
                    figure = self.get_figure_draw(menu.game.current_player.get_figure())[1]
                    figure[0] = mouse_object_surface
                    figure[1] = pygame.Color(200, 200, 200, 150)

                    pygame.draw.rect(*figure)
                    instruction.append((mouse_object_surface, (0, 0)))

            else:
                if menu.game.current_player.can_draw():
                    inst = instruction.append(menu.game.current_player.get_figure().draw(self))
                    if inst is not None:
                        instruction.append(inst)

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


def quit():
    sys.exit()


class Game:
    alone_one = True
    play = True
    end_game = False
    can_continue = False

    fps = 60
    clock = pygame.time.Clock()

    def __init__(self, players, grid_pos, grid_size, gws, max_sizes, player_colors, inlines, outlines):
        self.step = 0

        self.is_first_player_step = True
        self.grid = Grid_of_game(grid_pos, gws, grid_size, inlines, outlines)

        self.grid_size = grid_size

        self.grid.area = [Rectangle(player_colors[0], (0, 0), (1, 1)),
                          Rectangle(player_colors[1], (self.grid.column - 1, self.grid.row - 1), (1, 1))]

        self.grid.raw_area[0][0] = 1
        self.grid.raw_area[self.grid.column - 1][self.grid.row - 1] = 2

        self.grid.area_timers = [0, 0]

        self.max_sizes = max_sizes

        self.player_colors = player_colors

        self.scores = [1, 1]

        self.players = tuple(
            (players[player_i](self.grid, self, self.player_colors[player_i], player_i, max_sizes) for player_i in
             range(len(players))))

        self.current_player = self.players[self.step % 2]
        self.scores1 = pygame.font.SysFont("Gouranga Cyrillic", 32)

        self.scores2 = pygame.font.SysFont("Gouranga Cyrillic", 32)

    def get_current_player(self):
        self.current_player = self.players[self.step % 2]

    def mainloop(self):
        self.back = self.gen_bg()
        click_delay = 20
        can_click = False

        self.can_continue = False

        self.get_current_player()

        while self.play:
            self.back()

            self.current_player.check()

            self.score_text()

            if can_click:
                pass
                # self.keyboard()
            else:
                if click_delay > 0:
                    click_delay -= 1
                else:
                    can_click = True

            if not self.end_game:

                instr = self.grid.get_main_draw()
                instr += self.status_bar((620, 390), (160, 160), (True, True))

                for i in instr:
                    if i is not None:
                        if isinstance(i[0], pygame.Surface):
                            win.blit(i[0], i[1])
                        else:
                            i[0](*i[1])

                pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.play = False
                    self.can_continue = True
                    break

                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.play = False
                        self.can_continue = True
                        break

                    else:
                        self.current_player.keyboard(event)

            self.clock.tick(self.fps)

        self.show_end_msg()

    def set_mouse_figure(self, figure):
        self.grid.new_figure(figure, self.step % 2)
        self.scores[self.step % 2] += figure.y2 * figure.x2
        self.step += 1
        self.get_current_player()

    def status_bar(self, pos, figure_size, lines):
        bar_size = list((ci + 2 for ci in self.max_sizes))
        cell_size = list((figure_size[ci] / bar_size[ci] for ci in range(2)))

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

        figure = menu.game.current_player.get_figure()

        instruction.append((pygame.draw.rect, (win, figure.color,
                                               ((round(pos[0] + cell_size[0]), round(pos[1] + cell_size[1])),
                                                (round(figure.x2 * cell_size[0]), round(figure.y2 * cell_size[1]))))))

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

        return instruction

    def show_end_msg(self):
        self.end_msg = True

        def continue_game():
            self.play = True
            self.end_msg = False

        def go_to_menu():
            self.end_msg = False
            menu.gaming = False
            if isinstance(self, NetGame):
                self.terminal.send('quit')

        def over():
            if isinstance(self, NetGame):
                self.terminal.send('quit')

            quit()

        restart_button = Button((350, 350), (200, 32),
                                self.end_this_game_and_start_new, pygame.Color(255, 255, 255),
                                pygame.Color(0, 200, 0),
                                "Restart", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (70, 6),
                                texture=pygame.image.load(r'Images/End message/Restart.png'))

        end_button = Button((350, 400), (200, 32), over, pygame.Color(255, 255, 255), pygame.Color(200, 50, 50),
                            "Quit", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (40, 6),
                            texture=pygame.image.load(r'Images/End message/Quit.png'))

        menu_button = Button((55, 400), (200, 32), go_to_menu, pygame.Color(255, 255, 255), pygame.Color(100, 100, 255),
                             "Back to menu", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (120, 6),
                             texture=pygame.image.load(r'Images/End message/Back.png'))

        continue_button = Button((55, 350), (200, 32), continue_game, pygame.Color(255, 255, 255),
                                 pygame.Color(0, 200, 0),
                                 "Continue", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (70, 6),
                                 texture=pygame.image.load(r'Images/End message/Continue.png'))

        instr = self.grid.get_main_draw()

        for i in instr:
            if i is not None:
                if isinstance(i[0], pygame.Surface):
                    win.blit(i[0], i[1])
                else:
                    i[0](*i[1])

        pygame.display.update()

        if self.can_continue:
            end_background = pygame.image.load(r'Images/End message/Background2.png')
        else:
            end_background = pygame.image.load(r'Images/End message/Background.png')

        while self.end_msg:
            win.blit(end_background, (20, 150))

            if self.can_continue:
                continue_button.draw()

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

    def fill(self):
        self.grid.is_mouse = False

        def get_empty():
            _empty_cells = []
            for i in range(len(self.grid.raw_area)):
                for j in range(len(self.grid.raw_area[i])):
                    if self.grid.raw_area[i][j] == 0:
                        cell = (i, j)
                        sides = [0 if cell[0] == self.grid_size[0] - 1 else self.grid.raw_area[cell[0] + 1][cell[1]],
                                 0 if cell[0] == 0 else self.grid.raw_area[cell[0] - 1][cell[1]],
                                 0 if cell[1] == self.grid_size[1] - 1 else self.grid.raw_area[cell[0]][cell[1] + 1],
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
                sides = [0 if cell[0] == self.grid_size[0] - 1 else self.grid.raw_area[cell[0] + 1][cell[1]],
                         0 if cell[0] == 0 else self.grid.raw_area[cell[0] - 1][cell[1]],
                         0 if cell[1] == self.grid_size[1] - 1 else self.grid.raw_area[cell[0]][cell[1] + 1],
                         0 if cell[1] == 0 else self.grid.raw_area[cell[0]][cell[1] - 1]]

                # sides = [random.randint(ignored,2),random.randint(ignored,2),random.randint(ignored,2),random.randint(ignored,2)]

                if any(sides):
                    players = [side for side in sides if side]
                    self.grid.area.append(Rectangle(colorsRGBA[players[0] - 1], cell, (1, 1)))
                    self.grid.raw_area[cell[0]][cell[1]] = players[0]
                    self.grid.area_timers.append(0)
                    self.plus1score(players[0] - 1)

                    self.back()
                    self.score_text()

                    instr = self.grid.get_main_draw()
                    instr += self.status_bar((620, 390), (160, 160), (True, True))

                    for i in instr:
                        i[0](*i[1])

                    pygame.display.update()

                    empty_cells = get_empty()
                pygame.event.get()
            else:
                t = 0
                while t < 120:
                    self.back()
                    self.score_text()

                    instr = self.grid.get_main_draw()
                    instr += self.status_bar((620, 390), (160, 160), (True, True))

                    for i in instr:
                        i[0](*i[1])

                    pygame.display.update()
                    t += 1
                    self.clock.tick(self.fps)

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


class ServerTerminal:
    work = True
    queue = []

    def __init__(self, settings=None):
        self.sock = socket.socket()
        self.sock.setblocking(False)

        self.bind()

        self.settings = settings

    def bind(self):
        if not isinstance(self, ClientTerminal):
            self.sock.bind(('', IP[1]))
            self.sock.listen(1)

    def send(self, message):
        self.conn.send(message.encode('utf-8'))

    def accept(self, target=None):
        try:
            self.conn, address = self.sock.accept()

        except socket.error:
            pass

        else:
            print('connected:', address)
            if target is not None:
                target()

            if self.settings is not None:
                self.send(str(self.settings))

    def receive(self):
        try:
            rcv_data = self.conn.recv(1024)
            a = rcv_data
            b = a.decode('utf-8')
            c = b.split(';')
            self.queue.extend(c)

        except (ConnectionAbortedError, ConnectionResetError):
            self.sock.close()

        except socket.error:
            pass

    def get_queue(self):
        if self.queue:
            copy = self.queue.copy()
            self.queue = []
            return copy

        else:
            return []

    def close(self):
        self.sock.close()
        self.conn.close()


class ClientTerminal(ServerTerminal):
    server_settings = {}
    connecting_state = False

    def connect(self, target_connected=None, target_not=None, ip=('localhost', 9090)):
        try:
            self.sock.setblocking(True)
            print(ip)
            self.sock.connect(ip)
        except (ConnectionRefusedError, TimeoutError):
            if target_not is not None:
                target_not()

        # except socket.error:
        #     pass

        else:
            self.server_settings = literal_eval(self.sock.recv(1024 * 4).decode('utf-8'))
            self.sock.setblocking(False)
            if target_connected is not None:
                target_connected()
                self.connecting_state = False

    def connecting(self, target_connected=None, target_not=None):
        if not self.connecting_state:
            self.connecting_state = True
            connect_thread = threading.Thread(target=self.connect, args=(target_connected, target_not, IP))
            connect_thread.start()

    def send(self, message):
        self.sock.send(message.encode('utf-8'))

    def receive(self):
        try:
            rcv_data = self.sock.recv(1024)
            self.queue.extend(rcv_data.decode('utf-8').split(';'))
        except (ConnectionAbortedError, ConnectionResetError):
            if self.work:
                quit()

        except socket.error:
            pass

    def close(self):
        self.sock.close()


class NetGame(Game):
    enemy_figure_size = [3, 3]

    def __init__(self, terminal, place, players, grid_pos, grid_size, gws, max_sizes, player_colors, inlines, outlines):
        self.terminal = terminal

        if isinstance(terminal, ClientTerminal):
            new_setting = self.terminal.server_settings
            Player.alone_figure = new_setting['alone_figures']

            super().__init__(players, grid_pos, new_setting['grid_size'], gws, new_setting['max_figure_size'],
                             player_colors, inlines, outlines)
        else:
            super().__init__(players, grid_pos, grid_size, gws, max_sizes, player_colors, inlines, outlines)

        self.place = place

        self.players[not place].lock()
        self.players[place].unlock()

    def encode_message(self, message):
        splinted = message.split(' ')

        if splinted[0] == 'new_figure':
            self.set_mouse_figure(Rectangle(self.player_colors[self.step % 2],
                                            (int(splinted[1]), int(splinted[2])),
                                            (int(splinted[3]), int(splinted[4]))), True)

        elif splinted[0] == 'rotate':
            self.enemy_figure_size[0], self.enemy_figure_size[1] = self.enemy_figure_size[1], self.enemy_figure_size[0]

        elif splinted[0] == 'quit':
            self.can_continue = False
            self.play = False

        elif splinted[0] == 'new_step':
            self.enemy_figure_size = [int(splinted[1]), int(splinted[2])]

        elif splinted[0] == 'fill':
            self.fill(True)

        elif splinted[0] == 'skip':
            self.step += 1
            self.get_current_player()

    def get_current_player(self):
        self.current_player = self.players[self.step % 2]

    def mainloop(self):
        self.back = self.gen_bg()
        quit_ = False
        click_delay = 20
        can_click = False

        self.get_current_player()

        while self.play:

            self.terminal.receive()

            for message in self.terminal.get_queue():
                if message:
                    # print(message)
                    self.encode_message(message)

            self.back()

            self.current_player.check()

            self.score_text()

            if can_click:
                pass
                # self.keyboard()
            else:
                if click_delay > 0:
                    click_delay -= 1
                else:
                    can_click = True

            if not self.end_game:

                instr = self.grid.get_main_draw()
                instr += self.status_bar((620, 390), (160, 160), (True, True))

                for i in instr:
                    if i is not None:
                        if isinstance(i[0], pygame.Surface):
                            win.blit(i[0], i[1])
                        else:
                            i[0](*i[1])

                pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.play = False
                    self.can_continue = True
                    break

                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.play = False
                        self.can_continue = True
                        break

                    else:
                        if not self.current_player.locked:
                            self.current_player.keyboard(event)

            if quit_:
                break

            self.clock.tick(self.fps)

        self.show_end_msg()

    def status_bar(self, pos, figure_size, lines):
        bar_size = list((ci + 2 for ci in self.max_sizes))
        cell_size = list((figure_size[ci] / bar_size[ci] for ci in range(2)))

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

        if not self.current_player.locked:
            figure = self.current_player.get_figure()
        else:
            figure = Rectangle(self.current_player.color, (0, 0), self.enemy_figure_size)

        instruction.append((pygame.draw.rect, (win, figure.color,
                                               ((round(pos[0] + cell_size[0]), round(pos[1] + cell_size[1])),
                                                (round(figure.x2 * cell_size[0]), round(figure.y2 * cell_size[1]))))))

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

        return instruction

    def end_this_game_and_start_new(self):
        self.terminal.work = False

        if isinstance(self.terminal, ClientTerminal):
            menu.mainloop()
        else:
            menu.server_loop()
            menu.mainloop()

    def set_mouse_figure(self, figure, is_net=False):
        super().set_mouse_figure(figure)
        if not is_net:
            self.terminal.send(f'new_figure {figure.x1} {figure.y1} {figure.x2} {figure.y2};')

    def fill(self, is_net=False):
        if not is_net:
            self.terminal.send('fill')
        super().fill()


class MainMenu:
    fps = 60
    clock = pygame.time.Clock()

    terminals = []

    def __init__(self, settings):
        self.setting = settings

    def mainloop(self):
        def show_online_menu():
            nonlocal terminal
            nonlocal showed_menu
            start_server_button = Button((240, 140), (200, 32), self.server_loop, pygame.Color(255, 255, 255),
                                         pygame.Color(0, 255, 0),
                                         "Start Server", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (105, 6),
                                         texture=pygame.image.load("Images/Menu/Start server.png"))

            start_client_button = Button((460, 140), (200, 32), terminal.connecting, pygame.Color(255, 255, 255),
                                         pygame.Color(0, 255, 0),
                                         "Start Client", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (105, 6),
                                         args=[start, fail],
                                         texture=pygame.image.load("Images/Menu/Connect.png"))

            showed_menu = [start_server_button, start_client_button]

        play_offline_button = Button((20, 100), (200, 32), self.game_loop, pygame.Color(255, 255, 255),
                                     texture=pygame.image.load("Images/Menu/Play offline.png"))

        play_online_button = Button((20, 140), (200, 32), show_online_menu, pygame.Color(255, 255, 255),
                                    texture=pygame.image.load("Images/Menu/Play online.png"))

        setting_button = Button((20, 180), (200, 32), self.settings_loop, pygame.Color(255, 255, 255),
                                texture=pygame.image.load("Images/Menu/Settings.png"))

        quit_button = Button((20, 220), (200, 32), quit, pygame.Color(255, 255, 255),
                             texture=pygame.image.load("Images/Menu/Quit.png"))

        buttons = [play_offline_button,
                   play_online_button,
                   setting_button,
                   quit_button]

        showed_menu = []

        back = pygame.image.load(r"Images/main/Background.png")

        terminal = ClientTerminal()

        def start():
            nonlocal indicator
            indicator = 600

        def fail():
            nonlocal indicator
            indicator = 300

        indicator = -1  # 0..60 - connecting, 300...420-fail, 600..720 - success

        fine_image = pygame.image.load(r'Images/Text/Area server waiting/Successful.png')
        fail_image = pygame.image.load(r'Images/Text/Area server waiting/Fail.png')

        while True:

            win.blit(back, (0, 0))

            for button in buttons:
                button.draw()

            for item in showed_menu:
                if isinstance(item, (Button, SettingParameter)):
                    item.draw()

            if indicator >= 0:

                indicator += 1

                if 0 <= indicator <= 60:
                    pygame.draw.rect(win, pygame.Color(0, 0, 200), ((500, 125), (100, 100)))

                elif 300 <= indicator <= 420:
                    win.blit(fail_image, (500, 125))

                elif 600 <= indicator <= 720:
                    win.blit(fine_image, (500, 125))

                    if indicator == 720:
                        self.net_game_loop(terminal, 2)
                        terminal = ClientTerminal()

                        showed_menu[1] = Button((460, 140), (200, 32), terminal.connecting,
                                                pygame.Color(255, 255, 255),
                                                pygame.Color(0, 255, 0),
                                                "Start Client", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32,
                                                (105, 6),
                                                args=[start, fail],
                                                texture=pygame.image.load("Images/Menu/Connect.png"))


                else:
                    indicator = -1

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:

                    quit()

                else:
                    pass

            self.clock.tick(self.fps)

    def server_loop(self):
        connecting = True
        start_game = False

        def stop():
            nonlocal connecting
            connecting = False

        def successful():
            nonlocal connecting
            nonlocal start_game
            connecting = False
            start_game = True

        terminal = ServerTerminal({'grid_size': self.setting[2],
                                   'max_figure_size': self.setting[4],
                                   'alone_figures': self.setting[8]})

        game_info_font = pygame.font.SysFont("Myriad Pro", 24)
        texts = [game_info_font.render(IP[0], 1, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0)),
                 game_info_font.render(str(IP[1]), 1, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0)),
                 game_info_font.render('192.168.0.248', 1, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))]

        abort_button = Button((575, 545), (200, 32), stop, pygame.Color(255, 255, 255),
                              texture=pygame.image.load("Images/Menu/Stop.png"))

        t = 0

        back = pygame.image.load("Images/main/Background server.png")
        waiting_list = [pygame.image.load("Images/Text/Area server waiting/01.png"),
                        pygame.image.load("Images/Text/Area server waiting/02.png"),
                        pygame.image.load("Images/Text/Area server waiting/03.png"),
                        pygame.image.load("Images/Text/Area server waiting/Successful.png")]

        while True:

            terminal.accept(target=successful)

            win.blit(back, (0, 0))
            win.blit(texts[0], (120, 525))
            win.blit(texts[1], (78, 553))
            win.blit(texts[2], (144, 499))

            if not start_game:
                win.blit(waiting_list[t // 30], (350 - 10, 300 - 54))
            else:
                win.blit(waiting_list[3], (350, 280))

            if t < 180 // 2 - 1:
                t += 1
            else:
                t = 0

            abort_button.draw()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            if start_game:
                break

            if not connecting:
                break

            self.clock.tick(self.fps)

        if start_game:
            time.sleep(2)

            self.net_game_loop(terminal, 1)

    def settings_loop(self):
        def exit_settings():
            save()
            nonlocal show_settings
            show_settings = False

        show_settings = True

        global alone_figures
        global lines
        global ghosts
        global play_logo
        global play_music
        global sounds
        global lights

        textures = {r"Images/Settings menu/Buttons/Alone.png": [alone_figures],
                    r"Images/Settings menu/Buttons/Ghosts.png": [ghosts],
                    r"Images/Settings menu/Buttons/internal lines.png": [lines[0]],
                    r"Images/Settings menu/Buttons/Intro.png": [play_logo],
                    r"Images/Settings menu/Buttons/Music.png": [play_music],
                    r"Images/Settings menu/Buttons/Sounds.png": [sounds],
                    r"Images/Settings menu/Buttons/Lights.png": [lights]}

        buttons = []

        i = 0
        for texture, data in textures.items():
            buttons.append(SettingParameter(win, (20, 100 + 50 * i), texture, state=data[0]))
            i += 1

        def save():
            global alone_figures
            global lines
            global ghosts
            global play_logo
            global play_music
            global sounds
            global lights

            ms = play_music

            nonlocal buttons
            mb = buttons[:-1]

            alone_figures = mb[0].state
            lines = (mb[2].state, True)
            ghosts = mb[1].state
            play_logo = mb[3].state
            play_music = mb[4].state
            sounds = mb[5].state
            lights = mb[6].state

            if play_music:
                if not ms:
                    start_music()
            else:
                pygame.mixer.music.stop()

            settings_data = {'intro': play_logo,
                             'music': play_music,
                             'ghosts': ghosts,
                             'lights': lights,
                             'sounds': sounds,
                             "grid_size": grid_size[0],
                             "lines": lines,
                             "max_figure_size": max_figure_size[0],
                             "alone_figures": alone_figures,
                             'colorsRGBA': colorsRGBA}

            settings_file = open('settings.txt', 'w', encoding='utf-8')
            settings_file.write(str(settings_data))
            settings_file.close()

            self.__init__(
                [players, grid_pos, grid_size, grid_widget_size, max_figure_size, colorsRGBA, *lines, alone_figures])

        save_button = Button((20, 545), (200, 32), exit_settings, pygame.Color(255, 255, 255),
                             texture=pygame.image.load("Images/Settings menu/Buttons/Save.png"))

        buttons.append(save_button)

        back = pygame.image.load(r"Images/Settings menu/Settings back.png")
        over = pygame.image.load(r"Images/Settings menu/Settings over.png")
        t = 0
        while show_settings:
            win.blit(back, (-1600 + math.floor(t), 0))
            win.blit(over, (0, 0))

            for button in buttons:
                button.draw()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:

                    quit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for line in buttons:
                        if isinstance(line, SettingParameter):
                            line.check_event(event)

                else:
                    pass

            t = (t + .5) % 1100

            self.clock.tick(self.fps)

    def net_game_loop(self, terminal, type_of_game):
        self.start_new_game(type_of_game=type_of_game, terminal=terminal)
        self.gaming = True
        while self.gaming:
            self.game.mainloop()

        for i in self.terminals:
            i.close()

        self.terminals = []

    def game_loop(self):
        self.start_new_game()
        self.gaming = True

        while self.gaming:
            self.game.mainloop()

    def start_new_game(self, type_of_game=0, terminal=None):

        Player.alone_figure = self.setting[8]

        if type_of_game == 0:
            self.setting[0] = (Player, Player)
            self.game = Game(*self.setting[:-1])

        elif type_of_game == 1:
            self.setting[0] = (NetPlayer, NetPlayer)
            self.game = NetGame(terminal, 0, *self.setting[:-1])
            self.terminals.append(terminal)

        elif type_of_game == 2:
            self.setting[0] = (NetPlayer, NetPlayer)
            self.game = NetGame(terminal, 1, *self.setting[:-1])
            self.terminals.append(terminal)


class Player:
    alone_figure = True

    def __init__(self, grid: Grid_of_game, game, color, me_id, max_sizes):
        self.grid_data = (grid.grid_pos, grid.grid_size, grid.cell_size)
        self.grid = grid
        self.game = game

        self.max_sizes = max_sizes

        self.color = color

        self.me_id = me_id

        self.figure_size = [random.randint(1, self.max_sizes[0]),
                            random.randint(1, self.max_sizes[1])]

        self.mouse_figure = [self.get_in_grid_pos(), self.figure_size]

    def keyboard(self, event):
        def skip_turn():
            self.game.step += 1
            self.game.get_current_player()
            self.mouse_figure = [self.get_in_grid_pos(), self.figure_size]
            self.new_step()

        key_binds = {pygame.K_SPACE: skip_turn,
                     pygame.K_r: self.rotate,
                     pygame.K_F12: self.game.fill
                     }

        mouse_binds = [None,
                       self.set,
                       None,
                       self.rotate,
                       None,
                       None,
                       None,
                       None]

        # print(event.button)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mouse_binds[event.button] is not None:
                mouse_binds[event.button]()

        elif event.type == pygame.KEYDOWN:
            if event.key in key_binds:
                key_binds[event.key]()

    def set(self):
        if self.can_set():
            self.game.set_mouse_figure(self.get_figure())
            self.new_step()

    def can_set(self):

        in_pos = self.get_in_grid_pos()

        if self.can_draw():
            for x in range(in_pos[0], in_pos[0] + self.figure_size[0]):
                for y in range(in_pos[1], in_pos[1] + self.figure_size[1]):
                    if self.grid.raw_area[x][y] != 0:
                        return False

            if self.alone_figure and self.figure_size == [1, 1]:
                return True

            try:
                y = in_pos[1] - 1
                for x in range(in_pos[0], in_pos[0] + self.figure_size[0]):
                    if self.grid.raw_area[x][y] == self.me_id + 1:
                        return True
            except IndexError:
                pass

            try:
                y = in_pos[1] + self.figure_size[1]
                for x in range(in_pos[0], in_pos[0] + self.figure_size[0]):
                    if self.grid.raw_area[x][y] == self.me_id + 1:
                        return True
            except IndexError:
                pass

            try:
                x = in_pos[0] - 1
                for y in range(in_pos[1], in_pos[1] + self.figure_size[1]):
                    if self.grid.raw_area[x][y] == self.me_id + 1:
                        return True
            except IndexError:
                pass

            try:
                x = in_pos[0] + self.figure_size[0]
                for y in range(in_pos[1], in_pos[1] + self.figure_size[1]):
                    if self.grid.raw_area[x][y] == self.me_id + 1:
                        return True
            except IndexError:
                pass

            return False

        else:
            return False

    def can_draw(self):
        in_pos = self.get_in_grid_pos()

        if in_pos[0] >= 0 and in_pos[1] >= 0 and \
                in_pos[0] + self.figure_size[0] < self.grid_data[1][0] + 1 \
                and in_pos[1] + self.figure_size[1] < self.grid_data[1][1] + 1:
            return True

        else:
            return False

    def get_in_grid_pos(self):
        mouse = pygame.mouse.get_pos()
        a = [math.floor((mouse[0] - self.grid_data[0][0]) // self.grid_data[2][0]),
             math.floor((mouse[1] - self.grid_data[0][1]) // self.grid_data[2][1])]
        return a

    def get_figure(self):
        return Rectangle(self.color, *self.mouse_figure)

    def rotate(self):
        self.figure_size[0], self.figure_size[1] = self.figure_size[1], self.figure_size[0]

    def new_step(self):
        self.figure_size = [random.randint(1, self.max_sizes[0]),
                            random.randint(1, self.max_sizes[1])]
        self.update()

    def update(self):
        self.mouse_figure = [self.get_in_grid_pos(), self.figure_size]

    def check(self):
        if self.mouse_figure[0] != self.get_in_grid_pos():
            self.update()


class NetPlayer(Player):
    locked = False

    def __init__(self, grid: Grid_of_game, game: NetGame, color, me_id, max_sizes):
        super().__init__(grid, game, color, me_id, max_sizes)

    def keyboard(self, event):
        def skip_turn():
            self.game.terminal.send('skip;')
            self.game.step += 1
            self.game.get_current_player()
            self.mouse_figure = [self.get_in_grid_pos(), self.figure_size]
            self.new_step()

        key_binds = {pygame.K_SPACE: skip_turn,
                     pygame.K_r: self.rotate,
                     pygame.K_F12: self.game.fill
                     }

        mouse_binds = [None,
                       self.set,
                       None,
                       self.rotate,
                       None,
                       None,
                       None,
                       None]

        # print(event.button)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mouse_binds[event.button] is not None:
                mouse_binds[event.button]()

        elif event.type == pygame.KEYDOWN:
            if event.key in key_binds:
                key_binds[event.key]()

    def can_draw(self):
        in_pos = self.get_in_grid_pos()

        if in_pos[0] >= 0 and in_pos[1] >= 0 and \
                in_pos[0] + self.figure_size[0] < self.grid_data[1][0] + 1 \
                and in_pos[1] + self.figure_size[1] < self.grid_data[1][1] + 1 \
                and not self.locked:
            return True

        else:
            return False

    def rotate(self):
        super().rotate()
        self.game.terminal.send('rotate;')

    def new_step(self):
        super().new_step()
        self.game.terminal.send(f'new_step {self.figure_size[0]} {self.figure_size[1]};')

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False
        self.game.terminal.send(f'new_step {self.figure_size[0]} {self.figure_size[1]};')


def start_music():
    music_list = ['1.mp3', '2.mp3', '3.mp3', '4.mp3']
    music_volume = [.2, .2, .2, .2]

    music_id = random.randint(0, 3)
    music_file = 'Sounds/Music/' + music_list[music_id]
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(music_volume[music_id])
    pygame.mixer.music.play(-1)


if __name__ == '__main__':

    try:
        ip_file = open('IP.txt', 'r')
        IP = literal_eval(ip_file.read())
        ip_file.close()
    except FileNotFoundError:
        IP = ('localhost', 9090)
        print('Ошибка при чтенни файла. Использованно значение поумолчанию.')

        ip_file = open('IP.txt', 'w')
        ip_file.write(str(IP))
        ip_file.close()

    win = pygame.display.set_mode((800, 600))  # размеры X и Y
    try:
        pygame.display.set_icon(pygame.image.load("Images/main/ico.png"))
    except pygame.error:
        pass
    pygame.display.set_caption("Area")

    grid_widget_size = (500, 500)
    grid_pos = (50, 50)
    players = ()

    try:
        settings_file = open('settings.txt', 'r', encoding='utf-8')
        settings_data = literal_eval(settings_file.read())
        settings_file.close()

    except FileNotFoundError:
        grid_size = (40, 40)
        lines = (False, True)
        max_figure_size = (6, 6)
        alone_figures = True
        colorsRGBA = [pygame.Color(255, 160, 0, 1), pygame.Color(165, 45, 45, 1)]
        play_music = True
        ghosts = True
        lights = True
        sounds = True

        def_settings = {'music': True,
                        'ghosts': True,
                        'lights': True,
                        'sounds': True,
                        "grid_size": 40,
                        "lines": (False, True),
                        "max_figure_size": 6,
                        "alone_figures": True,
                        'colorsRGBA': ((255, 160, 0, 1), (165, 45, 45, 1))}

        settings_file = open('settings.txt', 'w', encoding='utf-8')
        settings_file.write(str(def_settings))
        settings_file.close()

    else:
        ghosts = settings_data['ghosts']
        grid_size = [settings_data['grid_size'], settings_data['grid_size']]
        lines = settings_data['lines']
        max_figure_size = (settings_data['max_figure_size'], settings_data['max_figure_size'])
        alone_figures = settings_data['alone_figures']
        colorsRGBA = [pygame.Color(*settings_data['colorsRGBA'][0]), pygame.Color(*settings_data['colorsRGBA'][1])]
        lights = settings_data['lights']
        play_music = settings_data['music']
        sounds = settings_data['sounds']

    settings = [players, grid_pos, grid_size, grid_widget_size, max_figure_size, colorsRGBA, *lines, alone_figures]

    menu = MainMenu(settings)

    if play_music:
        start_music()

    while True:
        menu.mainloop()
