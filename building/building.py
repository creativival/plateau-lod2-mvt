

class Building:
    def __init__(self, id, coordinates=None, height=0):
        self.id = id
        self.coordinates = coordinates
        self.height = height

        # 簡略化した座標を保持する属性
        self.simplified_coordinates = None

        # 長方形に簡略化した座標を保持する属性
        self.rect_width = None
        self.rect_height = None
        self.rect_angle = None

        # 重心の座標
        self.centroid = None

        # 全ての頂点を含む円の半径
        self.bounding_circle_radius = None

        # ビルノード
        self.building_node = None

    def __str__(self):
        return (f"Building(id={self.id}, height={self.height}, "
                f"centroid={self.centroid}, "
                f"bounding_circle_radius={self.bounding_circle_radius})"
                f"Rectangle - Width: {self.rect_width}, Height: {self.rect_height}, Angle: {self.rect_angle}")

    def __repr__(self):
        return self.__str__()
