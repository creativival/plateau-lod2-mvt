# plateau-lod2-mvt

```
{
  "id": 10000,
  "coordinates": [[[[4176, 718], [4176, 712], [4096, 678], [4047, 657], [3943, 898], [3959, 905], [3961, 901], [3949, 896], [4049, 663], [4096, 684], [4176, 718]]], [[[4176, 1290], [4096, 1257], [4087, 1253], [4096, 1232], [4096, 1229], [4092, 1228], [4080, 1255], [4096, 1262], [4176, 1295], [4176, 1290]]]],
  "height": 123
}
```



















[3D都市モデル（Project PLATEAU）東京都23区（CityGML 2020年度）](https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-citygml-2020) で
公開されている CityGML データのうち、建築物 (bldg:Building) について Mapbox Vector Tile 形式に変換したデータセットです。

<https://github.com/indigo-lab/plateau-tokyo23ku-building-mvt-2020> との違いは以下の通りです。

- LOD2 が整備されている建物については、LOD2 からデータを生成しています
- 属性情報は z のみに限定されています


# デモ

## 積み木調

<https://indigo-lab.github.io/plateau-lod2-mvt/>

[![plateau-lod2-mvt](https://repository-images.githubusercontent.com/438873495/0bb4e945-c215-49a5-b98d-7f51d20062f8)](https://indigo-lab.github.io/plateau-lod2-mvt/)

## 木目調

<https://indigo-lab.github.io/plateau-lod2-mvt/wood.html>

[![wood](https://user-images.githubusercontent.com/8913051/148005895-73bcae05-30f2-4faf-a9e1-221866b95a3f.png)](https://indigo-lab.github.io/plateau-lod2-mvt/wood.html)

※ テクスチャとして [Tiny Texture Pack: 25 Wood Textures (CC0 Public Domain)](https://opengameart.org/content/tiny-texture-pack) を使用しています。

# タイル仕様

URL         | <https://indigo-lab.github.io/plateau-lod2-mvt/{z}/{x}/{y}.pbf>
----------- | -----------------------------------------------------------------------------------
データソース  | [3D都市モデル（Project PLATEAU）東京都23区（CityGML 2020年度）](https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-citygml-2020)
ズームレベル  | 10〜16 (※)
作成日時     | 2021年12月17日

※ 10〜15のズームレベルでは個々の pbf ファイルが 500kbytes 以内に収まるように、比較的小さな建築物を間引く処理が行われています


## レイヤー定義

以下のレイヤーを含んでいます。

source-layer | description
------------ | --------------------------------------------
bldg         | 建築物 (bldg:Building) を収納したレイヤー


## ジオメトリ情報

ジオメトリ情報は、ソースの CityGML を以下のルールで処理して作成したものです。

- bldg:Building 配下に bldg:RoofSurface および bldg:GroundSurface がある場合には、 bldg:RoofSurface 配下の gml:Polygon ひとつに対してひとつの GeoJSON Polygon を生成する
- そうでない場合には bldg:lod0RoofEdge または bldg:lod0FootPrint 配下の gml:Polygon ひとつに対してひとつの GeoJSON Polygon を生成する

また、ズームレベルに応じた座標値の丸めが行われていることにも注意してください。

## 属性情報

属性情報は z (建物高さに相当、単位はメートル) のみを収録しています。以下のルールで作成されています。

- bldg:RoofSurface をソースとする場合は、`(bldg:RoofSurface 配下の exterior polygon の z値の最大値と最小値の平均) - (bldg:GroundSurface 配下の exterior polygon の z値の最大値と最小値の平均)` を算出して z に設定します
- bldg:lod0RoofEdge または bldg:lod0FootPrint をソースとする場合は、所属する `bldg:Building` に設定された `bldg:measuredHeight` の値を採用します。
- もし `bldg:Building` に `bldg:measuredHeight` が設定されていない場合には `0` を設定します


# ライセンス

本データセットは [CC-BY-4.0](LICENSE) で提供されます。
使用の際にはこのレポジトリへのリンクを提示してください。

また、本データセットは [3D都市モデル（Project PLATEAU）東京都23区（CityGML 2020年度）](https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-citygml-2020) を
加工して作成したものです。
本データセットの使用・加工にあたっては、[PLATEAU Policy](https://www.mlit.go.jp/plateau/site-policy/) を確認し、権利者の権利を侵害しないように留意してください。

# 技術情報

## tippecanoe

本データセットは CityGML から独自に生成した GeoJSON Text Sequences を [tippecanoe](https://github.com/mapbox/tippecanoe) で MVT に変換したものです。

tippecanoe に設定したオプションは以下の通りです。

```sh
$ bzcat geojson.bz2 | tippecanoe --no-tile-compression -ad -an -Z10 -z16 -e dist -l bldg -ai
```

## maplibre-gl-js

デモページでの MVT の表示には [maplibre-gl-js](https://github.com/maplibre/maplibre-gl-js) を使っています。

# 更新履歴

## 2021-12-24

- 初版公開

## 2022-01-04

- 木目調デモを追加
