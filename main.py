from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from building.building_data_loader import BuildingDataLoader
from building.camera import CameraController  # CameraControllerをインポート


class MyApp(ShowBase):
    min_height = 20  # 表示する建物の最低高さ

    def __init__(self):
        ShowBase.__init__(self)

        # 座標軸を表示する
        self.axis = self.loader.loadModel('zup-axis')
        self.axis.reparentTo(self.render)
        self.axis.setScale(100)  # 座標軸の長さを設定

        # 地面を描画
        self.card = CardMaker('ground')
        self.card.setFrame(-2048, 2048, -2048, 2048)
        self.ground = self.render.attachNewNode(self.card.generate())
        self.ground.setP(-90)
        self.ground.setColor(0, 0.5, 0, 1)  # 緑色

        # カメラコントローラーを初期化
        self.camera_controller = CameraController(self)

        # ライトの追加
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((1, 1, 1, 1))
        self.render.setLight(self.render.attachNewNode(ambient_light))

        # 全てのビルを配置するノード
        self.buildings_node = self.render.attachNewNode('buildings_node')
        self.buildings_node.setPos(-2038, -2048, 0)
        self.buildings_node.setScale(0.8119, 0.9245, 1)

        # タイル座標を指定
        z = 16
        x = 58199
        y = 25811

        # ワイヤーフレームモードを切り替えるフラグ
        DRAW_WIREFRAME = True  # Trueにするとワイヤーフレーム、Falseにすると面を描画
        # DRAW_WIREFRAME = False  # Trueにするとワイヤーフレーム、Falseにすると面を描画

        # 建物データをロード
        self.building_list = BuildingDataLoader.load_buildings(z, x, y)

        # 建物データから3Dモデルを作成
        building_count = 0
        for building in self.building_list:
            # ビル用のノードを作成し、名前をIDに設定
            building.building_node = self.buildings_node.attachNewNode(str(building.id))

            if building.height < self.min_height:
                continue

            if building.simplified_coordinates_3d:
                building_count = building_count + 1
                self.create_building(building.building_node, building.simplified_coordinates_3d, building.height,
                                     color=(1, 0.5, 0, 1), wireframe=DRAW_WIREFRAME)  # オレンジ色
            elif building.simplified_coordinates_4d:
                building_count = building_count + 1
                for coords in building.simplified_coordinates_4d:
                    self.create_building(building.building_node, coords, building.height, color=(0, 1, 1, 1),
                                         wireframe=DRAW_WIREFRAME)  # 水色
            else:
                # 座標がない場合はスキップ
                continue
        print(f"Total buildings: {building_count}")

        print(f'Polygon vertices: {BuildingDataLoader.vertex_count}')
        print(f'Simplified polygon vertices: {BuildingDataLoader.simplified_vertex_count}')

        self.accept('escape', exit)

    def create_building(self, building_node, coords_list, height, color=(1, 1, 1, 1), wireframe=False):
        # 上面のポリゴンを作成
        top_geom = self.create_polygon_geom(coords_list, color)
        top_node = GeomNode('top_face')
        top_node.addGeom(top_geom)
        top_node_path = building_node.attachNewNode(top_node)
        top_node_path.setPos(0, 0, 1)  # 基準高さ（=1）分だけ移動

        # 側面を作成
        side_geom = self.create_side_geom(coords_list, height, color)
        side_node = GeomNode('side_faces')
        side_node.addGeom(side_geom)
        side_node_path = building_node.attachNewNode(side_node)

        # ワイヤーフレームと面の切り替え
        if wireframe:
            # ワイヤーフレーム表示
            building_node.setRenderModeWireframe()
        else:
            # 面を表示
            building_node.setRenderModeFilled()

        # ビルノードの高さを設定
        building_node.setSz(height)

    def create_polygon_geom(self, coords_list, color=(1, 1, 1, 1)):
        # 上面のポリゴンのジオメトリを作成する
        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('top_face', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')

        # 頂点の追加
        coords = coords_list[0]
        for x, y in coords:
            vertex.addData3f(x, y, 0)
            color_writer.addData4f(*color)

        # ポリゴンを構成するプリミティブの作成
        tris = GeomTriangles(Geom.UHStatic)
        num_vertices = len(coords)
        for i in range(1, num_vertices - 1):
            tris.addVertices(0, i, i + 1)
            tris.closePrimitive()

        # ジオメトリの作成
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        return geom

    def create_side_geom(self, coords_list, height, color=(1, 1, 1, 1)):
        # 側面のジオメトリを作成する
        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('side_faces', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')

        # 側面の作成
        coords = coords_list[0]
        num_vertices = len(coords)
        # ポリゴンが閉じていない場合は、最初の頂点を末尾に追加
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        idx = 0
        tris = GeomTriangles(Geom.UHStatic)

        for i in range(num_vertices - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]

            # 底面の頂点
            vertex.addData3f(x1, y1, 0)
            color_writer.addData4f(*color)
            vertex.addData3f(x2, y2, 0)
            color_writer.addData4f(*color)
            # 上面の頂点
            vertex.addData3f(x1, y1, 1)  # 基準高さ（=1）分だけ移動
            color_writer.addData4f(*color)
            vertex.addData3f(x2, y2, 1)  # 基準高さ（=1）分だけ移動
            color_writer.addData4f(*color)

            # 二つの三角形で四角形を構成
            tris.addVertices(idx, idx + 2, idx + 1)
            tris.addVertices(idx + 1, idx + 2, idx + 3)
            tris.closePrimitive()
            idx += 4

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        return geom


if __name__ == '__main__':
    app = MyApp()
    app.run()
