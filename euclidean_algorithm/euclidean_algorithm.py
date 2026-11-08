"""
ユークリッドの互除法による幾何分割ビジュアライゼーション
参考文献 / 参考書籍:
    『数学から創るジェネラティブアート ― Processingで学ぶかたちのデザイン』
    著者: 巴山竜来
    出版社: 技術評論社 (2019)
    URL: https://gihyo.jp/book/2019/978-4-297-10463-4
"""

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
    itr = 0
    xEndPos = xPos + wd
    yEndPos = yPos + wd / ratio
    pygame.draw.rect(screen, color_selector.get_next(), (xPos, yPos, wd, wd / ratio))

    while wd > threshold:
        itr += 1
        if itr % 2 == 0:
            while xPos + wd < xEndPos + 0.1:
                divSquare(xPos, yPos, wd)
                xPos += wd
            wd = xEndPos - xPos
        else:
            while yPos + wd < yEndPos + 0.1:
                divSquare(xPos, yPos, wd)
                yPos += wd
            wd = yEndPos - yPos


def divSquare(xPos, yPos, wd):
    itr = 0
    xEndPos = xPos + wd
    yEndPos = yPos + wd
    pygame.draw.rect(screen, color_selector.get_next(), (xPos, yPos, wd, wd))

    while wd > threshold:
        itr += 1
        if itr % 2 == 1:
            while xPos + wd * ratio < xEndPos + 0.1:
                divRect(xPos, yPos, wd * ratio)
                xPos += wd * ratio
            wd = xEndPos - xPos
        else:
            while yPos + wd / ratio < yEndPos + 0.1:
                divRect(xPos, yPos, wd)
                yPos += wd / ratio
            wd = yEndPos - yPos


pygame.init()

# 画面設定（下部にUI操作パネル用の領域を追加）
sim_width, sim_height = 500, 500
ui_height = 140
width, height = sim_width, sim_height + ui_height
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Euclidean Algorithm Visualization")

font = pygame.font.SysFont("Consolas", 14)


class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, label, is_int=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.is_int = is_int
        self.dragging = False
        self.handle_radius = h // 2 + 3

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            handle_x = self.rect.x + int(
                (self.value - self.min_val)
                / (self.max_val - self.min_val)
                * self.rect.w
            )
            handle_rect = pygame.Rect(
                handle_x - self.handle_radius,
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2,
            )
            if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_val(mouse_x)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_val(event.pos[0])
            return True
        return False

    def _update_val(self, mouse_x):
        ratio = (mouse_x - self.rect.x) / self.rect.w
        ratio = max(0.0, min(1.0, ratio))
        val = self.min_val + ratio * (self.max_val - self.min_val)
        if self.is_int:
            val = round(val)
        self.value = val

    def draw(self, surface):
        # 背景バー
        pygame.draw.rect(
            surface, (60, 60, 60), self.rect, border_radius=self.rect.h // 2
        )
        # つまみ位置
        handle_x = self.rect.x + int(
            (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.w
        )
        # 進行バー
        filled_rect = pygame.Rect(
            self.rect.x, self.rect.y, handle_x - self.rect.x, self.rect.h
        )
        pygame.draw.rect(
            surface, (70, 130, 180), filled_rect, border_radius=self.rect.h // 2
        )
        # つまみ描画
        pygame.draw.circle(
            surface, (220, 220, 220), (handle_x, self.rect.centery), self.handle_radius
        )
        pygame.draw.circle(
            surface, (30, 30, 30), (handle_x, self.rect.centery), self.handle_radius, 2
        )

        # ラベルと値の描画
        val_str = f"{int(self.value)}" if self.is_int else f"{self.value:.1f}"
        text_surf = font.render(f"{self.label}: {val_str}", True, (220, 220, 220))
        surface.blit(text_surf, (self.rect.x, self.rect.y - 18))


# スライダーの配置 (x, y, w, h, min, max, initial, label)
# numB > numA の拘束のため初期値を numA = 6, numB = 10 に設定
slider_numA = Slider(110, sim_height + 25, 340, 10, 1, 49, 6, "numA")
slider_numB = Slider(110, sim_height + 65, 340, 10, 2, 50, 10, "numB")
slider_threshold = Slider(110, sim_height + 105, 340, 10, 5, 200, 98, "threshold")
sliders = [slider_numA, slider_numB, slider_threshold]

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for s in sliders:
            s.handle_event(event)

    # numB > numA の拘束
    if slider_numA.dragging:
        # numA を動かしているときは、numB が最低でも numA + 1 になるよう押し上げる
        if slider_numB.value <= slider_numA.value:
            slider_numB.value = min(slider_numB.max_val, slider_numA.value + 1)
            # それでも numB > numA を維持できない場合は numA 側を抑える
            if slider_numA.value >= slider_numB.value:
                slider_numA.value = slider_numB.value - 1
    elif slider_numB.dragging:
        # numB を動かしているときは、numA が最大でも numB - 1 になるよう押し下げる
        if slider_numA.value >= slider_numB.value:
            slider_numA.value = max(slider_numA.min_val, slider_numB.value - 1)
            # それでも numB > numA を維持できない場合は numB 側を抑える
            if slider_numB.value <= slider_numA.value:
                slider_numB.value = slider_numA.value + 1
    else:
        # 非ドラッグ時（安全策）
        if slider_numB.value <= slider_numA.value:
            slider_numB.value = min(slider_numB.max_val, slider_numA.value + 1)

    screen.fill((0, 0, 0))

    numA = max(1, slider_numA.value)
    numB = max(1, slider_numB.value)
    threshold = max(1, slider_threshold.value)

    ratio = numB / numA

    xPos = 0
    yPos = 0
    wd = sim_width

    # 上部描画エリアのクリッピング（UI領域にはみ出さないように設定）
    screen.set_clip(pygame.Rect(0, 0, sim_width, sim_height))
    color_selector.reset()
    divSquare(xPos, yPos, wd)
    screen.set_clip(None)

    # UI領域の背景
    ui_rect = pygame.Rect(0, sim_height, width, ui_height)
    pygame.draw.rect(screen, (30, 30, 34), ui_rect)
    pygame.draw.line(screen, (70, 70, 80), (0, sim_height), (width, sim_height), 2)

    # スライダー描画
    for s in sliders:
        s.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
