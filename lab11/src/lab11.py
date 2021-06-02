import cv2
import time

img_sets = [
    'eiffel_tower',
    'lady_liberty',
    'taipei_101',
]

detector_SURF = cv2.xfeatures2d.SURF_create()
detector_SIFT = cv2.xfeatures2d.SIFT_create()
detector_ORB = cv2.ORB_create()

# Select which img_set and detector to use here
img_set = img_sets[0]
detector = detector_SURF


img1 = cv2.imread(f'../img/{img_set}/1.png')
img2 = cv2.imread(f'../img/{img_set}/2.png')

kp1, des1 = detector.detectAndCompute(img1, None)
kp2, des2 = detector.detectAndCompute(img2, None)

bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda x: x.distance)

# For speed testing
# start_time = time.time()
# for _ in range(100):
#     kp1, des1 = detector.detectAndCompute(img1, None)
#     kp2, des2 = detector.detectAndCompute(img2, None)

#     bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
#     matches = bf.match(des1, des2)
#     matches = sorted(matches, key=lambda x: x.distance)
# end_time = time.time()
# print(end_time - start_time)
########

matching_result = cv2.drawMatches(img1, kp1, img2, kp2, matches[:30], None)

cv2.imshow('matching_result', matching_result)
cv2.waitKey(0)
cv2.destroyAllWindows()
