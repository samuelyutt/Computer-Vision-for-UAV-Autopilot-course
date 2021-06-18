import csv
import numpy as np
import matplotlib.pyplot as plt

orbslam2_data_path = '../data/orbslam2_testing_path_xyz.csv'
colmap_data_path = '../data/colmap_testing_path_xyz.csv'


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
    # Read datasets and find matches
    points, orb_match_ps_idx, col_match_ps_idx = read_dataset()
    print(0, points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])

    # Move each center of models to the origin
    origin_col_mean = np.mean(points['col'], axis=0)
    points['orb'] -= np.mean(points['orb'], axis=0)
    points['col'] -= origin_col_mean

    # Scale ORB_SLAM2 model to the size of COLMOP model
    scale = (np.linalg.norm(points['col'][col_match_ps_idx[0]]) /
             np.linalg.norm(points['orb'][orb_match_ps_idx[0]]))
    points['orb'] *= scale

    print(1, points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])

    # Rotate around z-axis
    # Make the projection of ORB_SLAM2 p0 to XY-plane the same as the projection of COLMAP p0 to XY-plane
    axis = [0, 0, 1]
    ang = get_angle(points['orb'][orb_match_ps_idx[0]][:2], points['col'][col_match_ps_idx[0]][:2])
    rot_mtx = rotation_mtx(axis, ang)
    points['orb'] = np.matmul(rot_mtx, points['orb'].T).T

    print(2, points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])

    # Rotate around a vector on XY-plane orthogonal to the projection vector of ORB_SLAM2 p0 to XY-plane
    # Make ORB_SLAM2 p0 the same as COLMAP p0
    axis = [points['orb'][orb_match_ps_idx[0]][1], -points['orb'][orb_match_ps_idx[0]][0], 0]
    ang = get_angle(points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])
    rot_mtx = rotation_mtx(axis, ang)
    points['orb'] = np.matmul(rot_mtx, points['orb'].T).T

    print(3, points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])
    print(4, points['orb'][orb_match_ps_idx[1]], points['col'][col_match_ps_idx[1]])

    # Rotate around ORB_SLAM2 p0 vector
    # Make ORB_SLAM2 p20 close to COLMAP p20
    axis = points['orb'][orb_match_ps_idx[0]]
    ang = get_angle(points['orb'][orb_match_ps_idx[20]], points['col'][col_match_ps_idx[20]])
    rot_mtx = rotation_mtx(axis, ang)
    points['orb'] = np.matmul(rot_mtx, points['orb'].T).T

    print(5, points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])
    print(6, points['orb'][orb_match_ps_idx[1]], points['col'][col_match_ps_idx[1]])

    # Move back to original COLMAP model coordinates
    points['orb'] += origin_col_mean
    points['col'] += origin_col_mean

    print(7, points['orb'][orb_match_ps_idx[0]], points['col'][col_match_ps_idx[0]])

    # Calcualte errors and statistics
    error_vecs = np.subtract(
        [points['orb'][i] for i in orb_match_ps_idx],
        [points['col'][i] for i in col_match_ps_idx]
    )
    error_dists = np.linalg.norm(error_vecs, axis=1)
    mean_square_error = np.mean(error_dists)
    print(mean_square_error)

    # Plot both models
    plot(points['orb'], points['col'])
