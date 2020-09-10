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

pygame.init()
pygame.font.init()

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

n = 0


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

    def __init__(self, pos1, pos2, target, color_reg, color_hov=None, text=None, text_color=None, font=None,
                 font_size=None, text_correct=(10, -2), args=()):
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
                    self.target(*self.args)

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
        self.is_mouse = True

        self.inlines = inlines
        self.outlines = outlines

        self.area = []
        self.raw_area = [[0 for _ in range(grid_size[0])] for _ in range(grid_size[1])]

    def new_figure(self, figure: Rectangle, player_id):
        self.area.append(figure)

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

    fps = 60
    clock = pygame.time.Clock()

    def __init__(self, players, grid_pos, grid_size, gws, max_sizes, player_colors, inlines, outlines):
        self.step = 0

        self.is_first_player_step = True
        self.grid = Grid_of_game(grid_pos, gws, grid_size, inlines, outlines)

        self.grid.area = [Rectangle(player_colors[0], (0, 0), (1, 1)),
                          Rectangle(player_colors[1], (self.grid.column - 1, self.grid.row - 1), (1, 1))]

        self.grid.raw_area[0][0] = 1
        self.grid.raw_area[self.grid.column - 1][self.grid.row - 1] = 2

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
        quit_ = False
        click_delay = 20
        can_click = False

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
                        i[0](*i[1])

                pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.play = False
                    quit_ = True
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    self.current_player.keyboard(event)

            if quit_:
                break

            self.clock.tick(self.fps)

        else:
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

        def go_to_menu():
            self.end_msg = False
            menu.gaming = False
            menu.start_new_game()

        def orevuar():
            pygame.quit()
            quit()

        restart_button = Button((200, 350), (200, 32), self.end_this_game_and_start_new, pygame.Color(255, 255, 255),
                                pygame.Color(0, 200, 0),
                                "Restart", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (70, 6))

        end_button = Button((350, 400), (200, 32), orevuar, pygame.Color(255, 255, 255), pygame.Color(200, 50, 50),
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


class ServerTerminal:
    work = True
    queue = []

    def __init__(self, settings=None):
        self.sock = socket.socket()
        self.settings = settings

    def send(self, message):
        self.conn.send(message.encode('utf-8'))

    def accept(self, target=None):
        self.sock.bind(('', IP[1]))
        self.sock.listen(1)
        self.conn, addr = self.sock.accept()
        print('connected:', addr)
        if target is not None:
            target()

        if self.settings is not None:
            self.send(str(self.settings))

    def accepting(self, target):
        accept_thread = threading.Thread(target=self.accept, args=[target])
        accept_thread.start()

    def receiving(self):
        while self.work:
            try:
                rcv_data = self.conn.recv(1024 * 4)
                a = rcv_data
                b = a.decode('utf-8')
                c = b.split(';')
                self.queue.extend(c)
            except (ConnectionAbortedError, ConnectionResetError):
                if self.work:
                    quit()

    def start_recv(self):
        self.queue = []
        thread = threading.Thread(target=self.receiving)
        thread.start()

    def get_queue(self):
        if self.queue:
            copy = self.queue.copy()
            self.queue = []
            return copy

        else:
            return []

    def close(self):
        self.conn.close()
        self.sock.close()


class ClientTerminal(ServerTerminal):
    server_settings = {}

    def connect(self, target_connected=None, target_not=None):
        try:
            self.sock.connect(IP)
        except (ConnectionRefusedError, TimeoutError):
            if target_not is not None:
                target_not()
        else:
            self.server_settings = literal_eval(self.sock.recv(1024 * 4).decode('utf-8'))
            if target_connected is not None:
                target_connected()

    def send(self, message):
        self.sock.send(message.encode('utf-8'))

    def receiving(self):
        while self.work:
            try:
                rcv_data = self.sock.recv(1024 * 4)
                self.queue.extend(rcv_data.decode('utf-8').split(';'))
            except (ConnectionAbortedError, ConnectionResetError):
                if self.work:
                    quit()

    def close(self):
        self.sock.close()


class NetGame(Game):
    enemy_figure_size = [3, 3]

    def __init__(self, terminal, place, players, grid_pos, grid_size, gws, max_sizes, player_colors, inlines, outlines):
        self.terminal = terminal

        if isinstance(terminal, ClientTerminal):
            new_setting = self.terminal.server_settings
            Player.alone_figure = new_setting['alone_figures']

            super().__init__(players, grid_pos, new_setting['grid_size'], gws, new_setting['max_figure_size'], player_colors, inlines, outlines)
        else:
            super().__init__(players, grid_pos, grid_size, gws, max_sizes, player_colors, inlines, outlines)

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

        self.terminal.start_recv()

        while self.play:

            for message in self.terminal.get_queue():
                if message:
                    print(message)
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
                    i[0](*i[1])

                pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.play = False
                    quit_ = True
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    self.current_player.keyboard(event)

            if quit_:
                break

            self.clock.tick(self.fps)

        else:
            self.show_end_msg()

    def show_end_msg(self):
        self.end_msg = True

        def go_to_menu():
            self.end_msg = False
            menu.gaming = False
            menu.start_new_game()

        def orevuar():
            self.terminal.work = False
            self.terminal.close()
            pygame.quit()
            quit()

        restart_button = Button((200, 350), (200, 32), self.end_this_game_and_start_new, pygame.Color(255, 255, 255),
                                pygame.Color(0, 200, 0),
                                "Restart", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (70, 6))

        end_button = Button((350, 400), (200, 32), orevuar, pygame.Color(255, 255, 255), pygame.Color(200, 50, 50),
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
        self.terminal.close()

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

    def __init__(self, settings):
        self.setting = settings

    def mainloop(self):
        def show_online_menu():

            def try_connect(self):
                def start():
                    game_title_text = 'Connected'.upper()
                    game_title_font = pygame.font.SysFont("Gouranga Cyrillic", 32)
                    sucs_title = game_title_font.render(game_title_text, 1, pygame.Color(0, 200, 0),
                                                        pygame.Color(0, 0, 0))

                    win.blit(sucs_title, (480, 180))
                    pygame.display.update()

                    time.sleep(2)

                    nonlocal self
                    self.start_new_game(type_of_game=2, terminal=terminal)
                    self.gaming = True

                    while self.gaming:
                        self.game.mainloop()

                def fail():
                    game_title_text = 'Connection fail'.upper()
                    game_title_font = pygame.font.SysFont("Gouranga Cyrillic", 32)
                    fail_title = game_title_font.render(game_title_text, 1, pygame.Color(200, 0, 0),
                                                        pygame.Color(0, 0, 0))

                    win.blit(fail_title, (480, 145))
                    # nonlocal start_client_button
                    # start_client_button.draw()

                    pygame.display.update()

                    time.sleep(2)

                terminal = ClientTerminal()
                terminal.connect(start, fail)

            nonlocal showed_menu
            start_server_button = Button((240, 140), (200, 32), self.server_loop, pygame.Color(255, 255, 255),
                                         pygame.Color(0, 255, 0),
                                         "Start Server", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (105, 6))

            start_client_button = Button((460, 140), (200, 32), try_connect, pygame.Color(255, 255, 255),
                                         pygame.Color(0, 255, 0),
                                         "Start Client", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (105, 6),
                                         args=[self])

            showed_menu = [start_server_button, start_client_button]

        def show_settings():
            nonlocal showed_menu
            showed_menu = []

        game_title_text = '"Area" the game'.upper()
        game_title_font = pygame.font.SysFont("Gouranga Cyrillic", 32)
        game_title = game_title_font.render(game_title_text, 1, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0, 0))

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

        def successful():
            nonlocal connecting
            nonlocal start_game
            connecting = False
            start_game = True

        terminal = ServerTerminal({'grid_size': self.setting[2],
                                   'max_figure_size': self.setting[4],
                                   'alone_figures': self.setting[8]})

        terminal.accepting(target=successful)

        game_title_text = '"Area" the game'.upper()
        game_title_font = pygame.font.SysFont("Gouranga Cyrillic", 32)
        game_title = game_title_font.render(game_title_text, 1, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))

        ip_address = f"{IP[0]}:{IP[1]}"
        ip_title = game_title_font.render(ip_address, 1, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))

        abort_button = Button((590, 560), (200, 32), stop, pygame.Color(255, 255, 255), pygame.Color(255, 8, 0),
                              "Abort", pygame.Color(0, 0, 0), "Gouranga Cyrillic", 32, (30, 6))

        buttons = [abort_button]

        t = 0

        while True:
            win.fill(0)
            win.blit(game_title, (300, 50))
            win.blit(ip_title, (15, 570))

            if not start_game:
                waiting_text = f"Waiting{'.' * (t // 60)}"
            else:
                waiting_text = "Connected"

            waiting = game_title_font.render(waiting_text, 1, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))
            win.blit(waiting, (350, 300))

            if t <= 350:
                t += 1
            else:
                t = 0

            for button in buttons:
                button.draw()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            if start_game:
                time.sleep(2)
                break

            if not connecting:
                break

            self.clock.tick(self.fps)

        if start_game:
            self.start_new_game(type_of_game=1, terminal=terminal)
            self.gaming = True

            while self.gaming:
                self.game.mainloop()

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

        elif type_of_game == 2:
            self.setting[0] = (NetPlayer, NetPlayer)
            self.game = NetGame(terminal, 1, *self.setting[:-1])


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

        key_binds = {pygame.K_ESCAPE: skip_turn,
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

    def check(self):
        if self.mouse_figure[0] != self.get_in_grid_pos():
            self.mouse_figure = [self.get_in_grid_pos(), self.figure_size]


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

        key_binds = {pygame.K_ESCAPE: skip_turn,
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
    music_list = [r"Music\1.mp3", r"Music\2.mp3", r"Music\3.mp3", r"Music\4.mp3"]
    music_volume = [.2, .2, .2, .2]

    music_id = random.randint(0, 3)
    music_file = music_list[music_id]
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(music_volume[music_id])
    pygame.mixer.music.play(-1)


if __name__ == '__main__':

    win = pygame.display.set_mode((800, 600))  # размеры X и Y
    try:
        pygame.display.set_icon(pygame.image.load("Images\\ico.png"))
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
        play_logo = True

        def_settings = {'intro': True,
                        "grid_size": (40, 40),
                        "lines": (False, True),
                        "max_figure_size": (6, 6),
                        "alone_figures": True,
                        'colorsRGBA': ((255, 160, 0, 1), (165, 45, 45, 1))}

        settings_file = open('settings.txt', 'w', encoding='utf-8')
        settings_file.write(str(def_settings))
        settings_file.close()

    else:
        grid_size = settings_data['grid_size']
        lines = settings_data['lines']
        max_figure_size = settings_data['max_figure_size']
        alone_figures = settings_data['alone_figures']
        colorsRGBA = [pygame.Color(*settings_data['colorsRGBA'][0]), pygame.Color(*settings_data['colorsRGBA'][1])]
        play_logo = settings_data['intro']

    settings = [players, grid_pos, grid_size, grid_widget_size, max_figure_size, colorsRGBA, *lines, alone_figures]

    menu = MainMenu(settings)

    if play_logo:
        t = 0

        background = pygame.image.load('Images\\Background.png')
        GDC = pygame.image.load('Images\\GDC.png')

        fps = 60
        clock = pygame.time.Clock()

        sur2 = pygame.Surface((800, 600))
        sur1 = pygame.Surface((800, 600))
        sur1.blit(background, (0, 0))
        sur2.blit(GDC, (0, 0))

        while play_logo:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            if t > 50:
                sur2.set_alpha(t - 50)
                win.blit(sur2, (0, 0))
            else:
                sur1.set_alpha(t)
                win.blit(sur1, (0, 0))

            pygame.display.update()
            t += 1
            if t >= 360:
                break
            clock.tick(fps)

    # start_music()

    while True:
        menu.mainloop()
