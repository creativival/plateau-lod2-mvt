

class Building:
    def __init__(self, id, coordinates_3d=None, coordinates_4d=None, height=0):
        self.id = id
        self.coordinates_3d = coordinates_3d
        self.coordinates_4d = coordinates_4d
        self.height = height

        # 簡略化した座標を保持する属性
        self.simplified_coordinates_3d = None
        self.simplified_coordinates_4d = None

        # 重心の座標
        self.centroid = None

        # 全ての頂点を含む円の半径
        self.bounding_circle_radius = None

        # ビルノード
        self.building_node = None

    def __str__(self):
        return (f"Building(id={self.id}, height={self.height}, "
                f"centroid={self.centroid}, "
                f"bounding_circle_radius={self.bounding_circle_radius})")

    def __repr__(self):
        return self.__str__()
