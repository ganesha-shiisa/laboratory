"""
対数螺旋の描画

参考文献 / 参考書籍:
    『数学から創るジェネラティブアート ― Processingで学ぶかたちのデザイン』
    著者: 巴山竜来
    出版社: 技術評論社 (2019)
    URL: https://gihyo.jp/book/2019/978-4-297-10463-4
"""

import pygame

pygame.init()

width, height = 500, 500
screen = pygame.display.set_mode((width, height))

points = [(0, 0), (500, 0), (500, 500), (0, 500)]


def shift_point(point_a, point_b, gap):
    vec_a = pygame.math.Vector2(point_a)
    vec_b = pygame.math.Vector2(point_b)

    direction = (vec_b - vec_a).normalize()
    result_vec = vec_a + direction * gap
    return (result_vec.x, result_vec.y)


print(shift_point(points[0], points[1], 10))


def shift_points(points, gap):
    shifted_points = []
    for i in range(len(points)):
        point_a = points[i]
        point_b = points[(i + 1) % len(points)]
        shifted_point = shift_point(point_a, point_b, gap)
        shifted_points.append(shifted_point)
    return shifted_points


points_2 = shift_points(points, 10)
print(shift_points(points_2, 10))

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))

    draw_points = [tuple(int(x) for x in t) for t in points]
    pygame.draw.polygon(screen, (0, 255, 0), draw_points, width=2)

    next_points = shift_points(points, 100)
    draw_points = [tuple(int(x) for x in t) for t in next_points]
    pygame.draw.polygon(screen, (0, 255, 0), draw_points, width=2)

    next_points = shift_points(next_points, 100)
    draw_points = [tuple(int(x) for x in t) for t in next_points]
    pygame.draw.polygon(screen, (0, 255, 0), draw_points, width=2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
