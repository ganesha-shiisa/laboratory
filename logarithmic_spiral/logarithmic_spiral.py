"""
対数螺旋の描画

参考文献 / 参考書籍:
    『数学から創るジェネラティブアート ― Processingで学ぶかたちのデザイン』
    著者: 巴山竜来
    出版社: 技術評論社 (2019)
    URL: https://gihyo.jp/book/2019/978-4-297-10463-4
"""

import math

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

    @property
    def current_color(self):
        return self.colors[self.selected_idx]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            start_x = self.x + 95
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

        start_x = self.x + 95
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
        self.step = step
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
        elif self.step:
            val = round(val / self.step) * self.step
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
        if self.is_int:
            val_str = f"{int(self.value)}"
        else:
            val_str = f"{self.value:.2f}"
        text_surf = font.render(f"{self.label}: {val_str}", True, (220, 220, 220))
        surface.blit(text_surf, (self.rect.x, self.rect.y - 18))


def shift_point(point_a, point_b, gap):
    vec_a = pygame.math.Vector2(point_a)
    vec_b = pygame.math.Vector2(point_b)

    result_vec = vec_a + (vec_b - vec_a) * gap
    return (result_vec.x, result_vec.y)


def shift_points(points, gap):
    shifted_points = []
    for i in range(len(points)):
        point_a = points[i]
        point_b = points[(i + 1) % len(points)]
        shifted_point = shift_point(point_a, point_b, gap)
        shifted_points.append(shifted_point)
    return shifted_points


def get_max_edge_length(points):
    """多角形の1辺の長さの最大値を返す"""
    if len(points) < 2:
        return 0.0

    max_length = 0.0
    for i in range(len(points)):
        p1 = pygame.math.Vector2(points[i])
        p2 = pygame.math.Vector2(points[(i + 1) % len(points)])
        edge_length = p1.distance_to(p2)
        if edge_length > max_length:
            max_length = edge_length

    return max_length


def create_regular_polygon_points(n, center, radius=200, rotation=0.0):
    """
    正n角形（頂点数/角の数: n）の頂点座標リストを作成する

    :param n: 角の数（頂点数, 3以上の整数）
    :param center: 中心座標 (cx, cy)
    :param radius: 外接円の半径。デフォルトは 200
    :param rotation: 傾き・回転角度（ラジアン）。時計回りに回転。デフォルトは 0.0
    :return: 頂点座標のタプルのリスト [(x1, y1), (x2, y2), ...]
    """
    if n < 3:
        raise ValueError("角の数は3以上である必要があります。")

    cx, cy = center
    points = []

    # -pi/2 で真上（12時方向）から開始し、rotation 分傾ける
    for i in range(n):
        angle = -math.pi / 2 + rotation + 2 * math.pi * i / n
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))

    return points


pygame.init()

sim_width, sim_height = 500, 500
ui_height = 205
width, height = sim_width, sim_height + ui_height
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Logarithmic Spiral Visualization")

font = pygame.font.SysFont("Consolas", 14)

# スライダーの配置 (x, y, w, h, min, max, initial, label)
slider_n = Slider(50, sim_height + 25, 330, 10, 3, 12, 4, "n (corners)", is_int=True)
slider_rotation = Slider(
    50,
    sim_height + 65,
    330,
    10,
    0.0,
    360.0,
    45.0,
    "rotation (deg)",
    is_int=False,
    step=1.0,
)
slider_gap = Slider(
    50, sim_height + 105, 330, 10, 0.02, 0.50, 0.20, "gap", is_int=False, step=0.01
)
sliders = [slider_n, slider_rotation, slider_gap]

# カラーパレットの候補色
bg_color = ["#050505", "#0B0F19", "#1A0B2E", "#1E222A", "#000000"]
line_color = ["#00F0FF", "#FF2A6D", "#FF9E00", "#A0E7E5", "#E5C158"]

bg_color_options = [tuple(pygame.Color(c)[:3]) for c in bg_color]
line_color_options = [tuple(pygame.Color(c)[:3]) for c in line_color]

palette_bg = ColorPalette(
    50, sim_height + 130, "BG Color", bg_color_options, selected_idx=0
)
palette_line = ColorPalette(
    50, sim_height + 165, "Line Color", line_color_options, selected_idx=0
)
palettes = [palette_bg, palette_line]


def update_ui_positions():
    """ウィンドウサイズ変更時に各UI要素の位置と幅を再計算する"""
    slider_w = max(180, width - 180)

    slider_n.rect.x = 130
    slider_n.rect.y = sim_height + 25
    slider_n.rect.w = slider_w

    slider_rotation.rect.x = 130
    slider_rotation.rect.y = sim_height + 65
    slider_rotation.rect.w = slider_w

    slider_gap.rect.x = 130
    slider_gap.rect.y = sim_height + 105
    slider_gap.rect.w = slider_w

    palette_bg.y = sim_height + 130
    palette_line.y = sim_height + 165


clock = pygame.time.Clock()
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
        for p in palettes:
            p.handle_event(event)

    bg_col = palette_bg.current_color
    line_col = palette_line.current_color

    screen.fill(bg_col)

    # パラメータ取得
    n = int(slider_n.value)
    rotation_rad = math.radians(slider_rotation.value)
    gap = slider_gap.value

    # 上部描画領域（ウィンドウサイズに合わせて中心と半径を自動追従）
    screen.set_clip(pygame.Rect(0, 0, sim_width, sim_height))
    center = (sim_width / 2, sim_height / 2)
    radius = min(sim_width, sim_height) * 0.44  # 描画エリアの44%（余白を少し残す）
    points = create_regular_polygon_points(
        n, center, radius=radius, rotation=rotation_rad
    )
    draw_points = [tuple(int(x) for x in t) for t in points]
    pygame.draw.polygon(screen, line_col, draw_points, width=2)

    while True:
        if get_max_edge_length(points) < 1:
            break

        points = shift_points(points, gap)
        draw_points = [tuple(int(x) for x in t) for t in points]
        pygame.draw.polygon(screen, line_col, draw_points, width=2)

    screen.set_clip(None)

    # 下部UI操作パネル
    ui_rect = pygame.Rect(0, sim_height, width, ui_height)
    pygame.draw.rect(screen, (30, 30, 34), ui_rect)
    pygame.draw.line(screen, (70, 70, 80), (0, sim_height), (width, sim_height), 2)

    for s in sliders:
        s.draw(screen)
    for p in palettes:
        p.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
