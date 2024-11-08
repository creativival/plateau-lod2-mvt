from direct.showbase.DirectObject import DirectObject
from panda3d.core import WindowProperties, CollisionTraverser, CollisionNode, CollisionHandlerPusher, CollisionRay, \
    BitMask32
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import CollisionSphere


class CameraController(DirectObject):
    heading_angular_velocity = 1500
    pitch_angular_velocity = 500
    max_pitch_angle = 60
    min_pitch_angle = -30

    def __init__(self, base):
        self.base = base
        self.camera = base.camera
        self.render = base.render
        self.mode = 'external'  # 'external' または 'internal'

        # カメラの初期設定
        self.setup_cameras()

        # キー入力のマッピング
        self.accept('c', self.toggle_mode)  # 'c'キーでカメラモードを切り替え

        # 移動用の変数
        self.key_map = {"forward": False, "backward": False, "left": False, "right": False,
                        "up": False, "down": False}
        self.mouse_sensitivity = 0.2

        # キー入力の受付
        self.accept('w', self.set_key, ['forward', True])
        self.accept('w-up', self.set_key, ['forward', False])
        self.accept('s', self.set_key, ['backward', True])
        self.accept('s-up', self.set_key, ['backward', False])
        self.accept('a', self.set_key, ['left', True])
        self.accept('a-up', self.set_key, ['left', False])
        self.accept('d', self.set_key, ['right', True])
        self.accept('d-up', self.set_key, ['right', False])
        self.accept('q', self.set_key, ['up', True])
        self.accept('q-up', self.set_key, ['up', False])
        self.accept('e', self.set_key, ['down', True])
        self.accept('e-up', self.set_key, ['down', False])

        # マウスの初期設定
        self.disable_mouse_control()
        self.prev_mouse_pos = (0, 0)

        # タスクの追加
        self.base.taskMgr.add(self.update, 'camera_update_task')

    def setup_cameras(self):
        # 外部カメラの設定
        if self.mode == 'external':
            self.base.disableMouse()  # デフォルトのカメラコントロールを無効化
            self.camera.setPos(2048, -5000, 2048)  # 上空にカメラを配置
            self.camera.lookAt(0, 0, 0)
            self.enable_mouse_control()  # マウスでカメラを回転できるようにする
        # 内部カメラの設定
        elif self.mode == 'internal':
            self.base.disableMouse()
            self.camera.setPos(0, 0, 1.6)  # 地面上にカメラを配置
            self.camera.setHpr(0, 0, 0)
            self.disable_mouse_control()
            # self.prev_mouse_pos = None

    def toggle_mode(self):
        if self.mode == 'external':
            self.mode = 'internal'
            self.setup_cameras()
        else:
            self.mode = 'external'
            self.setup_cameras()

    def set_key(self, key, value):
        self.key_map[key] = value

    def enable_mouse_control(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)
        self.base.win.movePointer(0, int(self.base.win.getProperties().getXSize() / 2),
                                  int(self.base.win.getProperties().getYSize() / 2))
        self.prev_mouse_pos = None

    def disable_mouse_control(self):
        props = WindowProperties()
        props.setCursorHidden(False)
        self.base.win.requestProperties(props)

    def update(self, task):
        dt = globalClock.getDt()
        if self.mode == 'internal':
            self.control_camera(dt)
        elif self.mode == 'external':
            self.control_external_camera(dt)
        return task.cont

    def control_camera(self, dt):
        # キー入力による移動
        speed = 200 * dt
        x_direction = self.camera.getMat().getRow3(0)
        y_direction = self.camera.getMat().getRow3(1)
        camera_x, camera_y, camera_z = self.camera.getPos()

        if self.key_map['forward']:
            camera_x = camera_x + y_direction.x * speed
            camera_y = camera_y + y_direction.y * speed
        if self.key_map['backward']:
            camera_x = camera_x - y_direction.x * speed
            camera_y = camera_y - y_direction.y * speed
        if self.key_map['left']:
            camera_x = camera_x - x_direction.x * speed
            camera_y = camera_y - x_direction.y * speed
        if self.key_map['right']:
            camera_x = camera_x + x_direction.x * speed
            camera_y = camera_y + x_direction.y * speed

        self.camera.setPos(camera_x, camera_y, camera_z)

        # マウスによる視点の回転
        if self.base.mouseWatcherNode.hasMouse():
            x = self.base.mouseWatcherNode.getMouseX()
            y = self.base.mouseWatcherNode.getMouseY()
            if self.prev_mouse_pos is not None:
                dx = x - self.prev_mouse_pos[0]
                dy = y - self.prev_mouse_pos[1]
                heading = self.camera.getH() - dx * CameraController.heading_angular_velocity * speed
                pitch = self.camera.getP() + dy * CameraController.pitch_angular_velocity * speed
                pitch = min(CameraController.max_pitch_angle, max(CameraController.min_pitch_angle, pitch))
                self.camera.setH(heading)
                self.camera.setP(pitch)
            self.prev_mouse_pos = (x, y)

    def control_external_camera(self, dt):
        # キー入力による移動
        speed = 500 * dt
        if self.key_map['forward']:
            self.camera.setY(self.camera, speed)
        if self.key_map['backward']:
            self.camera.setY(self.camera, -speed)
        if self.key_map['left']:
            self.camera.setX(self.camera, -speed)
        if self.key_map['right']:
            self.camera.setX(self.camera, speed)
        if self.key_map['up']:
            self.camera.setZ(self.camera.getZ() + speed)
        if self.key_map['down']:
            self.camera.setZ(self.camera.getZ() - speed)

        # マウスによるカメラの回転
        if self.base.mouseWatcherNode.hasMouse():
            x = self.base.mouseWatcherNode.getMouseX()
            y = self.base.mouseWatcherNode.getMouseY()
            if self.prev_mouse_pos is not None:
                dx = x - self.prev_mouse_pos[0]
                dy = y - self.prev_mouse_pos[1]
                self.camera.setH(self.camera.getH() - dx * 100 * self.mouse_sensitivity)
                self.camera.setP(self.camera.getP() - dy * 100 * self.mouse_sensitivity)
            self.prev_mouse_pos = (x, y)
