from mapbox_vector_tile import decode


def export_building_dicts(z, x, y):
    # PBFファイルのパス
    pbf_file = f'{z}/{x}/{y}.pbf'

    # 出力する辞書のリスト
    building_list = []

    # PBFファイルの読み込み
    with open(pbf_file, 'rb') as f:
        data = f.read()
        tile = decode(data)

    # デコードされたタイルのレイヤー名を表示
    print("Available layers:", tile.keys())

    buildings = tile.get('bldg', {})

    # デコードされたタイルのレイヤー名を表示
    print("Building layers:", buildings.keys())
    print("Building extent:", buildings['extent'])
    print("Building version:", buildings['version'])
    print("Building layers:", buildings['type'])
    print("Building features count:", len(buildings['features']))

    ids = []
    for i, feature in enumerate(buildings['features']):
        id_value = feature.get('id', None)
        ids.append(id_value)
        geometry = feature.get('geometry', {})
        coordinates = geometry.get('coordinates', [])
        height = feature['properties'].get('z', 0)
        building_dict = {
            'id': id_value,
            'coordinates': coordinates,
            'height': height
        }
        building_list.append(building_dict)

        # if i < 1:
        #     print('Sample building feature:')
        #     print("Feature type:", type(feature))
        #     print("Feature keys:", feature.keys())
        #     print("Feature id:", feature['id'])
        #     print("Feature properties:", feature['properties'])
        #     print("Feature type:", feature['type'])
        #     print("Feature geometry:", feature['geometry'])
        #     print("Feature geometry type:", feature['geometry']['type'])
        #     print("Feature geometry coordinates:", feature['geometry']['coordinates'])

    # print("Unique IDs:", len(set(ids)), len(ids))
    # print("Unique IDs:", set(ids))

    return building_list


if __name__ == '__main__':
    # タイルのズームレベル、X、Y座標
    # 渋谷駅のタイル座標
    # ズームレベル 10: x=909, y=403
    # ズームレベル 11: x=1818, y=806
    # ズームレベル 12: x=3637, y=1613
    # ズームレベル 13: x=7274, y=3226
    # ズームレベル 14: x=14549, y=6452
    # ズームレベル 15: x=29099, y=12905
    # ズームレベル 16: x=58199, y=25811

    # z = 15
    # x = 29099
    # y = 12905

    z = 16
    x = 58199
    y = 25811
    building_dicts = export_building_dicts(z, x, y)

    print("Building dictionary:", building_dicts[0])
