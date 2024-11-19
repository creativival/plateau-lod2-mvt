from panda3d.core import GeomNode
from building.geom_utils import create_box_geom, create_polygon_geom, create_side_geom


class GeometryGenerator:
    def __init__(self):
        # 必要に応じてインスタンス変数を初期化
        pass

    @staticmethod
    def create_building(building_node, coords_list, height, color=(1, 1, 1, 1), wireframe=False):
        """
        一般的なビルのモデルを作成します。
        """
        # 上面のポリゴンを作成
        top_geom = create_polygon_geom(coords_list, color)
        top_node = GeomNode('top_face')
        top_node.addGeom(top_geom)
        top_node_path = building_node.attachNewNode(top_node)
        top_node_path.setPos(0, 0, 1)

        # 側面を作成
        side_geom = create_side_geom(coords_list, color)
        side_node = GeomNode('side_faces')
        side_node.addGeom(side_geom)
        side_node_path = building_node.attachNewNode(side_node)

        # ワイヤーフレームと面の切り替え
        if wireframe:
            building_node.setRenderModeWireframe()
        else:
            building_node.setRenderModeFilled()

        # ビルノードの高さを設定
        building_node.setSz(height)

    @staticmethod
    def create_rect_building(building_node, rect_params, centroid, height, color=(1, 1, 1, 1), wireframe=False):
        """
        長方形のビルのモデルを作成します。
        """
        # 長方形のジオメトリを作成
        rect_geom = create_box_geom(rect_params, color)

        # シーンに新しいノードとしてアタッチ
        rect_geom.reparentTo(building_node)

        # 位置の設定
        rect_geom.setPos(centroid[0], centroid[1], 0)

        # 回転の設定（ヒンジ角度）
        rect_geom.setH(rect_params[2])

        # ワイヤーフレームと面の切り替え
        if wireframe:
            rect_geom.setRenderModeWireframe()
            rect_geom.setTwoSided(True)
        else:
            rect_geom.setRenderModeFilled()

        # ビルノードの高さを設定
        building_node.setSz(height)
