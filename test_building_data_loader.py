from building.building_data_loader import BuildingDataLoader


if __name__ == '__main__':
    z = 16
    x = 58199
    y = 25811
    building_list = BuildingDataLoader.load_buildings(z, x, y)

    if building_list:
        for building in building_list[:20]:  # 最初の5件を表示
            print(building)
            print(f"Original Coordinates:")
            if building.coordinates_3d:
                print(f"Coordinates 3D: {building.coordinates_3d}")
            if building.coordinates_4d:
                print(f"Coordinates 4D: {building.coordinates_4d}")

            print(f"Simplified Coordinates:")
            if building.simplified_coordinates:
                print(f"Simplified 3D: {building.simplified_coordinates}")
            if building.simplified_coordinates_4d:
                print(f"Simplified 4D: {building.simplified_coordinates_4d}")

            print(f"Centroid: {building.centroid}")
            print(f"Bounding Circle Radius: {building.bounding_circle_radius}")
            print("-----")
    else:
        print("No building data found.")
