import mercantile

# 渋谷駅の緯度・経度
latitude = 35.6580
longitude = 139.7016

# 複数のズームレベルでタイル座標を取得
for z in range(10, 17):
    tile = mercantile.tile(longitude, latitude, z)
    print(f"ズームレベル {z}: x={tile.x}, y={tile.y}")
