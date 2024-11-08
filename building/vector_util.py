from math import acos, atan2, sin, cos, degrees, radians, sqrt
import numpy as np


def convert_to_polar(x, y, z):
  """直交座標系から極座標系に変換する"""
  r = sqrt(x ** 2 + y ** 2 + z ** 2)  # ここから（1）
  theta = degrees(acos(z / r))
  phi = degrees(atan2(y, x))
  return r, theta, phi  # ここまで（1）


def convert_to_cartesian(r, theta, phi):
  """極座標系から直交座標系に変換する"""
  rad_theta, rad_phi = radians(theta), radians(phi)  # ここから（2）
  x = r * sin(rad_theta) * cos(rad_phi)
  y = r * sin(rad_theta) * sin(rad_phi)
  z = r * cos(rad_theta)
  return x, y, z  # ここまで（2）


def get_point_from_rotated_coordinates(x, y, z, heading, pitch, roll):
  """回転した座標系からみた点の座標を計算する"""
  reverse_heading_rad = -radians(heading)  # ここから（3）
  reverse_pitch_rad = -radians(pitch)
  reverse_roll_rad = -radians(roll)

  # Z軸周りの回転行列
  heading_rotation_matrix = np.array([
    [cos(reverse_heading_rad), -sin(reverse_heading_rad), 0],
    [sin(reverse_heading_rad), cos(reverse_heading_rad), 0],
    [0, 0, 1]
  ])

  # X軸周りの回転行列
  pitch_rotation_matrix = np.array([
    [1, 0, 0],
    [0, cos(reverse_pitch_rad), -sin(reverse_pitch_rad)],
    [0, sin(reverse_pitch_rad), cos(reverse_pitch_rad)]
  ])

  # Y軸周りの回転行列
  roll_rotation_matrix = np.array([
    [cos(reverse_roll_rad), 0, sin(reverse_roll_rad)],
    [0, 1, 0],
    [-sin(reverse_roll_rad), 0, cos(reverse_roll_rad)]
  ])

  # 回転行列を合成 (roll -> pitch -> heading の順)
  rotation_matrix = np.dot(roll_rotation_matrix, np.dot(pitch_rotation_matrix, heading_rotation_matrix))

  # 点の座標を行列に変換
  point = np.array([x, y, z])

  # 逆回転行列を適用
  return rotation_matrix.dot(point)  # ここまで（3）
