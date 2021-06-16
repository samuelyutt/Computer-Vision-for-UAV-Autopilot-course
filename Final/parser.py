import numpy as np
import matplotlib.pyplot as plt

def readORB_SLAM(file):
    pts = []
    with open(file, 'r') as f:
        s = [float(val) for val in f.readline().split()]
        while len(s) != 0:
            x, y, z = s[1], s[2], s[3]
            pts.append(np.array([x, y, z]))
            s = [float(val) for val in f.readline().split()]
    return pts

def readCOL_MAP(file):
    truth, pts = [], []
    with open(file, 'r') as f:
        # Header
        for i in range(3):
            f.readline()
        
        # Ground truth
        for i in range(175):
            s = f.readline().split()
            x, y, z = float(s[6]), float(s[7]), float(s[8])
            truth.append(np.array([x, y, z]))
            
        # Testing
        s = f.readline().split()
        while len(s) != 0:
            rw, rx, ry, rz = float(s[2]), float(s[3]), float(s[4]), float(s[5])
            x, y, z = float(s[6]), float(s[7]), float(s[8])
            pts.append(np.array([x, y, z]))
            s = f.readline().split()
            
    return truth, pts  

def axisTransform(pts):
    anchor = pts[3]
    d = np.array([-anchor[0], -anchor[1], -anchor[2]])
    for p in pts:
        p += d

def plot(pts_ORB, pts_COL):
    fig = plt.figure()
    ax = fig.gca(projection='3d')    
    ax.scatter(pts_ORB[:, 0], pts_ORB[:, 1], pts_ORB[:, 2],
               c=pts_ORB[:, 2], cmap='Reds', label='ORB_SLAM')
    
    ax.plot(pts_COL[:, 0], pts_COL[:, 1], pts_COL[:, 2], color='gray', label='COL_MAP')
    #ax.scatter(pts_COL[:, 0], pts_COL[:, 1], pts_COL[:, 2],
    #           c=pts_COL[:, 2], cmap='Blues', label='My Points 2')
    ax.legend()    
    plt.show()

if __name__ == "__main__":
    KeyFrame_file = 'C:/Users/user/Desktop/dataset/KeyFrameTrajectory.txt'
    nvm_file = 'C:/Users/user/Desktop/dataset/colmap_model.nvm'
    
    pts_ORB = readORB_SLAM(KeyFrame_file)
    ground_truth, pts_COL = readCOL_MAP(nvm_file)
    
    axisTransform(pts_COL)
    
    plot(np.array(pts_ORB), np.array(pts_COL))