import csv
import numpy as np
import matplotlib.pyplot as plt

orbslam2_data_path = '../data/orbslam2_testing_path_xyz.csv'
colmap_data_path = '../data/colmap_testing_path_xyz.csv'
match_p_idx = {'orb': 0, 'col': 3}

def read_dataset():
    points = {'orb': [], 'col': []}
    matches = {}
    col_match_ps_idx = []
    orb_match_ps_idx = []

    with open(orbslam2_data_path, newline='') as csvfile:
        orbslam2_data = list(csv.reader(csvfile))
    with open(colmap_data_path, newline='') as csvfile:
        colmap_data = list(csv.reader(csvfile))

    for i, row in enumerate(orbslam2_data):
        points['orb'].append(
            [float(val) for val in row[1:]])
        abosolute_i = int(row[0])
        if abosolute_i in matches:
            matches[abosolute_i]['orb'] = i
        else:
            matches[abosolute_i] = {'orb': i}

    for i, row in enumerate(colmap_data):
        points['col'].append(
            [float(val) for val in row[1:]])
        abosolute_i = int(row[0])
        if abosolute_i in matches:
            matches[abosolute_i]['col'] = i
        else:
            matches[abosolute_i] = {'col': i}

    for method in points:
        points[method] = np.array(points[method])

    for row in matches:
        match = matches[row]
        if 'orb' in match and 'col' in match:
            orb_match_ps_idx.append(match['orb'])
            col_match_ps_idx.append(match['col'])
    orb_match_ps_idx.sort()
    col_match_ps_idx.sort()
    
    return points, orb_match_ps_idx, col_match_ps_idx


def rotation_mtx(axis, angle):
    axis = np.array(axis)
    u = axis / np.linalg.norm(axis)
    cos = np.cos(angle)
    sin = np.sin(angle)
    c = 1 - cos
    ux, uy, uz = u[0], u[1], u[2]

    R = np.array(
        [[cos + ux**2 * c, ux * uy * c - uz * sin, ux * uz * c + uy * sin],
         [uy * ux * c + uz * sin, cos + uy**2 * c, uy * uz * c - ux * sin],
         [uz * ux * c - uy * sin, uz * uy * c + ux * sin, cos + uz**2 * c]]
    )

    return R


def get_angle(vec1, vec2):
    cos_val = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return np.arccos(cos_val)


def plot(pts_ORB, pts_COL):
    fig = plt.figure()
    ax = plt.axes(projection='3d')

    ax.scatter3D(pts_ORB[:, 0], pts_ORB[:, 1], pts_ORB[:, 2],
                 c=[i for i in range(len(pts_ORB))], cmap='Reds')
    # ax.plot3D(pts_ORB[:, 0], pts_ORB[:, 1], pts_ORB[:, 2], color='green', label='ORB_SLAM2')
    ax.plot3D(pts_COL[:, 0], pts_COL[:, 1], pts_COL[:, 2], color='gray', label='COLMAP')
    ax.legend()
    plt.show()


if __name__ == "__main__":
    points, orb_match_ps_idx, col_match_ps_idx = read_dataset()
    print(orb_match_ps_idx)
    print(col_match_ps_idx)
    print(0, points['orb'][match_p_idx['orb']], points['col'][match_p_idx['col']])

    points['orb'] -= np.mean(points['orb'], axis=0)
    points['col'] -= np.mean(points['col'], axis=0)

    scale = np.sqrt((
        np.sum(np.square(points['col'][col_match_ps_idx[0]])) /
        np.sum(np.square(points['orb'][orb_match_ps_idx[0]]))
    ))
    points['orb'] *= scale

    print(1, points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])

    axis = [0, 0, 1]
    ang = get_angle(points['orb'][orb_match_ps_idx[0]][:2], points['col'][col_match_ps_idx[0]][:2])
    rot_mtx = rotation_mtx(axis, ang)
    points['orb'] = np.matmul(rot_mtx, points['orb'].T).T
    
    print(2, points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])

    axis = [points['orb'][orb_match_ps_idx[0]][1], -points['orb'][orb_match_ps_idx[0]][0], 0]
    ang = get_angle(points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])
    rot_mtx = rotation_mtx(axis, ang)
    points['orb'] = np.matmul(rot_mtx, points['orb'].T).T

    print(3, points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])
    print(4, points['orb'][orb_match_ps_idx[1]], points['col'][col_match_ps_idx[1]])

    axis = points['orb'][orb_match_ps_idx[0]]
    ang = get_angle(points['orb'][orb_match_ps_idx[5]], points['col'][col_match_ps_idx[5]])
    rot_mtx = rotation_mtx(axis, ang)
    points['orb'] = np.matmul(rot_mtx, points['orb'].T).T

    print(5, points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])
    print(6, points['orb'][orb_match_ps_idx[1]], points['col'][col_match_ps_idx[1]])

    plot(points['orb'], points['col'])
