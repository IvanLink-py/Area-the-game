#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import random
import time

import socket
import pygame

pygame.init()
pygame.font.init()
win = pygame.display.set_mode((800, 600))  # размеры X и Y
pygame.display.set_icon(pygame.image.load("ico.png"))
pygame.display.set_caption("Area")

sock = socket.socket()
sock.connect(('localhost', 9090))

fps = 60
clock = pygame.time.Clock()


working = True
while working:
    data = {'mouse': (pygame.mouse.get_pos(), pygame.mouse.get_pressed(), pygame.mouse.get_focused()), 'keyboard': pygame.key.get_pressed()}
    str_data = str(data)
    bytes_data = str_data.encode('utf-8')

    sock.send(bytes_data)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sock.send(b'quit')
            sock.close()

    clock.tick(fps)

sock.close()

