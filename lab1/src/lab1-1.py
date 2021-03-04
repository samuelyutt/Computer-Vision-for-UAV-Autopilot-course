import cv2
import numpy as np

# Read the image
img_kobe = cv2.imread('../img/kobe.jpg')

# Reverse the image row by row
row_idx = 0
for row in img_kobe:
    img_kobe[row_idx] = row[::-1]
    row_idx += 1

# Display the flipped image
cv2.imshow('Flipped image', img_kobe)
cv2.waitKey(0)
cv2.destroyAllWindows()
