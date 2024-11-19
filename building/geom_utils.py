from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles, Geom, GeomNode, NodePath


def create_box_geom(rect_params, color=(1, 1, 1, 1)):
    """
    箱型ジオメトリを作成します。
    """
    width, length = rect_params[0], rect_params[1]

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

    # 各頂点に色を設定
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


def create_polygon_geom(coords_list, color=(1, 1, 1, 1)):
    """
    上面のポリゴンのジオメトリを作成します。
    """
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


def create_side_geom(coords_list, color=(1, 1, 1, 1)):
    """
    側面のジオメトリを作成します。
    """
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
        vertex.addData3f(x1, y1, 1)
        color_writer.addData4f(*color)
        vertex.addData3f(x2, y2, 1)
        color_writer.addData4f(*color)

        # 二つの三角形で四角形を構成
        tris.addVertices(idx, idx + 2, idx + 1)
        tris.addVertices(idx + 1, idx + 2, idx + 3)
        tris.closePrimitive()
        idx += 4

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    return geom
