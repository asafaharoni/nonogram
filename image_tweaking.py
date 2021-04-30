import cv2

if __name__ == '__main__':
    im = cv2.imread(r'data\images\maayan.greyscale.jpeg', cv2.IMREAD_GRAYSCALE)
    thresh = 200
    im_res = cv2.resize(im, (70, 77))
    img_binary = cv2.threshold(im_res, thresh, 255, cv2.THRESH_BINARY)[1]
    cv2.imwrite(r'data\images\maayan.bw.small.png', img_binary)
