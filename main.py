from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from building.building_data_loader import BuildingDataLoader
from building.camera import CameraController
import threading
import math
from building.sound import Sound
from direct.task import Task
from queue import Empty


class MyApp(ShowBase):
    # ワイヤーフレームモードを切り替えるフラグ
    # DRAW_WIREFRAME = True  # Trueにするとワイヤーフレーム、Falseにすると面を描画
    DRAW_WIREFRAME = False  # Trueにするとワイヤーフレーム、Falseにすると面を描画
    min_height = 0  # 表示する建物の最低高さ

    def __init__(self, z, x, y):
        ShowBase.__init__(self)

        # ウインドウの設定
        self.props = WindowProperties()
        self.props.setTitle('Plateau Building Viewer')
        self.props.setSize(1800, 1200)  # ウインドウサイズは環境に合わせて調整する。
        self.win.requestProperties(self.props)
        self.setBackgroundColor(0, 0, 0)  # ウインドウの背景色を黒 (0, 0, 0) に設定。

        # 全てを配置するノード
        self.world_node = self.render.attachNewNode('world_node')
        self.world_node.setPos(-2048, -2048, 0)
        self.world_node.setScale(0.8119, 0.9245, 1)
        # 透明度属性とブレンディングを有効にする
        self.world_node.setTransparency(TransparencyAttrib.MAlpha)

        # 座標軸を表示する
        self.axis = self.loader.loadModel('zup-axis')
        self.axis.reparentTo(self.render)
        self.axis.setScale(100)  # 座標軸の長さを設定

        # 地面を描画
        self.card = CardMaker('ground')
        self.card.setFrame(0, 4096, 0, 4096)
        self.ground = self.world_node.attachNewNode(self.card.generate())
        self.ground.setP(-90)
        self.ground.setColor(0, 0.5, 0, 0.5)  # 緑色

        # カメラコントローラーを初期化
        self.camera_controller = CameraController(self)

        # ライトの追加
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((1, 1, 1, 1))
        self.render.setLight(self.render.attachNewNode(ambient_light))

        # 全てのビルを配置するノード
        self.buildings_node = self.world_node.attachNewNode('buildings_node')

        # 建物データをロード
        self.building_list = BuildingDataLoader.load_buildings(z, x, y)

        # 建物データから3Dモデルを作成
        building_count = 0
        rect_building_count = 0
        not_rect_building_count = 0
        for building in self.building_list:
            building_count += 1
            # ビル用のノードを作成し、名前をIDに設定
            building.node = self.buildings_node.attachNewNode(str(building.id))

            if building.height < self.min_height:
                continue

            if building.rect_width is not None:
                rect_params = (building.rect_width, building.rect_height, building.rect_angle)
                rect_building_count += 1
                self.create_rect_building(
                    building.node,
                    rect_params,
                    building.centroid,
                    building.height,
                    # color=(0, 1, 1, 0.5),  # シアン色
                    color=building.color,  # シアン色
                    wireframe=self.DRAW_WIREFRAME
                )
            elif building.simplified_coordinates:

                if len(building.simplified_coordinates[0]) >= 4:
                    not_rect_building_count += 1
                    self.create_building(
                        building.node,
                        building.simplified_coordinates,
                        building.height,
                        # color=(1, 0.5, 0, 0.5),  # オレンジ色
                        color=building.color,  # オレンジ色
                        wireframe=self.DRAW_WIREFRAME
                    )
            else:
                # 座標がない場合はスキップ
                continue

        print(f"ビル数: {BuildingDataLoader.all_building_count}")
        print(f"長方形のビル数: {BuildingDataLoader.rect_building_count}")
        print('長方形ではないビル数:', BuildingDataLoader.not_rect_building_count)

        print(f"building_list count: {len(self.building_list)}")
        print(f"Total buildings: {building_count}")
        print(f"Total rect buildings: {rect_building_count}")
        print(f"Total not rect buildings: {not_rect_building_count}")

        print(f'Polygon vertices: {BuildingDataLoader.vertex_count}')
        print(f'Simplified polygon vertices: {BuildingDataLoader.simplified_vertex_count}')

        # Soundクラスを初期化
        self.sound = Sound("sound/Dive_To_Mod.mp3")
        # サウンドの再生を別スレッドで開始
        self.sound_thread = threading.Thread(target=self.sound.play)
        self.sound_thread.start()

        # ビルの高さを更新するタスクを追加
        self.taskMgr.doMethodLater(0.1, self.update_buildings_task, 'UpdateBuildingsTask')

        self.accept('escape', exit)

    def create_rect_building(self, building_node, rect_params, centroid, height, color=(1, 1, 1, 1), wireframe=False):
        # 長方形のジオメトリを作成
        rect_geom = self.create_box_geom(rect_params, color)

        # シーンに新しいノードとしてアタッチ
        rect_geom.reparentTo(building_node)

        # 位置の設定
        rect_geom.setPos(centroid[0], centroid[1], 0)

        # 回転の設定（ヒンジ角度）
        rect_geom.setH(rect_params[2])  # rect_params[2]が回転角度（度単位）

        # ワイヤーフレームと面の切り替え
        if wireframe:
            rect_geom.setRenderModeWireframe()
            rect_geom.setTwoSided(True)
        else:
            rect_geom.setRenderModeFilled()

        # ビルノードの高さを設定
        building_node.setSz(height)

    def create_box_geom(self, rect_params, color=(1, 1, 1, 1)):
        """
        箱型ジオメトリを作成します。
        """
        width = rect_params[0]
        length = rect_params[1]

        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('box', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')

        # キューブの8頂点
        vertices = [
            (-width / 2, -length / 2, 0),
            (width / 2, -length / 2, 0),
            (width / 2, length / 2, 0),
            (-width / 2, length / 2, 0),
            (-width / 2, -length / 2, 1),
            (width / 2, -length / 2, 1),
            (width / 2, length / 2, 1),
            (-width / 2, length / 2, 1),
        ]

        # 各頂点に色を設定（白色）
        for v in vertices:
            vertex.addData3f(*v)
            color_writer.addData4f(*color)

        # 各面を三角形で定義
        triangles = GeomTriangles(Geom.UHStatic)
        # 下面
        triangles.addVertices(0, 1, 2)
        triangles.addVertices(0, 2, 3)
        # 上面
        triangles.addVertices(4, 6, 5)
        triangles.addVertices(4, 7, 6)
        # 前面
        triangles.addVertices(0, 4, 5)
        triangles.addVertices(0, 5, 1)
        # 背面
        triangles.addVertices(3, 2, 6)
        triangles.addVertices(3, 6, 7)
        # 左面
        triangles.addVertices(0, 3, 7)
        triangles.addVertices(0, 7, 4)
        # 右面
        triangles.addVertices(1, 5, 6)
        triangles.addVertices(1, 6, 2)

        geom = Geom(vdata)
        geom.addPrimitive(triangles)
        geom_node = GeomNode('box_geom')
        geom_node.addGeom(geom)
        box_node = NodePath(geom_node)
        return box_node

    def create_building(self, building_node, coords_list, height, color=(1, 1, 1, 1), wireframe=False):
        # print(f"coords count: {len(coords_list[0])}")
        # 上面のポリゴンを作成
        top_geom = self.create_polygon_geom(coords_list, color)
        top_node = GeomNode('top_face')
        top_node.addGeom(top_geom)
        top_node_path = building_node.attachNewNode(top_node)
        top_node_path.setPos(0, 0, 1)  # 基準高さ（=1）分だけ移動

        # 側面を作成
        side_geom = self.create_side_geom(coords_list, color)
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

    def create_side_geom(self, coords_list, color=(1, 1, 1, 1)):
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
            print("Closing polygon")
            coords.append(coords[0])
        else:
            print("Polygon is closed")

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

    def update_buildings_task(self, task):
        if not self.sound.is_playing.is_set() and self.sound.amplitude_queue.empty():
            return Task.done  # サウンドの再生が終了したらタスクを停止

        try:
            # 振幅データを取得
            amplitude = self.sound.amplitude_queue.get_nowait()
        except Empty:
            # 振幅データがまだない場合は次のフレームへ
            return Task.cont

        # 振幅を正規化（0〜1の範囲）
        max_amplitude = 32768  # int16の最大値
        normalized_amplitude = amplitude / max_amplitude

        # 現在の時間を取得
        current_time = globalClock.getFrameTime()

        # 波のパラメータ
        wave_length = 500  # 波の長さ（空間的な波長）
        wave_speed = 2  # 波の速度（値を調整して波の進行速度を変える）
        wave_height_scale = 300  # 波の高さを調整するスケール

        # ビルの高さを更新
        for building in self.building_list:
            x, y = building.centroid
            # 波の位相を計算
            phase = (x + y) / wave_length - wave_speed * current_time
            # 波の高さを計算
            wave_height = normalized_amplitude * math.sin(phase) * wave_height_scale + 100

            # ビルの高さを更新
            if building.node:
                building.node.setSz(max(wave_height, 1))  # 最小高さを1に設定

        return Task.cont  # タスクを継続


if __name__ == '__main__':
    # 渋谷駅のタイル座標
    # ズームレベル 10: x=909, y=403
    # ズームレベル 11: x=1818, y=806
    # ズームレベル 12: x=3637, y=1613
    # ズームレベル 13: x=7274, y=3226
    # ズームレベル 14: x=14549, y=6452
    # ズームレベル 15: x=29099, y=12905
    # ズームレベル 16: x=58199, y=25811

    # タイル座標を指定
    # Z = 10
    # X = 909
    # Y = 403
    # Z = 11
    # X = 1818
    # Y = 806
    # Z = 12
    # X = 3637
    # Y = 1613
    # Z = 13
    # X = 7274
    # Y = 3226
    # Z = 14
    # X = 14549
    # Y = 6452
    # Z = 15
    # X = 29099
    # Y = 12905
    Z = 16
    X = 58199
    Y = 25811

    app = MyApp(Z, X, Y)
    app.run()
