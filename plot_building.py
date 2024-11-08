import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

# 建物IDと座標データ
building_id = 395833
coordinates = [
    [   # 第一ポリゴン
        [
            [-80, 782], [-77, 781], [-74, 788], [-64, 783],
            [-73, 760], [-74, 761], [-76, 757], [-80, 759], [-80, 782]
        ]
    ],
    [   # 第二ポリゴン
        [
            [-80, 782], [-80, 794], [-79, 793], [-80, 782]
        ]
    ]
]
coordinates = [[[[4160, 2660], [4164, 2658], [4153, 2636], [4149, 2638], [4160, 2660]]], [[[4165, 2671], [4169, 2669], [4166, 2663], [4162, 2665], [4165, 2671]]]]
coordinates = [[[[610, -80], [614, -70], [615, -70], [616, -69], [617, -69], [618, -68], [622, -70], [625, -80], [610, -80]]], [[[610, -80], [607, -80], [607, -78], [610, -80]]]]
coordinates = [[[[3796, 2030], [3797, 2026], [3792, 2024], [3791, 2025], [3787, 2024], [3784, 2033], [3801, 2040], [3801, 2038], [3794, 2036], [3795, 2030], [3796, 2030]]], [[[3806, 2040], [3819, 2046], [3820, 2042], [3815, 2040], [3815, 2038], [3796, 2030], [3801, 2033], [3799, 2034], [3810, 2039], [3811, 2039], [3810, 2041], [3806, 2040]]], [[[3806, 2040], [3803, 2039], [3803, 2040], [3805, 2041], [3806, 2040]]]]

# ポリゴンの作成
polygons = []
for polygon_coords in coordinates:
    rings = [ring for ring in polygon_coords]
    polygon = Polygon(shell=rings[0], holes=rings[1:])
    polygons.append(polygon)

# マルチポリゴンの作成
building_shape = MultiPolygon(polygons)

# 描画の準備
fig, ax = plt.subplots()
patches = []
colors = []  # 各ポリゴンの色を指定するリスト

# カラーマップまたは色のリストを用意
polygon_colors = ['orange', 'cyan']  # ポリゴンの数に合わせて色を指定

# ポリゴンをパッチとして追加
for idx, geom in enumerate(building_shape.geoms):
    exterior_coords = list(geom.exterior.coords)
    polygon_patch = MplPolygon(exterior_coords, closed=True)
    patches.append(polygon_patch)
    colors.append(polygon_colors[idx % len(polygon_colors)])  # 色を指定

    # 内側のリング（穴）がある場合
    for interior in geom.interiors:
        interior_coords = list(interior.coords)
        interior_patch = MplPolygon(interior_coords, closed=True)
        patches.append(interior_patch)
        colors.append('white')  # 穴は白で塗りつぶし

# パッチコレクションを作成
p = PatchCollection(patches, facecolor=colors, edgecolor='black', alpha=0.5)
ax.add_collection(p)

# 軸の範囲を設定
all_x_coords = [coord[0] for poly in polygons for coord in poly.exterior.coords]
all_y_coords = [coord[1] for poly in polygons for coord in poly.exterior.coords]
ax.set_xlim(min(all_x_coords) - 10, max(all_x_coords) + 10)
ax.set_ylim(min(all_y_coords) - 10, max(all_y_coords) + 10)

# タイトルと表示
ax.set_title(f'Building ID {building_id}')
ax.set_aspect('equal', 'box')
plt.xlabel('X座標')
plt.ylabel('Y座標')
plt.grid(True)
plt.show()
