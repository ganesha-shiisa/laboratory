# ユークリッドの互除法


def gcd(a, b):
    """最大公約数を求める関数"""
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    """最小公倍数を求める関数"""
    return abs(a * b) // gcd(a, b)


print("最大公約数:", gcd(48, 18))  # 出力: 最大公約数: 6
print("最小公倍数:", lcm(48, 18))  # 出力: 最小公倍数: 144

# %%
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


color_selector = ColorSelector(100)

# %%
pygame.init()

screen = pygame.display.set_mode((800, 600))

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))

    numA = 14
    numB = 9
    scalar = min(int(800 / numA), int(600 / numB))

    numA *= scalar
    numB *= scalar

    wd = numB
    xPos = 0
    yPos = 0
    itr = 0
    color_selector.reset()
    while wd > 0:
        itr += 1
        if itr % 2 == 1:
            while xPos + wd <= numA:
                pygame.draw.rect(
                    screen, color_selector.get_next(), (xPos, yPos, wd, wd)
                )
                xPos += wd
            wd = numA - xPos
        else:
            while yPos + wd <= numB:
                pygame.draw.rect(
                    screen, color_selector.get_next(), (xPos, yPos, wd, wd)
                )
                yPos += wd
            wd = numB - yPos

    pygame.display.flip()

    clock.tick(60)
pygame.quit()

# %%
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

    numA = 14
    numB = 9
    ratio = numB / numA

    xPos = 0
    yPos = 0
    itr = 0

    wd = width

    color_selector.reset()
    while wd > 0.1:
        itr += 1
        if itr % 2 == 1:
            while xPos + wd * ratio <= width + 0.1:
                pygame.draw.rect(
                    screen, color_selector.get_next(), (xPos, yPos, wd * ratio, wd)
                )
                xPos += wd * ratio
            wd = width - xPos
        else:
            while yPos + wd / ratio < width + 0.1:
                pygame.draw.rect(
                    screen, color_selector.get_next(), (xPos, yPos, wd, wd / ratio)
                )
                yPos += wd / ratio
            wd = width - yPos

    pygame.display.flip()

    clock.tick(60)

pygame.quit()

# %%
