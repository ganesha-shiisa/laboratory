# ユークリッドの互除法
import random

import pygame


class ColorSelector:
    def __init__(self, count):
        self.colors = [
            (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))
            for _ in range(count)
        ]
        self.index = 0

    def get_next(self):
        color = self.colors[self.index]
        self.index = (self.index + 1) % len(self.colors)
        return color

    def reset(self):
        self.index = 0


color_selector = ColorSelector(1000)


def divRect(xPos, yPos, wd):
    # print(f"divRect: xPos={xPos}, yPos={yPos}, wd={wd}")
    itr = 0
    xEndPos = xPos + wd
    yEndPos = yPos + wd / ratio
    pygame.draw.rect(screen, color_selector.get_next(), (xPos, yPos, wd, wd / ratio))

    while wd > threshold:
        itr += 1
        if itr % 2 == 0:
            while xPos + wd < xEndPos + 0.1:
                divSquare(xPos, yPos, wd)
                # pygame.draw.rect(
                #     screen, color_selector.get_next(), (xPos, yPos, wd, wd)
                # )
                xPos += wd
            wd = xEndPos - xPos
        else:
            while yPos + wd < yEndPos + 0.1:
                divSquare(xPos, yPos, wd)
                # pygame.draw.rect(
                #     screen, color_selector.get_next(), (xPos, yPos, wd, wd)
                # )
                yPos += wd
            wd = yEndPos - yPos


def divSquare(xPos, yPos, wd):
    # print(f"divSquare: xPos={xPos}, yPos={yPos}, wd={wd}")
    itr = 0
    xEndPos = xPos + wd
    yEndPos = yPos + wd
    pygame.draw.rect(screen, color_selector.get_next(), (xPos, yPos, wd, wd))

    while wd > threshold:
        itr += 1
        if itr % 2 == 1:
            while xPos + wd * ratio < xEndPos + 0.1:
                divRect(xPos, yPos, wd * ratio)
                # pygame.draw.rect(
                #     screen, color_selector.get_next(), (xPos, yPos, wd * ratio, wd)
                # )
                xPos += wd * ratio
            wd = xEndPos - xPos
        else:
            while yPos + wd / ratio < yEndPos + 0.1:
                divRect(xPos, yPos, wd)
                # pygame.draw.rect(
                #     screen, color_selector.get_next(), (xPos, yPos, wd, wd / ratio)
                # )
                yPos += wd / ratio
            wd = yEndPos - yPos


pygame.init()

width, height = 500, 500
screen = pygame.display.set_mode((width, height))


clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))

    numA = 10
    numB = 6
    threshold = 98

    ratio = numB / numA

    xPos = 0
    yPos = 0
    wd = width

    color_selector.reset()
    divSquare(xPos, yPos, wd)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
