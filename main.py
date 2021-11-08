import numpy as np
import cv2.cv2 as cv2
from time import sleep
import os
import pyautogui

if os.name != 'posix':
    from PIL import ImageGrab  # Windows and macOS only

if os.name == "Windows":
    sep = '\\'
else:
    sep = '/'

WIDTH = 0
HEIGHT = 0
SETTING_FILE = "settings.txt"
FOLDER_PATH = "images_to_click"
cap = cv2.VideoCapture(0)


def set_screen_size():
    global WIDTH
    global HEIGHT
    sz = pyautogui.size()
    WIDTH = sz[0]
    HEIGHT = sz[1]


def take_line_without_spaces(line):
    s = ""
    for el in line:
        if el != ' ' and el != "\n":
            s += el
    return s


def take_settings():
    """

    :return: dict {setting: parameter}
    """
    dd = {}
    with open(SETTING_FILE, 'r') as file:
        while True:
            line = file.readline()
            if len(line) > 1:
                param = take_line_without_spaces(line[0: line.index('=')])
                value = take_line_without_spaces(line[line.index('=') + 1:])

                dd.update({param: value})
            else:
                break
    return dd


def give_templates(folder):
    templates = []
    try:

        for el in os.listdir(folder):
            templates.append(cv2.imread(folder + sep + el, cv2.IMREAD_GRAYSCALE))
    except FileNotFoundError:
        os.mkdir(folder)
    return templates


def give_cords(gray_frame, templates):
    """

    :param gray_frame: image (screen capture)
    :param templates: image templates
    :return: list[[int, int]] list of cords to click
    """
    ret = []
    for template in templates:
        res = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.7)
        x, y, n = 0, 0, 0
        w, h = template.shape[::-1]
        for pt in zip(*loc[::-1]):
            x += pt[0] + w
            y += pt[1] + h
            n += 1
        if n != 0:
            x /= n
            y /= n
            ret.append([x, y])
        else:
            print("nothing to click")
    return ret


def give_frame():
    pass
    if os.name != 'posix':
        img = ImageGrab.grab(bbox=(0, 0, WIDTH, HEIGHT))  # x, y, w, h
        frame = np.array(img)
        return frame
    image = pyautogui.screenshot()  # sudo apt-get install scrot
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return image


def frame_to_gray(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray_frame


def click(x, y):
    x_b, y_b = pyautogui.position()
    pyautogui.click(x=x, y=y)
    pyautogui.moveTo(x_b, y_b)
    print("clicking:", x, y)


def click_on_images(cords):
    for pair in cords:
        click(pair[0], pair[1])


def main():
    set_screen_size()
    settings = take_settings()
    time_to_sleep = int(settings['sleep'])
    templates = give_templates(settings['images_folder'])  # Error can occur
    while True:

        frame = give_frame()
        gray_frame = frame_to_gray(frame)

        to_click = give_cords(gray_frame, templates)

        click_on_images(to_click)
        sleep(time_to_sleep)


if __name__ == '__main__':
    main()