import pygetwindow as gw
import pyautogui as pa
import time
from PIL import Image
import numpy as np
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def delay(x):
    for i in range(x):
        print(f"\r{x-i}", end='') #count down second
        time.sleep(1) #delay 1s

def resizeimg(path, scale):
    Template = Image.open(path)
    width, height = Template.size
    NewSize = (int(width*scale), int(height*scale))
    resized_img = Template.resize(NewSize)
    return(resized_img)

def BackToLobby():
    return_img = resizeimg("pictures/return.png", scale)
    classical_img = resizeimg("pictures\classical.png", scale)
    # lobby_img = resizeimg("pictures/lobby.png", scale)
    returned = False
    start_time = time.time()
    while time.time()-start_time<3:
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
            pa.locateCenterOnScreen(classical_img, region=region, confidence=0.8)
        except pa.ImageNotFoundException as e:
            try:
                ReturnLocation = pa.locateCenterOnScreen(return_img, region=region, confidence=0.8) #press return button
                pa.click(ReturnLocation)
                returned = False
            except pa.ImageNotFoundException as e:
                print("\rCannot find return button", end='')
        else:
            returned = True
            print("\r已返回大厅                           ")

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

def farming_matches(basic_times=50, times=10):

    # start to play
    classical_img = resizeimg("pictures\classical.png", scale)
    excercise1_img = resizeimg("pictures\exercise1.png", scale)
    excercise2_img = resizeimg("pictures\exercise2.png", scale)

    while True:
        try:
            location = pa.locateCenterOnScreen(classical_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find classical_image! {e}", end='')
        else:
            pa.click(location)
            print("\r已进入标准场")
            break
    
    while True:
        try:
            location = pa.locateCenterOnScreen(excercise1_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find exercise_image! {e}", end='')
        else:
            pa.click(location)
            print("\r已进入演练                             ")
            break
    i = 1
    while True:
        gamma = 3
        finded_charater = False
        while not finded_charater:
            while True:
                try:
                    location = pa.locateCenterOnScreen(excercise2_img, region=region, confidence=0.8, grayscale=True)
                except pa.ImageNotFoundException as e:
                    print(f"\rError: Cannot find exercise_image! {e}", end='')
                else:
                    time.sleep(1)
                    pa.click(location)
                    print("\r已进入演练                             ")
                    break

            # choose the character
            HP_img = resizeimg("pictures\HP.png", scale)
            region_character = (left, top+height//2, width*3//4, height//2)
            time.sleep(9)
            while True:
                try:
                    time.sleep(1)
                    location = pa.locateCenterOnScreen(HP_img, region=region_character, confidence=0.8, grayscale=True)
                except pa.ImageNotFoundException as e:
                    print(f"\rError: Cannot find HP_image! {e}", end='')
                else:
                    x, y = location
                    character_img = pa.screenshot(region=(int(x), int(y-(90*scale)), int(100*scale), int(90*scale)))
                    pa.doubleClick(location)
                    # break
                    time.sleep(1)

                    # Template match
                    template = np.array(character_img)
                    template = cv2.cvtColor(template, cv2.COLOR_RGB2BGR)

                    screenshot = pa.screenshot(region=(left, top, width, height))
                    # screenshot.save("pictures/screenshot.png")
                    screenshot = np.array(screenshot)
                    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
                    screenshot = apply_gamma_correction(screenshot, gamma)
                    template = apply_gamma_correction(template, gamma)
                    template_height, template_width = template.shape[:2]
                    
                    template_height, template_width = template.shape[:2]
                    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    print(max_val)
                    if max_val >= 0.9:
                        x = max_loc[0]+left+template_width//2
                        y = max_loc[1]+top+template_height//2
                        pa.doubleClick(x, y)
                    print("已点选武将")     

                    # quit from the game
                    plus_img = resizeimg("pictures\plus.png", scale)
                    quit_img = resizeimg("pictures\quit.png", scale)
                    confirm_img = resizeimg("pictures\confirm.png", scale)
                    start_time = time.time()
                    while time.time()-start_time<3:
                        try:
                            location = pa.locateCenterOnScreen(plus_img, region=region, confidence=0.8, grayscale=True)
                        except pa.ImageNotFoundException as e:
                            print(f"\rError: Cannot find plus_image! {e}", end='')
                        else:
                            finded_charater = True #loaced the plus button
                            pa.click(location)
                            time.sleep(1.3)

                            start_time = time.time()
                            # find quit button
                            while time.time()-start_time<3: 
                                try:
                                    location = pa.locateCenterOnScreen(quit_img, region=region, confidence=0.8, grayscale=True)
                                except pa.ImageNotFoundException as e:
                                    print(f"\rError: Cannot find quit_image! {e}", end='')
                                else:
                                    pa.click(location)
                                    start_time = time.time()
                                    # find confirm button
                                    while time.time()-start_time < 3:
                                        try:
                                            location = pa.locateCenterOnScreen(confirm_img, region=region, confidence=0.8, grayscale=True)
                                        except pa.ImageNotFoundException as e:
                                            print(f"\rError: Cannot find confirm_image! {e}", end='')
                                        else:
                                            pa.click(location)
                                            break # located confirm button
                                    else:
                                        start_time = time.time() #refresh the colck
                                        continue
                                    break # located quit button
                            else:
                                print("\r无法找到\"退出按钮\"，正在返回上一步操作                    ", end='')
                            break # located puls button
                    else:
                        print("\r无法找到\"+\"，正在返回上一步操作                 ", end='')
                        continue
                    break
        print(f"\r已刷{i}次                       ")
        i += 1
        if ((i-1)%times == 0) and (i-1)>=basic_times:
            print("正在返回大厅并检查历练值                  ")
            BackToLobby()
            spacialOffer_img = resizeimg("pictures\spacial_offer.png", scale)
            activities_img = resizeimg("pictures\\activities.png", scale)
            GalleryOfHeros_img = resizeimg("pictures\Gallery of Heroes.png", scale)
            boost_img = resizeimg("pictures\\boost.png", scale)
            while True:
                try:
                    location = pa.locateCenterOnScreen(spacialOffer_img, region=region, confidence=0.8, grayscale=True)
                except pa.ImageNotFoundException as e:
                    print(f"\rError: Cannot find spacial_offer_image! {e}", end='')
                else:
                    pa.click(location)
                    break # located spacial offer button

            while True:
                try:
                    location = pa.locateCenterOnScreen(activities_img, region=region, confidence=0.8, grayscale=True)
                except pa.ImageNotFoundException as e:
                    print(f"\rError: Cannot find activities_image! {e}", end='')
                else:
                    pa.click(location)
                    break # located activities button

            while True:
                try:
                    location = pa.locateCenterOnScreen(GalleryOfHeros_img, region=region, confidence=0.8, grayscale=True)
                except pa.ImageNotFoundException as e:
                    print(f"\rError: Cannot find Gallery of Heroes image! {e}", end='')
                else:
                    pa.click(location)
                    break # located spacial offer button
            
            while True: # OCR
                try:
                    location = pa.locateOnScreen(boost_img, region=region, confidence=0.8, grayscale=True)
                except pa.ImageNotFoundException as e:
                    print(f"\rError: Cannot find boost image! {e}", end='')
                else:
                    num_left, num_top, num_weight, num_height = location
                    location = (int(num_left), int(num_top-num_height), num_weight, num_height)
                    print(location)
                    num_img = pa.screenshot(region=location)
                    # num_img.save('num_img1.png')
                    num_img = num_img.convert('L')
                    threshold = 75
                    num_img = num_img.point(lambda p: p>threshold and 255)
                    # num_img.save('num_img2.png')
                    # num_img = np.array(num_img)
                    number = pytesseract.image_to_string(num_img)
                    print(number)
                    break # located boost button

            if number.strip() == "60/60":
                print("已刷满群英绘墙，正在返回大厅")
                BackToLobby()
                return
            
            BackToLobby()
            while True:
                try:
                    location = pa.locateCenterOnScreen(classical_img, region=region, confidence=0.8, grayscale=True)
                except pa.ImageNotFoundException as e:
                    print(f"\rError: Cannot find classical_image! {e}", end='')
                else:
                    pa.click(location)
                    print("\r已进入演练                             ")
                    break

def sign_in():
    plus_img = resizeimg("pictures\plus.png", scale)
    SignIn1_img = resizeimg("pictures\sign in 1.png", scale)
    SignIn2_img = resizeimg("pictures\sign in 2.png", scale)
    get_img= resizeimg("pictures\get.png", scale)
    while True:
        try:
            location = pa.locateCenterOnScreen(plus_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find plus image! {e}", end='')
        else:
            pa.click(location)
            break
    time.sleep(1)
    while True:
        try:
            location = pa.locateCenterOnScreen(SignIn1_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find sign in 1 image! {e}", end='')
        else:
            pa.click(location)
            break
    start_time = time.time()
    while time.time()-start_time<2:
        try:
            location = pa.locateCenterOnScreen(SignIn2_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find sign in 2 image! {e}", end='')
        else:
            pa.click(location)
            break
    else:
        print("\r今日已签到                                           ")

    start_time = time.time()
    while time.time()-start_time<3:
        try:
            location = pa.locateCenterOnScreen(get_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find get image! {e}", end='')
        else:
            pa.click(location)
            start_time = time.time()
            continue
    else:
        print("\r未识别到可领取的奖励                          ")

    BackToLobby()
    
def gather_gold():
    plus_img = resizeimg("pictures\plus.png", scale)
    gold_img = resizeimg("pictures\gold.png", scale)
    water_img = resizeimg("pictures\water.png", scale)
    SmallGolds_img = resizeimg("pictures\small golds.png", scale)
    BigGolds_img = resizeimg("pictures\\big golds.png", scale)
    while True:
        try:
            location = pa.locateCenterOnScreen(plus_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find plus image! {e}", end='')
        else:
            pa.click(location)
            break
    time.sleep(1)
    while True:
        try:
            location = pa.locateCenterOnScreen(gold_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find gold image! {e}", end='')
        else:
            pa.click(location)
            break

    start_time = time.time()
    while time.time()-start_time<3:
        try:
            location = pa.locateCenterOnScreen(water_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find water image! {e}", end='')
        else:
            pa.click(location)
            break
    else:
        print("\r今日已浇水                               ")
    start_time = time.time()
    while time.time()-start_time<3:
        try:
            location = pa.locateCenterOnScreen(SmallGolds_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find small golds image! {e}", end='')
        else:
            pa.click(location)
            start_time = time.time()
            continue
    else:
        print("\r未识别到可领取的小元宝                   ")
    start_time = time.time()
    while time.time()-start_time<2:
        try:
            location = pa.locateCenterOnScreen(BigGolds_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find big golds image! {e}", end='')
        else:
            pa.click(location)
            start_time = time.time()
            continue
    else:
        print("\r未识别到可领取的大元宝                       ")

    BackToLobby()

def reward():
    grow_img = resizeimg("pictures\\reward\grow.png", scale)
    get_img = resizeimg("pictures\\reward\get.png", scale)
    chest1_img = resizeimg("pictures\\reward\chest1.png", scale)
    chest2_img = resizeimg("pictures\\reward\chest2.png", scale)
    chest3_img = resizeimg("pictures\\reward\chest3.png", scale)
    chest4_img = resizeimg("pictures\\reward\chest4.png", scale)

    while True:
        try:
            location = pa.locateCenterOnScreen(grow_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find grow image! {e}", end='')
        else:
            pa.click(location)
            break
    start_time = time.time()
    while time.time()-start_time<2:
        try:
            location = pa.locateCenterOnScreen(get_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find get image! {e}", end='')
        else:
            pa.click(location)
            start_time = time.time()
            time.sleep(0.5)
            continue
    else:
        print("\r未识别到可领取的奖励                       ")

    time.sleep(1)

    while True:
        try:
            location = pa.locateCenterOnScreen(chest1_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find chest1 image! {e}", end='')
        else:
            pa.click(location)
            break
    while True:
        try:
            location = pa.locateCenterOnScreen(chest2_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find chest2 image! {e}", end='')
        else:
            pa.click(location)
            break
    while True:
        try:
            location = pa.locateCenterOnScreen(chest3_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find chest3image! {e}", end='')
        else:
            pa.click(location)
            break
    while True:
        try:
            location = pa.locateCenterOnScreen(chest4_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find chest4 image! {e}", end='')
        else:
            pa.click(location)
            break
    BackToLobby()

def recruit():
    shop_img = resizeimg("pictures\\recruit\shop.png", scale)
    get_hero_img = resizeimg("pictures\\recruit\get_hero.png", scale)
    get_skin_img = resizeimg("pictures\\recruit\get_skin.png", scale)
    skin_img = resizeimg("pictures\\recruit\skin.png", scale)
    cancel_img = resizeimg("pictures\\recruit\cancel.png", scale)
    print("正在尝试抽招募令和雁翎甲")
    while True:
        try:
            location = pa.locateCenterOnScreen(shop_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find shop image! {e}", end='')
        else:
            pa.click(location)
            break
    time.sleep(1)
    while True:
        try:
            location = pa.locateCenterOnScreen(get_hero_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find get_hero image! {e}", end='')
        else:
            pa.click(location)
            break

    start_time = time.time()
    while time.time()-start_time<2:
        try:
            location = pa.locateCenterOnScreen(cancel_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find cancel image! {e}", end='')
        else:
            print("无可用招募令")
            pa.click(location)
            break

    BackToLobby()

    while True:
        try:
            location = pa.locateCenterOnScreen(shop_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find shop image! {e}", end='')
        else:
            pa.click(location)
            break
    time.sleep(1)
    while True:
        try:
            location = pa.locateCenterOnScreen(skin_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find skin image! {e}", end='')
        else:
            pa.click(location)
            break
    time.sleep(1)
    while True:
        try:
            location = pa.locateCenterOnScreen(get_skin_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find get_skin image! {e}", end='')
        else:
            pa.click(location)
            break
    start_time = time.time()
    while time.time()-start_time<2:
        try:
            location = pa.locateCenterOnScreen(cancel_img, region=region, confidence=0.8, grayscale=True)
        except pa.ImageNotFoundException as e:
            print(f"\rError: Cannot find cancel image! {e}", end='')
        else:
            print("无可用雁翎甲")
            pa.click(location)
            break
    BackToLobby()
#########################################################################################################

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
scale = (width)/1600
print(f"窗口分辨率为：{width, height}缩放大小为{scale}")

# # start game
region = (left, top+34, width, height)
start_img = resizeimg('pictures/start game.png', scale)
try:
    location = pa.locateCenterOnScreen(start_img, region=region, confidence=0.8, grayscale=True)
except pa.ImageNotFoundException as e:
    print(f"Error: Cannot find start_image! {e}", end='')
else:
    pa.click(location)
    print("\r已进入游戏")

BackToLobby()

sign_in()

gather_gold()

farming_matches(times=10, basic_times=50)

recruit()

reward()
