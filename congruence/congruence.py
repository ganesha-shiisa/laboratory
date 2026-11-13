"""
合同

参考文献 / 参考書籍:
    『数学から創るジェネラティブアート ― Processingで学ぶかたちのデザイン』
    著者: 巴山竜来
    出版社: 技術評論社 (2019)
    URL: https://gihyo.jp/book/2019/978-4-297-10463-4
"""

import math
from turtle import color

import pygame


class ColorPalette:
    def __init__(self, x, y, label, colors, selected_idx=0):
        self.x = x
        self.y = y
        self.label = label
        self.colors = colors
        self.selected_idx = selected_idx
        self.box_size = 20
        self.gap = 8
        self.label_width = 150

    @property
    def current_color(self):
        return self.colors[self.selected_idx]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            start_x = self.x + self.label_width
            for i, col in enumerate(self.colors):
                rect = pygame.Rect(
                    start_x + i * (self.box_size + self.gap),
                    self.y - 2,
                    self.box_size,
                    self.box_size,
                )
                if rect.collidepoint(event.pos):
                    self.selected_idx = i
                    return True
        return False

    def draw(self, surface):
        # ラベル描画
        text_surf = font.render(f"{self.label}:", True, (220, 220, 220))
        surface.blit(text_surf, (self.x, self.y))

        start_x = self.x + self.label_width
        for i, col in enumerate(self.colors):
            rect = pygame.Rect(
                start_x + i * (self.box_size + self.gap),
                self.y - 2,
                self.box_size,
                self.box_size,
            )
            # カラーボックス描画
            pygame.draw.rect(surface, col, rect, border_radius=4)

            # 選択中の枠線ハイライト
            if i == self.selected_idx:
                highlight_rect = rect.inflate(4, 4)
                pygame.draw.rect(
                    surface, (255, 255, 255), highlight_rect, 2, border_radius=5
                )
            else:
                pygame.draw.rect(surface, (70, 70, 70), rect, 1, border_radius=4)


class Slider:
    def __init__(
        self, x, y, w, h, min_val, max_val, initial_val, label, is_int=False, step=None
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.is_int = is_int
        self.step = step if step is not None else (1 if is_int else 0.01)
        self.dragging = False
        self.handle_radius = h // 2 + 3
        self.btn_size = 20

    @property
    def btn_left_rect(self):
        """左矢印ボタン (◀) の矩形"""
        return pygame.Rect(
            self.rect.x - self.btn_size - 6,
            self.rect.centery - self.btn_size // 2,
            self.btn_size,
            self.btn_size,
        )

    @property
    def btn_right_rect(self):
        """右矢印ボタン (▶) の矩形"""
        return pygame.Rect(
            self.rect.right + 6,
            self.rect.centery - self.btn_size // 2,
            self.btn_size,
            self.btn_size,
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # ◀ ボタンクリック
            if self.btn_left_rect.collidepoint(event.pos):
                self.change_step(-1)
                return True
            # ▶ ボタンクリック
            elif self.btn_right_rect.collidepoint(event.pos):
                self.change_step(1)
                return True

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

    def change_step(self, direction):
        """1ステップ分値を増減させる"""
        step = self.step
        val = self.value + direction * step
        val = max(self.min_val, min(self.max_val, val))
        if self.is_int:
            val = round(val)
        else:
            val = round(val / step) * step
        self.value = val

    def _update_val(self, mouse_x):
        ratio = (mouse_x - self.rect.x) / self.rect.w
        ratio = max(0.0, min(1.0, ratio))
        val = self.min_val + ratio * (self.max_val - self.min_val)
        if self.is_int:
            val = round(val)
        elif self.step:
            val = round(val / self.step) * self.step
        self.value = val

    def draw(self, surface):
        # ◀ ボタン描画
        pygame.draw.rect(surface, (45, 45, 52), self.btn_left_rect, border_radius=4)
        pygame.draw.rect(surface, (80, 80, 90), self.btn_left_rect, 1, border_radius=4)
        t_left = font.render("<", True, (200, 200, 200))
        surface.blit(
            t_left,
            t_left.get_rect(center=self.btn_left_rect.center),
        )

        # ▶ ボタン描画
        pygame.draw.rect(surface, (45, 45, 52), self.btn_right_rect, border_radius=4)
        pygame.draw.rect(surface, (80, 80, 90), self.btn_right_rect, 1, border_radius=4)
        t_right = font.render(">", True, (200, 200, 200))
        surface.blit(
            t_right,
            t_right.get_rect(center=self.btn_right_rect.center),
        )

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
        if self.is_int:
            val_str = f"{int(self.value)}"
        elif self.step and self.step < 0.001:
            val_str = f"{self.value:.6f}"
        else:
            val_str = f"{self.value:.2f}"
        text_surf = font.render(f"{self.label}: {val_str}", True, (220, 220, 220))
        surface.blit(text_surf, (self.rect.x, self.rect.y - 18))


BUTTONS = [
    {"label": "Addition", "value": 0},
    {"label": "Multiplication", "value": 1},
    {"label": "Power", "value": 2},
]


class Button:
    def __init__(self, label, value):
        self.label = label
        self.value = value
        self.rect = pygame.Rect(0, 0, 100, 24)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.value
        return None

    def draw(self, surface, font, is_active=False):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)

        if is_active:
            bg_color = (60, 110, 170)
            border_color = (130, 180, 240)
            text_color = (255, 255, 255)
        elif is_hover:
            bg_color = (55, 55, 65)
            border_color = (120, 120, 140)
            text_color = (240, 240, 240)
        else:
            bg_color = (40, 40, 48)
            border_color = (70, 70, 80)
            text_color = (190, 190, 190)

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.rect, 1, border_radius=4)

        t_surf = font.render(self.label, True, text_color)
        surface.blit(t_surf, t_surf.get_rect(center=self.rect.center))


pygame.init()

sim_width, sim_height = 1000, 1000
ui_height = 200
width, height = sim_width, sim_height + ui_height
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Logarithmic Spiral Visualization")

font = pygame.font.SysFont("Consolas", 14)
font_btn = pygame.font.SysFont("Consolas", 12)

# スライダーの配置
slider_mod = Slider(50, sim_height, 330, 10, 2, 40, 10, "MOD", step=1.0)
sliders = [slider_mod]

# ボタンの配置
buttons = [Button(p["label"], p["value"]) for p in BUTTONS]

# アニメーション設定
anim_playing = False
last_anim_time = 0
anim_interval_ms = 10  # 100msごとに1回更新
anim_delta = 0.00001  # step (0.0001) より細かい変化量

# カラーパレットの候補色
bg_color = ["#050505", "#0B0F19", "#1A0B2E", "#1E222A", "#000000"]
line_color = ["#00F0FF", "#FF2A6D", "#FF9E00", "#A0E7E5", "#E5C158"]

bg_color_options = [tuple(pygame.Color(c)[:3]) for c in bg_color]
line_color_options = [tuple(pygame.Color(c)[:3]) for c in line_color]

palette_bg = ColorPalette(
    100, sim_height + 100, "BG Color", bg_color_options, selected_idx=2
)
palette_element = ColorPalette(
    100, sim_height + 135, "Element Color", line_color_options, selected_idx=2
)
palettes = [palette_bg, palette_element]


def update_ui_positions():
    """ウィンドウサイズ変更時に各UI要素の位置と幅を再計算する"""
    # 左右の矢印ボタン（各20px + マージン）分を考慮してスライダー幅を設定
    slider_w = max(180, width - 210)

    slider_mod.rect.x = 130
    slider_mod.rect.y = sim_height + 30
    slider_mod.rect.w = slider_w

    # ボタンの自動整列（折り返し配置）
    btn_x = 100
    btn_y = sim_height + 65
    for btn in buttons:
        text_w, _ = font_btn.size(btn.label)
        btn_w = max(90, text_w + 16)
        if btn_x + btn_w > width - 30 and btn_x > 130:
            btn_x = 130
            btn_y += 30
        btn.rect = pygame.Rect(btn_x, btn_y, btn_w, 24)
        btn_x += btn_w + 8

    palette_bg.y = sim_height + 110
    palette_element.y = sim_height + 145


def addition_table(mod: int):
    """合同の加法表を描画する"""

    table = [[(i + j) % mod for j in range(mod)] for i in range(mod)]

    return table


def multiplication_table(mod: int):
    """合同の乗法表を描画する"""

    table = [[(i * j) % mod for j in range(1, mod)] for i in range(1, mod)]

    return table


def power_table(mod: int):
    """合同の累乗表を描画する"""

    table = [[(i**j) % mod for j in range(mod)] for i in range(1, mod)]

    return table


def draw_table(surface, mod, table, center, width, color):
    rows = len(table)
    cols = len(table[0]) if rows > 0 else 0

    max_value = max(max(row) for row in table) if rows > 0 else 1

    cell_size = width // max(rows, cols)
    for i in range(rows):
        for j in range(cols):
            val = table[i][j]
            x = (center[0] - width // 2 + cell_size // 2) + j * cell_size
            y = (center[1] - width // 2 + cell_size // 2) + i * cell_size
            pygame.draw.circle(surface, color, (x, y), val * cell_size / max_value / 2)


mode = 0  # 0: Addition, 1: Multiplication, 2: Power
clock = pygame.time.Clock()
update_ui_positions()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # 最小サイズを制限（UIが潰れない高さ・幅）
            width = max(450, event.w)
            height = max(ui_height + 150, event.h)
            sim_width = width
            sim_height = height - ui_height
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            update_ui_positions()
        for s in sliders:
            s.handle_event(event)
        for btn in buttons:
            tmp = btn.handle_event(event)
            if tmp is not None:
                mode = tmp
        for p in palettes:
            p.handle_event(event)

    # アニメーション更新 (100msごとに anim_delta 分変化)
    current_time = pygame.time.get_ticks()
    if anim_playing and (current_time - last_anim_time >= anim_interval_ms):
        last_anim_time = current_time

    bg_col = palette_bg.current_color
    element_col = palette_element.current_color

    screen.fill(bg_col)

    # パラメータ取得
    mod = int(slider_mod.value)

    # 上部描画領域（ウィンドウサイズに合わせて中心と半径を自動追従）
    screen.set_clip(pygame.Rect(0, 0, sim_width, sim_height))
    center = (sim_width / 2, sim_height / 2)
    draw_width = min(sim_width, sim_height) * 0.9

    # 描画
    if mode == 0:
        table = addition_table(mod)
    elif mode == 1:
        table = multiplication_table(mod)
    else:
        table = power_table(mod)
    draw_table(screen, mod, table, center, draw_width, element_col)

    screen.set_clip(None)

    # 下部UI操作パネル
    ui_rect = pygame.Rect(0, sim_height, width, ui_height)
    pygame.draw.rect(screen, (30, 30, 34), ui_rect)
    pygame.draw.line(screen, (70, 70, 80), (0, sim_height), (width, sim_height), 2)

    for s in sliders:
        s.draw(screen)
    for btn in buttons:
        # 現在のslider_gの値と一致しているボタンをハイライト表示
        is_active = mode == btn.value
        btn.draw(screen, font_btn, is_active=is_active)
    for p in palettes:
        p.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
