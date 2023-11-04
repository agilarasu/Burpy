import pyautogui
import keyboard
import time
# Define the point to check for red color
x, y = 960, 539
#x,y=960,524
#520

# Define the target color and threshold
scope_red  = (254, 33, 3)
threshold  = 10
pyautogui.FAILSAFE=False
pixel_x, pixel_y =1594, 740
while True:
    # Wait for "9" key press
    keyboard.wait("9")
    
    # Run the while loop until "0" key press
    while not keyboard.is_pressed("0"):
        color = pyautogui.pixel(x, y)
        print(color)
        if abs(color[0] - scope_red[0]) <= threshold and abs(color[1] - scope_red[1]) <= threshold and abs(color[2] - scope_red[2]) <= threshold:
            #click 1594 740
            #pyautogui.click(1594, 740)
            #pyautogui.dragTo(1588,811, 0.2, button='left')
            pyautogui.dragTo(201,68, 0.2, button='left')
            pyautogui.click(201, 68)