from mapbox_vector_tile import decode
import os
from shapely.geometry import Polygon, MultiPolygon, LinearRing, Point
from .building import Building
# 必要なインポートを追加
from shapely.geometry import Polygon, MultiPolygon, LinearRing, Point
import math


class BuildingDataLoader:
    vertex_count = 0
    simplified_vertex_count = 0

    @staticmethod
    def load_buildings(z, x, y):

        # PBFファイルのパス
        pbf_file = f'{z}/{x}/{y}.pbf'

        # ファイルの存在確認
        if not os.path.isfile(pbf_file):
            print(f"PBF file not found: {pbf_file}")
            return []

        building_list = []

        # PBFファイルの読み込み
        with open(pbf_file, 'rb') as f:
            data = f.read()
            tile = decode(data)

        # レイヤーの取得
        buildings = tile.get('bldg', {})
        if not buildings:
            print("The 'bldg' layer is not available in this tile.")
            return []

        for feature in buildings.get('features', []):
            id_value = feature.get('id', None)
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            coordinates = geometry.get('coordinates', [])
            height = properties.get('z') or properties.get('height') or 0

            # coordinates の深さを取得
            depth = BuildingDataLoader.get_list_depth(coordinates)

            # Buildingインスタンスの作成
            if depth == 3:
                building = Building(id_value, coordinates_3d=coordinates, height=height)
            elif depth == 4:
                building = Building(id_value, coordinates_4d=coordinates, height=height)
            else:
                print(f"Unexpected coordinates depth ({depth}) for building ID {id_value}")
                building = Building(id_value, height=height)

            # 座標の簡略化と重心・半径の計算
            if depth == 3:
                simplified_coords, centroid, radius = BuildingDataLoader.process_coordinates(coordinates)
                building.simplified_coordinates_3d = simplified_coords
                building.centroid = centroid
                building.bounding_circle_radius = radius
            elif depth == 4:
                simplified_coords_list = []
                all_points = []
                # 4D座標の場合、複数のポリゴンがある
                for coords in coordinates:
                    simplified_coords, centroid, radius = BuildingDataLoader.process_coordinates(coords)
                    simplified_coords_list.append(simplified_coords)
                    all_points.extend([Point(pt) for ring in coords for pt in ring])
                building.simplified_coordinates_4d = simplified_coords_list
                # 全てのポイントから重心と半径を計算
                overall_centroid = BuildingDataLoader.calculate_centroid(all_points)
                overall_radius = BuildingDataLoader.calculate_bounding_circle_radius(all_points, overall_centroid)
                building.centroid = (overall_centroid.x, overall_centroid.y)
                building.bounding_circle_radius = overall_radius

            building_list.append(building)

        return building_list

    @staticmethod
    def process_coordinates(coords):
        # シェイプリーのポリゴンを作成
        linear_ring = LinearRing(coords[0])
        polygon = Polygon(linear_ring)

        # 簡略化の度合いを設定（値が大きいほど頂点数が減少）
        tolerance = 30  # 必要に応じて調整

        # ポリゴンの簡略化
        # simplified_polygon = polygon
        simplified_polygon = polygon.simplify(tolerance, preserve_topology=True)
        # simplified_polygon = polygon.convex_hull
        # # 頂点数を制限して簡略化
        # simplified_polygon = BuildingDataLoader.simplify_polygon_to_target_vertices(polygon, target_vertices=6)

        # 結果を表示
        print("元の頂点数:", len(polygon.exterior.coords))
        print("簡略化後の頂点数:", len(simplified_polygon.exterior.coords))
        BuildingDataLoader.vertex_count = BuildingDataLoader.vertex_count + len(polygon.exterior.coords)
        BuildingDataLoader.simplified_vertex_count = BuildingDataLoader.simplified_vertex_count + len(simplified_polygon.exterior.coords)

        # 簡略化した座標を取得
        simplified_coords = [list(simplified_polygon.exterior.coords)]

        # 重心の計算
        centroid = simplified_polygon.centroid
        centroid_coords = (centroid.x, centroid.y)

        # 包含円の半径を計算
        all_points = [Point(pt) for pt in simplified_polygon.exterior.coords]
        radius = BuildingDataLoader.calculate_bounding_circle_radius(all_points, centroid)

        return simplified_coords, centroid_coords, radius

    @staticmethod
    def calculate_centroid(points):
        # ポイントの集合から重心を計算
        x_coords = [point.x for point in points]
        y_coords = [point.y for point in points]
        centroid_x = sum(x_coords) / len(x_coords)
        centroid_y = sum(y_coords) / len(y_coords)
        return Point(centroid_x, centroid_y)

    @staticmethod
    def calculate_bounding_circle_radius(points, centroid):
        # 重心から各ポイントまでの距離の最大値を取得
        distances = [centroid.distance(point) for point in points]
        return max(distances)

    @staticmethod
    def get_list_depth(lst):
        """
        リストのネストの深さを取得します。
        空リストの場合は1とします。
        """
        if isinstance(lst, list):
            if not lst:  # 空リスト
                return 1
            return 1 + max(BuildingDataLoader.get_list_depth(item) for item in lst)
        else:
            return 0

    @staticmethod
    def simplify_polygon_to_target_vertices(polygon, target_vertices=8):
        tolerance = 0.0001
        simplified = polygon.simplify(tolerance, preserve_topology=True)
        while len(simplified.exterior.coords) > target_vertices:
            tolerance *= 1.5  # 誤差を増やす
            simplified = polygon.simplify(tolerance, preserve_topology=True)
        return simplified

