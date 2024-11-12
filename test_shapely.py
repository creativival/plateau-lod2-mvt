from shapely.geometry import Polygon
import matplotlib.pyplot as plt

# 元のポリゴン座標
coordinates = [
    [11, 3603], [39, 3569], [52, 3580], [71, 3557],
    [69, 3533], [0, 3476], [-80, 3410], [-80, 3420],
    [-67, 3430], [-80, 3446], [-80, 3527], [0, 3594],
    [11, 3603]
]

# Shapelyのポリゴンオブジェクトを作成
polygon = Polygon(coordinates)

# 簡略化の度合いを設定（値が大きいほど頂点数が減少）
tolerance = 20  # 必要に応じて調整

# ポリゴンを簡略化
simplified_polygon = polygon.simplify(tolerance, preserve_topology=True)

# 結果を表示
print("元の頂点数:", len(polygon.exterior.coords))
print("簡略化後の頂点数:", len(simplified_polygon.exterior.coords))
print("簡略化後の座標:", list(simplified_polygon.exterior.coords))

# ポリゴンを可視化（オプション）
fig, ax = plt.subplots()
x, y = polygon.exterior.xy
ax.plot(x, y, label='Original Polygon')

x_simp, y_simp = simplified_polygon.exterior.xy
ax.plot(x_simp, y_simp, label='Simplified Polygon', linestyle='--')

ax.legend()
plt.show()