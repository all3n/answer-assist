import cv2

# gen qa cut image str
def get_qa_image(screen,height_begin,height_end):
    cutted_image = screen[height_begin:height_end]
    return cv2.imencode('.png', cutted_image)[1].tostring()
