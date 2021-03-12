import cv2
import numpy as np

def cal_variance(t, hist_dict):
    nb = 0
    no = 0
    b = 0
    o = 0
    for i in range(256):
        if i < t:
            nb += hist_dict[i]
            b += hist_dict[i] * i
        else:
            no += hist_dict[i]
            o += hist_dict[i] * i
    meanb = b / nb
    meano = o / no
    variance = nb * no * ( (meanb - meano) ** 2 )
    # variance = t * (256 - t) * ( (meanb - meano) ** 2 )
    
    print(t, variance, nb, no, meanb, meano)
    return variance

def main():
    # Read the image
    img = cv2.imread('../img/input.jpg')
    after_img = img.copy()

    hist_dict = np.zeros(256, np.uint32)
    # hist_dict = [1] * 256

    size = 0
    for row in img:
        for pixel in row:
            intensity = np.uint( pixel[0] )
            hist_dict[intensity] += 1
            size += 1

    print(hist_dict)
    s = 0
    for it in hist_dict:
        s += it

    print(size, s)

    max_variance = -1
    best_t = 0
    for t in range(1, 255):
        tmp_variance = cal_variance(t, hist_dict)
        if tmp_variance > max_variance:
            max_variance = tmp_variance
            best_t = t
    print(best_t)
    i = 0
    for row in img:
        j = 0
        for pixel in row:
            intensity = int( pixel[0] )
            if intensity > best_t:
                after_img[i][j] = 255
            else:
                after_img[i][j] = 0
            j += 1
        i += 1

    # Display the image
    cv2.imshow('image', after_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()