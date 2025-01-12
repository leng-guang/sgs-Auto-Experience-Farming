import pygetwindow as gw
import pyautogui as pa
import time
from PIL import Image
import numpy as np
import cv2

def delay(x):
    for i in range(x):
        print(f"\r{x-i}", end='') #count down second
        time.sleep(1) #delay 1s

def resizeimg(img, scale):
    Template = Image.open(img)
    width, height = Template.size
    NewSize = (int(width*scale), int(height*scale))
    resized_img = Template.resize(NewSize)
    return(resized_img)

def BackToLobby():
    time.sleep(5)
    return_img = resizeimg("pictures/return.png", scale)
    lobby_img = resizeimg("pictures/lobby.png", scale)
    returned = False
    while True:
        try:
            ReturnLocation = pa.locateCenterOnScreen(return_img, region=region, confidence=0.8) #press return button
        except pa.ImageNotFoundException as e:
            print("\rCannot find return button", end='')
        else:
            pa.click(ReturnLocation)
            break

    while not returned:
        time.sleep(0.5)
        try:
            pa.locateCenterOnScreen(lobby_img, region=region, confidence=0.8)
        except pa.ImageNotFoundException as e:
            try:
                ReturnLocation = pa.locateCenterOnScreen(return_img, region=region, confidence=0.8) #press return button
                pa.click(ReturnLocation)
                returned = False
            except pa.ImageNotFoundException as e:
                print("\rCannot find return button", end='')
        else:
            returned = True
            print("\r已返回大厅")


print("程序已开始运行，请将模拟器调至屏幕最上方")
delay(5)

SizeCheck = True
while SizeCheck:
    print("\r正在检查窗口大小...")
    #get arguments of target window
    window = gw.getActiveWindow()
    left, top = window.left, window.top
    width, height = window.width, window.height
    # check the size of window
    if width<1280 or height<720:
        SizeCheck = True
        print("\r窗口过小，请扩大窗口后重新尝试")
        print("请至少将窗口扩大至1280*720分辨率，以保证识别的准确性")
        delay(3)
    else:
        SizeCheck = False
        print("\r窗口大小满足条件")

# calculate the scale factor
scale = width/1600
print(f"窗口分辨率为：{width, height}缩放大小为{scale}")

# start game
region = (left, top, width, height)
start_img = resizeimg('pictures/start game.png', scale)
try:
    location = pa.locateCenterOnScreen(start_img, region=region, confidence=0.8, grayscale=True)
except pa.ImageNotFoundException as e:
    print(f"Error: Cannot find start_image! {e}", end='')
else:
    pa.click(location)
    print("\r已进入游戏")

BackToLobby()

# start to play
classical_img = resizeimg("pictures\classical.png", scale)
excercise_img = resizeimg("pictures\exercise.png", scale)
time.sleep(1)

while True:
    try:
        location = pa.locateCenterOnScreen(classical_img, region=region, confidence=0.8, grayscale=True)
    except pa.ImageNotFoundException as e:
        print(f"\rError: Cannot find classical_image! {e}", end='')
    else:
        pa.click(location)
        print("\r已进入标准场")
        break

def apply_gamma_correction(image, gamma):
    """
    应用伽马校正，增强图像的亮部并压暗暗部。
    :param image: 输入图像
    :param gamma: 伽马值（小于1提高亮部，大于1增加暗部的亮度）
    :return: 伽马校正后的图像
    """
    # 将图像归一化到 0 到 1 的范围
    normalized_image = image / 255.0
    # 应用伽马校正
    gamma_corrected_image = np.power(normalized_image, gamma)
    # 将图像归一化回 0 到 255 的范围
    gamma_corrected_image = np.uint8(gamma_corrected_image * 255)
    return gamma_corrected_image

def farming_matches(times):
    for i in range(times):
        while True:
            try:
                location = pa.locateCenterOnScreen(excercise_img, region=region, confidence=0.8, grayscale=True)
            except pa.ImageNotFoundException as e:
                print(f"\rError: Cannot find exercise_image! {e}", end='')
            else:
                pa.click(location)
                print("\r已进入演练")
                break

        # choose the character
        HP_img = resizeimg("pictures\HP.png", scale)
        time.sleep(9)
        while True:
            try:
                time.sleep(1)
                location = pa.locateCenterOnScreen(HP_img, region=region, confidence=0.8, grayscale=True)
            except pa.ImageNotFoundException as e:
                print(f"\rError: Cannot find HP_image! {e}", end='')
            else:
                x, y = location
                character_img = pa.screenshot(region=(int(x), int(y-(90*scale)), int(100*scale), int(90*scale)))
                pa.doubleClick(location)
                break
        time.sleep(1)

        # Template match
        screenshot = pa.screenshot(region=(left, top, width, height))
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        template = np.array(character_img)
        template = cv2.cvtColor(template, cv2.COLOR_RGB2BGR)

        # cv2.imwrite("screenshot_before.png", screenshot)
        # cv2.imwrite("template_before.png", template)

        gamma = 2.5
        screenshot = apply_gamma_correction(screenshot, gamma)
        template = apply_gamma_correction(template, gamma)
        template_height, template_width = template.shape[:2]
        
        template_height, template_width = template.shape[:2]
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        x = max_loc[0]+left+template_width//2
        y = max_loc[1]+top+template_height//2
        
        pa.doubleClick(x, y)

        top_left = max_loc
        bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
        cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
        # cv2.imwrite("screenshot_after.png", screenshot)
        # cv2.imwrite("template_after.png", template)

        # while True:
        #     try:
        #         time.sleep(1)
        #         location = pa.locateCenterOnScreen(character_img, region=region, confidence=0.95, grayscale=False)
        #     except pa.ImageNotFoundException as e:
        #         print(f"\rError: Cannot find character_image! {e}", end='')
        #     else:
        #         pa.doubleClick(location)
        #         break
        print("已点选武将")

        # quit from the game
        plus_img = resizeimg("pictures\plus.png", scale)
        quit_img = resizeimg("pictures\quit.png", scale)
        confirm_img = resizeimg("pictures\confirm.png", scale)
        while True:
            try:
                location = pa.locateCenterOnScreen(plus_img, region=region, confidence=0.8, grayscale=True)
            except pa.ImageNotFoundException as e:
                print(f"\rError: Cannot find plus_image! {e}", end='')
            else:
                pa.click(location)
                break
        time.sleep(1)
        while True:
            try:
                location = pa.locateCenterOnScreen(quit_img, region=region, confidence=0.8, grayscale=True)
            except pa.ImageNotFoundException as e:
                print(f"\rError: Cannot find plus_image! {e}", end='')
            else:
                pa.click(location)
                break
        while True:
            try:
                location = pa.locateCenterOnScreen(confirm_img, region=region, confidence=0.8, grayscale=True)
            except pa.ImageNotFoundException as e:
                print(f"\rError: Cannot find plus_image! {e}", end='')
            else:
                pa.click(location)
                break
farming_matches(10)