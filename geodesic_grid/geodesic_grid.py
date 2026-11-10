import numpy as np
import pyvista as pv

# ============================================================
# 基本処理
# ============================================================


def get_triangles(mesh: pv.PolyData) -> np.ndarray:
    """PyVistaの三角形メッシュから頂点インデックスを取得する。"""
    faces = mesh.faces.reshape(-1, 4)

    if not np.all(faces[:, 0] == 3):
        raise ValueError("三角形以外の面が含まれています。")

    return faces[:, 1:4]


def create_triangle_mesh(
    vertices: np.ndarray,
    triangles: np.ndarray,
) -> pv.PolyData:
    """頂点配列と三角形インデックスからPolyDataを生成する。"""
    faces = np.hstack(
        [
            np.full((len(triangles), 1), 3, dtype=np.int64),
            triangles,
        ]
    )

    return pv.PolyData(vertices, faces)


def create_polygon_mesh(
    vertices: np.ndarray,
    polygons: list[list[int]],
) -> pv.PolyData:
    """可変頂点数の多角形面からPolyDataを生成する。"""
    face_data = []

    for polygon in polygons:
        face_data.extend([len(polygon), *polygon])

    return pv.PolyData(
        vertices,
        np.asarray(face_data, dtype=np.int64),
    )


# ============================================================
# Step 3：三角形細分化
# ============================================================


def subdivide(
    vertices: np.ndarray,
    triangles: np.ndarray,
    levels: int = 2,
):
    """
    三角形を指定回数だけ細分化する。

    1回の細分化:
        1 triangle -> 4 triangles

    levels=2 の場合:
        1 triangle -> 4 -> 16 triangles
    """

    current_vertices = np.asarray(vertices, dtype=float)
    current_triangles = np.asarray(triangles, dtype=np.int64)

    for _ in range(levels):

        new_vertices = current_vertices.tolist()
        midpoint_cache = {}

        def get_midpoint_index(i: int, j: int) -> int:
            edge = tuple(sorted((int(i), int(j))))

            # すでに同じ辺の中点を作っていたら再利用
            if edge in midpoint_cache:
                return midpoint_cache[edge]

            midpoint = (current_vertices[i] + current_vertices[j]) / 2.0

            index = len(new_vertices)
            new_vertices.append(midpoint.tolist())

            midpoint_cache[edge] = index

            return index

        new_triangles = []

        for a, b, c in current_triangles:
            ab = get_midpoint_index(a, b)
            bc = get_midpoint_index(b, c)
            ca = get_midpoint_index(c, a)

            new_triangles.extend(
                [
                    [a, ab, ca],
                    [b, bc, ab],
                    [c, ca, bc],
                    [ab, bc, ca],
                ]
            )

        # 今回作った結果を次の細分化の入力にする
        current_vertices = np.asarray(
            new_vertices,
            dtype=float,
        )

        current_triangles = np.asarray(
            new_triangles,
            dtype=np.int64,
        )

    return current_vertices, current_triangles


# ============================================================
# Step 4：球面投影
# ============================================================


def project_to_sphere(
    vertices: np.ndarray,
    radius: float = 1.0,
) -> np.ndarray:
    """頂点を原点中心・指定半径の球面へ投影する。"""
    lengths = np.linalg.norm(vertices, axis=1)

    if np.any(lengths == 0):
        raise ValueError("原点にある頂点は球面へ投影できません。")

    return vertices / lengths[:, np.newaxis] * radius


# ============================================================
# Step 5：Face Center
# ============================================================


def calculate_face_centers(
    vertices: np.ndarray,
    triangles: np.ndarray,
    radius: float = 1.0,
) -> np.ndarray:
    """
    各三角形の重心を計算し、
    球面上へ投影する。
    """
    centers = []

    for a, b, c in triangles:
        center = (vertices[a] + vertices[b] + vertices[c]) / 3.0

        center = center / np.linalg.norm(center) * radius
        centers.append(center)

    return np.asarray(centers, dtype=float)


def build_vertex_to_faces(
    triangles: np.ndarray,
    vertex_count: int,
) -> list[list[int]]:
    """各頂点に接している三角形IDを取得する。"""
    vertex_to_faces = [[] for _ in range(vertex_count)]

    for face_id, (a, b, c) in enumerate(triangles):
        vertex_to_faces[a].append(face_id)
        vertex_to_faces[b].append(face_id)
        vertex_to_faces[c].append(face_id)

    return vertex_to_faces


def sort_face_centers_around_vertex(
    vertex_position: np.ndarray,
    face_ids: list[int],
    face_centers: np.ndarray,
) -> list:
    """
    Face Centerを対象頂点の周囲の循環順に並べる。
    """
    normal = vertex_position / np.linalg.norm(vertex_position)

    if abs(normal[1]) < 0.9:
        reference = np.array([0.0, 1.0, 0.0])
    else:
        reference = np.array([1.0, 0.0, 0.0])

    tangent_u = np.cross(reference, normal)
    tangent_u /= np.linalg.norm(tangent_u)

    tangent_v = np.cross(normal, tangent_u)
    tangent_v /= np.linalg.norm(tangent_v)

    face_angles = []

    for face_id in face_ids:
        direction = face_centers[face_id] - vertex_position

        x = np.dot(direction, tangent_u)
        y = np.dot(direction, tangent_v)

        angle = np.arctan2(y, x)
        face_angles.append((angle, face_id))

    face_angles.sort(key=lambda item: item[0])

    ordered_face_ids = [face_id for _, face_id in face_angles]

    # 面が球の外側を向くように調整
    if len(ordered_face_ids) >= 3:
        p0 = face_centers[ordered_face_ids[0]]
        p1 = face_centers[ordered_face_ids[1]]
        p2 = face_centers[ordered_face_ids[2]]

        polygon_normal = np.cross(
            p1 - p0,
            p2 - p0,
        )

        if np.dot(polygon_normal, normal) < 0:
            ordered_face_ids.reverse()

    return ordered_face_ids


def build_dual_polygons(
    vertices: np.ndarray,
    triangles: np.ndarray,
    face_centers: np.ndarray,
):
    """
    元の各頂点の周囲にあるFace Centerを接続し、
    五角形・六角形を作る。
    """
    vertex_to_faces = build_vertex_to_faces(
        triangles,
        len(vertices),
    )

    pentagons = []
    hexagons = []
    cells = []

    for vertex_id, connected_faces in enumerate(vertex_to_faces):
        ordered_faces = sort_face_centers_around_vertex(
            vertices[vertex_id],
            connected_faces,
            face_centers,
        )

        side_count = len(ordered_faces)

        cell = {
            "id": vertex_id,
            "original_vertex_id": vertex_id,
            "face_center_indices": ordered_faces,
            "side_count": side_count,
        }

        if side_count == 5:
            cell["type"] = "pentagon"
            pentagons.append(ordered_faces)

        elif side_count == 6:
            cell["type"] = "hexagon"
            hexagons.append(ordered_faces)

        else:
            cell["type"] = "unexpected"

            print(f"Warning: Cell {vertex_id} has " f"{side_count} sides.")

        cells.append(cell)

    return pentagons, hexagons, cells


# ============================================================
# Step 1：正二十面体
# ============================================================

RADIUS = 1.0

base_mesh = pv.Icosahedron(radius=RADIUS)

base_vertices = base_mesh.points.copy()
base_triangles = get_triangles(base_mesh)

BASE_VERTEX_COUNT = len(base_vertices)


# ============================================================
# Step 3：細分化
# ============================================================

subdivided_vertices, subdivided_triangles = subdivide(
    base_vertices, base_triangles, levels=4
)

subdivided_mesh = create_triangle_mesh(
    subdivided_vertices,
    subdivided_triangles,
)


# ============================================================
# Step 4：球面投影
# ============================================================

projected_vertices = project_to_sphere(
    subdivided_vertices,
    radius=RADIUS,
)

projected_mesh = create_triangle_mesh(
    projected_vertices,
    subdivided_triangles,
)


# ============================================================
# Step 5：双対面を生成
# ============================================================

face_centers = calculate_face_centers(
    projected_vertices,
    subdivided_triangles,
    radius=RADIUS,
)

pentagons, hexagons, cells = build_dual_polygons(
    projected_vertices,
    subdivided_triangles,
    face_centers,
)

pentagon_mesh = create_polygon_mesh(
    face_centers,
    pentagons,
)

hexagon_mesh = create_polygon_mesh(
    face_centers,
    hexagons,
)


# ============================================================
# 検証
# ============================================================

print("Step 1")
print("  Vertices :", len(base_vertices))
print("  Faces    :", len(base_triangles))

print("\nStep 3 / 4")
print("  Vertices :", len(projected_vertices))
print("  Faces    :", len(subdivided_triangles))

print("\nStep 5 / 6")
print("  Face Centers :", len(face_centers))
print("  Cells        :", len(cells))
print("  Pentagons    :", len(pentagons))
print("  Hexagons     :", len(hexagons))

# assert len(base_vertices) == 12
# assert len(base_triangles) == 20
# assert len(projected_vertices) == 42
# assert len(subdivided_triangles) == 80
# assert len(face_centers) == 80
# assert len(cells) == 42
# assert len(pentagons) == 12
# assert len(hexagons) == 30
print(f"Vertices     : {len(projected_vertices)}")
print(f"Triangles    : {len(subdivided_triangles)}")
print(f"Face Centers : {len(face_centers)}")
print(f"Cells        : {len(cells)}")
print(f"Pentagons    : {len(pentagons)}")
print(f"Hexagons     : {len(hexagons)}")

# ============================================================
# PyVista Viewer
# ============================================================

plotter = pv.Plotter()
actors = []


def clear_geometry():
    global actors

    for actor in actors:
        plotter.remove_actor(actor)

    actors = []


def add_title(text: str):
    actors.append(
        plotter.add_text(
            text,
            position="upper_left",
            color="black",
            font_size=12,
        )
    )


def add_original_vertices(vertices: np.ndarray):
    """元の12頂点と追加頂点を色分けして表示する。"""
    actors.append(
        plotter.add_points(
            vertices[:BASE_VERTEX_COUNT],
            color="red",
            point_size=12,
            render_points_as_spheres=True,
        )
    )

    if len(vertices) > BASE_VERTEX_COUNT:
        actors.append(
            plotter.add_points(
                vertices[BASE_VERTEX_COUNT:],
                color="orange",
                point_size=10,
                render_points_as_spheres=True,
            )
        )


def add_dual_faces(opacity: float):
    """五角形と六角形の面を表示する。"""
    actors.append(
        plotter.add_mesh(
            pentagon_mesh,
            color="orange",
            opacity=opacity,
            show_edges=True,
            edge_color="black",
            line_width=3,
            smooth_shading=False,
        )
    )

    actors.append(
        plotter.add_mesh(
            hexagon_mesh,
            color="lightblue",
            opacity=opacity,
            show_edges=True,
            edge_color="black",
            line_width=2,
            smooth_shading=False,
        )
    )


def add_face_centers():
    """双対化後の頂点を青色で表示する。"""
    actors.append(
        plotter.add_points(
            face_centers,
            color="blue",
            point_size=9,
            render_points_as_spheres=True,
        )
    )


def show_state(step: int):
    global actors

    clear_geometry()

    # --------------------------------------------------------
    # Step 1
    # --------------------------------------------------------

    if step == 1:
        actors.append(
            plotter.add_mesh(
                base_mesh,
                color="lightblue",
                opacity=0.30,
                show_edges=True,
                edge_color="black",
                line_width=2,
            )
        )

        add_original_vertices(base_vertices)

        add_title(
            "Step 1 : Icosahedron\n"
            f"Vertices: {len(base_vertices)}\n"
            f"Faces: {len(base_triangles)}"
        )

    # --------------------------------------------------------
    # Step 2
    # --------------------------------------------------------

    elif step == 2:
        actors.append(
            plotter.add_mesh(
                subdivided_mesh,
                color="lightblue",
                opacity=0.30,
                show_edges=True,
                edge_color="black",
                line_width=2,
            )
        )

        add_original_vertices(subdivided_vertices)

        add_title(
            "Step 2 : Subdivision\n"
            f"Vertices: {len(subdivided_vertices)}\n"
            f"Faces: {len(subdivided_triangles)}"
        )

    # --------------------------------------------------------
    # Step 3
    # --------------------------------------------------------

    elif step == 3:
        actors.append(
            plotter.add_mesh(
                projected_mesh,
                color="lightblue",
                opacity=0.30,
                show_edges=True,
                edge_color="black",
                line_width=2,
            )
        )

        add_original_vertices(projected_vertices)

        add_title(
            "Step 3 : Spherical Projection\n"
            f"Vertices: {len(projected_vertices)}\n"
            f"Faces: {len(subdivided_triangles)}"
        )

    # --------------------------------------------------------
    # Step 4
    # 元の三角形＋元頂点＋Face Center＋双対面
    # --------------------------------------------------------

    elif step == 4:
        # 元の三角形を薄く表示
        actors.append(
            plotter.add_mesh(
                projected_mesh,
                color="lightgray",
                opacity=0.12,
                show_edges=True,
                edge_color="gray",
                line_width=1,
            )
        )

        # 赤・オレンジの元頂点
        add_original_vertices(projected_vertices)

        # 五角形・六角形
        add_dual_faces(opacity=0.50)

        # 青いFace Center
        add_face_centers()

        add_title(
            "Step 4 : Dualization\n"
            "Face Centers around each original vertex\n"
            f"Pentagons: {len(pentagons)}\n"
            f"Hexagons: {len(hexagons)}"
        )

    # --------------------------------------------------------
    # Step 5
    # 五角形・六角形の面＋青い頂点だけ
    # --------------------------------------------------------

    elif step == 5:
        add_dual_faces(opacity=0.65)
        add_face_centers()

        add_title(
            "Step 5 : Dual Cell Sphere\n"
            f"Dual Vertices: {len(face_centers)}\n"
            f"Pentagons: {len(pentagons)}\n"
            f"Hexagons: {len(hexagons)}\n"
            f"Cells: {len(cells)}"
        )

    plotter.render()


# ============================================================
# キーボード操作
# ============================================================

plotter.add_key_event("1", lambda: show_state(1))
plotter.add_key_event("2", lambda: show_state(2))
plotter.add_key_event("3", lambda: show_state(3))
plotter.add_key_event("4", lambda: show_state(4))
plotter.add_key_event("5", lambda: show_state(5))

plotter.add_axes()
plotter.set_background("white")

show_state(1)
plotter.show()
