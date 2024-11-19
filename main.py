from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from building.data_loader import DataLoader
from building.camera import CameraController
import threading
import math
from building.sound import Sound
from building.geometry_generator import GeometryGenerator
from direct.task import Task
from queue import Empty


class MyApp(ShowBase):
    # ワイヤーフレームモードを切り替えるフラグ
    # DRAW_WIREFRAME = True  # Trueにするとワイヤーフレーム、Falseにすると面を描画
    DRAW_WIREFRAME = False  # Trueにするとワイヤーフレーム、Falseにすると面を描画
    min_height = 0  # 表示する建物の最低高さ
    # SOUND_PATH = 'sound/Dive_To_Mod.mp3'
    IMAGE_PATH = 'images/flag_japan.png'
    SOUND_PATH = 'sound/kimigayo.mp3'
    IMAGE_PATH = 'images/flag_usa.png'
    SOUND_PATH = 'sound/star_spangled_banner.mp3'
    IMAGE_PATH = 'images/rocky.png'
    SOUND_PATH = 'sound/rocky_thema.mp3'

    def __init__(self, z, x, y):
        ShowBase.__init__(self)

        # ウインドウの設定
        self.props = WindowProperties()
        self.props.setTitle('Plateau Sound Visualization')
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
        self.ground.setColor(0, 0.5, 0, 0.3)  # 緑色

        # カメラコントローラーを初期化
        self.camera_controller = CameraController(self)

        # ライトの追加
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((1, 1, 1, 1))
        self.render.setLight(self.render.attachNewNode(ambient_light))

        # 全てのビルを配置するノード
        self.buildings_node = self.world_node.attachNewNode('buildings_node')

        # 建物データをロード
        self.building_list = DataLoader(z, x, y, self.IMAGE_PATH).load_building_list()

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
                GeometryGenerator.create_rect_building(
                    building.node,
                    rect_params,
                    building.centroid,
                    building.height,
                    color=building.color,
                    wireframe=self.DRAW_WIREFRAME
                )
            elif building.simplified_coordinates:
                if len(building.simplified_coordinates[0]) >= 4:
                    GeometryGenerator.create_building(
                        building.node,
                        building.simplified_coordinates,
                        building.height,
                        color=building.color,
                        wireframe=self.DRAW_WIREFRAME
                    )
            else:
                # 座標がない場合はスキップ
                continue

        print(f"ビル数: {DataLoader.all_building_count}")
        print(f"長方形のビル数: {DataLoader.rect_building_count}")
        print('長方形ではないビル数:', DataLoader.not_rect_building_count)

        print(f"building_list count: {len(self.building_list)}")
        print(f"Total buildings: {building_count}")
        print(f"Total rect buildings: {rect_building_count}")
        print(f"Total not rect buildings: {not_rect_building_count}")

        print(f'Polygon vertices: {DataLoader.vertex_count}')
        print(f'Simplified polygon vertices: {DataLoader.simplified_vertex_count}')

        # Soundクラスを初期化
        self.sound = Sound(self.SOUND_PATH)
        # サウンドの再生を別スレッドで開始
        self.sound_thread = threading.Thread(target=self.sound.play)
        self.sound_thread.start()

        # ビルの高さを更新するタスクを追加
        self.taskMgr.doMethodLater(0.1, self.update_buildings_task, 'UpdateBuildingsTask')

        self.accept('escape', exit)

    def update_buildings_task(self, task):
        if not self.sound.is_playing.is_set() and self.sound.amplitude_queue.empty():
            return Task.done  # サウンドの再生が終了したらタスクを停止

        try:
            # 振幅データを取得
            amplitude = self.sound.amplitude_queue.get_nowait()
        except Empty:
            # 振幅データがまだない場合は次のフレームへ
            return task.cont

        # 振幅を正規化（0〜1の範囲）
        max_amplitude = 32768  # int16の最大値
        normalized_amplitude = amplitude / max_amplitude

        # 現在の時間を取得
        current_time = globalClock.getFrameTime()

        # 波のパラメータ
        wave_length = 500  # 波の長さ（空間的な波長）
        wave_speed = 2  # 波の速度（値を調整して波の進行速度を変える）
        wave_height_scale = 500  # 波の高さを調整するスケール

        # ビルの高さを更新
        for building in self.building_list:
            x, y = building.centroid
            # 波の位相を計算
            # phase = (x + y) / wave_length - wave_speed * current_time
            phase = math.sqrt((x - 2048) ** 2 + (y - 2048) ** 2) / wave_length - wave_speed * current_time
            # phase = x / wave_length - wave_speed * current_time
            # 波の高さを計算
            wave_height = normalized_amplitude * math.sin(phase) * wave_height_scale + 100

            # ビルの高さを更新
            if building.node:
                building.node.setSz(max(wave_height, 1))  # 最小高さを1に設定

        return task.cont  # タスクを継続


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
