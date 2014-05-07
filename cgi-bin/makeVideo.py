# Python module that can be used to create videos of land cover type maps - currently the CV2 library is not installed or working properly 10/2/2014
import glob, cv2
print "Creating video.."
images = glob.glob ('/srv/www/htdocs/mstmp/landsat_*.png')
img = cv2.imread(images[0])
height , width , layers = img.shape
video = cv2.VideoWriter('/srv/www/htdocs/mstmp/video.avi', -1, 1, (width, height))
for image in images:
    video.write(cv2.imread(image))
cv2.destroyAllWindows()  # giving an error at the moment
video.release()