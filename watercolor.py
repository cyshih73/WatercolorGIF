import os, sys
import cv2
import imageio
import subprocess
import numpy as np
from PIL import Image

filename = sys.argv[1].split('.')[0]
fileext = sys.argv[1].split('.')[1]

def Watercolor(f, prefix):
    # Parameters
    average_square = (5, 5)
    sigma_x = 0
    k=20
    line_average = (9, 9)
    line_sigma_x = 0
    multi_w = 0.5
    paint_w = 0.9
    gamma = 1.5
    method = 2

    image = cv2.imread(f, 1)
    file = 'test'
    ext = '.jpg'

    # GaussianBlur
    image_blurring = cv2.GaussianBlur(image, average_square, sigma_x)
    w , h , channel = image_blurring.shape
    image_reshape = np.zeros((w , h ,3), np.uint8)
    image_reshape = image_blurring // k * k
    
    paint = cv2.GaussianBlur(image_reshape, average_square, sigma_x)
    cv2.imwrite(prefix + file + "_paint" + ext, paint)

    image_preprocessed  = cv2.cvtColor(cv2.GaussianBlur(image, line_average, line_sigma_x), cv2.COLOR_BGR2GRAY)

    # Canny
    image_binary = cv2.Canny(image_preprocessed, threshold1 = 50, threshold2 = 55) 
    image_binary = cv2.GaussianBlur(image_binary, average_square, sigma_x)
    res, image_binary = cv2.threshold(image_binary, 90, 255, cv2.THRESH_BINARY_INV)

    cv2.imwrite(prefix + file + "_line" + ext, image_binary)

    # Speedup processes
    w , h , channel = paint.shape
    image_binary = np.where(image_binary > 0, 255, 0)
    image_binary = np.dstack((image_binary, image_binary, image_binary))
    QQ = np.multiply(paint, image_binary) // 255
    result = np.array(QQ, np.uint8)
    
    d = cv2.addWeighted(result, multi_w, paint, paint_w, gamma)
    
    # Output the frame
    cv2.imwrite(prefix + file + "_output" + ext, d)


#For gif
if fileext == "gif":
    # Convert gif into jpgs
    subprocess.call(('convert -verbose -coalesce %s.gif %s.jpg' % (filename, filename)).split())

    # Find number of frames
    SIZE = 0
    while True:
        prefix = filename + "-%d" % SIZE
        f = prefix + '.jpg'
        try:
            fd = open(f, "r")
            SIZE += 1
        except:
            break
    
    # Processing the images
    print("Processing. Please wait.")
    for ID in range(SIZE): 
        prefix = filename + "-%d" % ID
        f = prefix + '.jpg'
        Watercolor(f, prefix)
        print("Frame " + str(ID) + " finished.")

    VALID_EXTENSIONS = ('png', 'jpg')

    # Output the gif
    def create_gif(filenames, duration):
        images = []
        for name in filenames:
            images.append(imageio.imread(name))
        output_file = "" + filename + "_result.gif"
        imageio.mimsave(output_file, images, duration=duration)

    duration = 0.1
    filenames = []
    for i in range(SIZE):
        filenames.append(filename + "-%dtest_output.jpg" % i)
    create_gif(filenames, duration)

    # Cleanup the working directory
    for i in range(SIZE):
        deletion = "" + filename + "-" + str(i)
        os.remove(deletion + ".jpg")
        os.remove(deletion + "test_line" + ".jpg")
        os.remove(deletion + "test_output" + ".jpg")
        os.remove(deletion + "test_paint" + ".jpg")

    print("Working directory cleaned. Exiting.")

# For jpg
else:
    f = filename + '.jpg'
    print("Processing. Please wait.")
    Watercolor(f, filename)
    os.rename("" + filename + "test_output.jpg", "" + filename + "_result.jpg")
    os.remove("" + filename + "test_line" + ".jpg")
    os.remove("" + filename + "test_paint" + ".jpg")
    print("Working directory cleaned. Exiting.")

