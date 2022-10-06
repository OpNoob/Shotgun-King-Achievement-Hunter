import time

import os
from image_similarity_measures.quality_metrics import rmse, ssim, sre
import numpy as np
import cv2
from mss import mss
from win32gui import FindWindow, GetWindowRect, SetForegroundWindow, IsWindowVisible, GetWindowText, GetForegroundWindow
import estimate

"""
https://stackoverflow.com/questions/35097837/capture-video-data-from-screen-in-python
"""

game = estimate.GameData()

data_dir_pos = 'Game Data/Positive'
data_dir_neg = 'Game Data/Negative'
files_pos = {f.replace(".png", "").replace("_", " ").replace("%", "'"): os.path.join(data_dir_pos, f) for f in
             os.listdir(data_dir_pos) if f.endswith(".png")}
files_neg = {f.replace(".png", "").replace("_", " ").replace("%", "'"): os.path.join(data_dir_neg, f) for f in
             os.listdir(data_dir_neg) if f.endswith(".png")}
files = {**files_pos, **files_neg, None: "Game Data/Empty.png"}
cards_pos = list(files_pos.keys())
cards_neg = list(files_neg.keys())

# Getting opencv images
file_data = dict()
dim = (210, 290)
for name, img_path in files.items():
    data_img = cv2.imread(img_path)
    resized_img = cv2.resize(data_img, dim, interpolation=cv2.INTER_AREA)
    file_data[name] = resized_img


def findMatch(input_image):
    input_image = cv2.resize(input_image, dim, interpolation=cv2.INTER_AREA)

    rmse_measures = {}

    for image_name, image_data in file_data.items():
        rmse_measures[image_name] = rmse(input_image, image_data)

    return min(rmse_measures, key=rmse_measures.get)


window_text = "Shotgun King"
window_handle = FindWindow(None, window_text)


def getFrame(resize_to: tuple[int, int] = None):
    SetForegroundWindow(window_handle)
    time.sleep(0.1)
    window_rect = GetWindowRect(window_handle)
    bounding_box = {'top': window_rect[1], 'left': window_rect[0], 'width': window_rect[2] - window_rect[0],
                    'height': window_rect[3] - window_rect[1]}
    sct = mss()

    sct_img = sct.grab(bounding_box)
    frame = np.array(sct_img)[:, :, :3]

    if resize_to is None:
        return frame
    else:
        return cv2.resize(frame, resize_to, interpolation=cv2.INTER_AREA)


def extractCards(show_updates=False, resolution_type=None, gui_queue=None):
    """
    Gets frame and analyses.  This interacts with the GUI.

    :param show_updates: Showing updates such as prints
    :param resolution_type: Options["1080p", None].
    :param gui_queue: Adds data to inputted queue
    :return: Either the choice or all the gathered data as well
    """
    frame = getFrame()

    data_tuple = findCards(frame, show_res=show_updates, typ=resolution_type)
    if gui_queue is not None:
        gui_queue.put(data_tuple)

    return data_tuple


def crop(image):
    y_nonzero, x_nonzero, _ = np.nonzero(image)
    return image[np.min(y_nonzero):np.max(y_nonzero), np.min(x_nonzero):np.max(x_nonzero)]


def findCards(frame, show_res=False, typ="1080p"):
    """
    Returns all found cards from image

    :param frame: Input frame in BGR form
    :param show_res: boolean to show result as print
    :param typ: Options["1080p", None].  With type "1080p", uses the normal 1080p resolution, while None will use the default resolution.
    :return:
    """

    resized = cv2.resize(frame, (700, 400), interpolation=cv2.INTER_AREA)
    # resized = cv2.resize(frame, (350, 200), interpolation=cv2.INTER_AREA)

    height, width, _ = resized.shape

    # Owned cards
    if typ is None:
        card_height = int(0.165 * height)
        card_width = int(0.07 * width)

        card_height_shove = int(0.015 * height)
        card_width_shove = int(0.009 * width)

        pos_col = int(0.0254 * width)
        neg_col = int(0.827 * width)  # int(0.905 * width)
        start_row = int(0.065 * height)
    elif typ == "1080p":
        card_height = int(0.175 * height)
        card_width = int(0.069 * width)

        card_height_shove = int(0.008 * height)
        card_width_shove = int(0.008 * width)

        pos_col = int(0.049 * width)
        neg_col = int(0.805 * width)
        start_row = int(0.05 * height)
    else:
        return

    # Grid section
    card_found_buffs = list()
    card_found_nerfs = list()
    # cards_found = list()
    for i in range(5):
        for j in range(2):
            card_image = resized[start_row + i * (card_height_shove + card_height):start_row + card_height + i * (
                    card_height_shove + card_height),
                         pos_col + j * (card_width + card_width_shove):pos_col + card_width + j * (
                                 card_width + card_width_shove)]
            # cards_found.append(findMatch(card_image))
            card_found_buffs.append(findMatch(card_image))
    for i in range(5):
        for j in range(2):
            card_image = resized[start_row + i * (card_height_shove + card_height):start_row + card_height + i * (
                    card_height_shove + card_height),
                         neg_col + j * (card_width + card_width_shove):neg_col + card_width + j * (
                                 card_width + card_width_shove)]
            # cards_found.append(findMatch(card_image))
            card_found_nerfs.append(findMatch(card_image))
            # cv2.imshow("card_image", card_image)
            # cv2.waitKey()

    # Options (Choices)
    if typ is None:
        option_col = (int(0.3 * width), int(0.368 * width))
        options1_row = (int(0.194 * height))
        options2_row = (int(0.599 * height))

        options_height = int(0.168 * height)

        options_row_shove = int(0.014 * height)
    elif typ == "1080p":
        option_col = (int(0.31 * width), int(0.375 * width))
        options1_row = (int(0.185 * height))
        options2_row = (int(0.599 * height))

        options_height = int(0.168 * height)

        options_row_shove = int(0.0174 * height)
    else:
        return

    # Options grid section
    options_1 = list()
    for i in range(2):
        option_image = resized[options1_row + i * (
                options_row_shove + options_height): options1_row + options_height + i * (
                options_row_shove + options_height), option_col[0]:option_col[1]]
        options_1.append(findMatch(option_image))
        # cv2.imshow("option_image", option_image)
        # cv2.waitKey()

    options_2 = list()
    for i in range(2):
        option_image = resized[options2_row + i * (
                options_row_shove + options_height): options2_row + options_height + i * (
                options_row_shove + options_height), option_col[0]:option_col[1]]
        options_2.append(findMatch(option_image))

    if show_res:
        # print(cards_found, options_1, options_2)
        print(card_found_buffs, card_found_nerfs, options_1, options_2)
    return card_found_buffs, card_found_nerfs, options_1, options_2


class CheckChoiceWindow:
    def __init__(self, error_thresh=0.1):
        self.previous_frame = None
        self._error_thresh = error_thresh

    def checkChoiceWindow(self, resolution_type=None, gui_queue=None):
        """
        Attempts to check if choice window is found.  This interacts with the GUI.

        :param resolution_type:
        :param gui_queue:
        :return:
        """

        frame = getFrame(resize_to=(700, 400))

        # Check if same frame
        if self.previous_frame is not None and frame.shape == self.previous_frame.shape:
            error = rmse(frame, self.previous_frame)  # 0.0035702968 or 0.0
            # print(error)
            if error < 0.01:
                return False  # Skip as this is the same frame

        self.previous_frame = frame  # Updating previous_frame after checks

        height, width, _ = frame.shape

        img = frame

        # Convert to graycsale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Blur the image for better edge detection
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)

        # Canny Edge Detection
        edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200)  # Canny Edge Detection
        # Display Canny Edge Detection Image
        # cv2.imshow('Canny Edge Detection', edges)
        # cv2.waitKey(0)

        ret, thresh = cv2.threshold(edges, 127, 255, 0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        bbox_top = list()
        bbox_bottom = list()
        for cnt in contours:
            x1, y1 = cnt[0][0]
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4:
                bbox = cv2.boundingRect(cnt)
                x, y, w, h = bbox
                if 0.4 * width < w < 0.8 * width:
                    if 0.3 * height < h < 0.5 * height:
                        if y < 0.5 * height:  # Top
                            if bbox not in bbox_top:
                                bbox_top.append(bbox)
                        else:  # Bottom
                            if bbox not in bbox_bottom:
                                bbox_bottom.append(bbox)

                        # img = cv2.drawContours(img, [cnt], -1, (0, 255, 0), 1)

        # cv2.imshow("img", img)
        # cv2.waitKey()
        # cv2.destroyAllWindows()

        if len(bbox_top) > 0 and len(bbox_bottom) > 0:
            return True
        else:
            return False

        # thresh_point = 0.05
        # thresh_size = 0.1
        # print(len(bbox_top), bbox_top, len(bbox_bottom))
        # if len(bbox_top) == 2 and len(bbox_bottom) == 2:
        #     for bbox_list in [bbox_top, bbox_bottom]:
        #
        #         if not ((bbox_list[0][0] - bbox_list[1][0]) ** 2 < thresh_point * width and (
        #                 bbox_list[0][1] - bbox_list[1][1]) ** 2 < thresh_point * width):
        #             return False
        #
        #         if not ((bbox_list[0][2] - bbox_list[1][2]) ** 2 < thresh_size * width and (
        #                 bbox_list[0][3] - bbox_list[1][3]) ** 2 < thresh_size * width):
        #             return False
        #
        # else:
        #     return False
        # return True


# ccw = CheckChoiceWindow()
# res = ccw.checkChoiceWindow()
# time.sleep(1)
# res = ccw.checkChoiceWindow()
# print(res)
