import pyautogui
import platform
import time
import math

def convert_percent_to_decimal(percent):
    try:
        # Remove the '%' sign and convert to float
        decimal_value = float(percent)

        # Convert to decimal (e.g., 20% -> 0.20)
        return decimal_value
    except ValueError as e:
        print(f"[convert_percent_to_decimal] error: {e}")
        return None


class Operator:
    
    def write(self, content):
        try:
            content = content.replace("\\n", "\n")
            for char in content:
                pyautogui.write(char)
        except Exception as e:
            print("[Operator][write] error:", e)

    def press(self, keys):
        try:
            for key in keys:
                pyautogui.keyDown(key)
            time.sleep(0.1)
            for key in keys:
                pyautogui.keyUp(key)
        except Exception as e:
            print("[Operator][press] error:", e)
    def click_mouse(self):
        x, y = pyautogui.position()
        pyautogui.click(x, y)
    def mouse(self, click_detail):
        try:
            x = convert_percent_to_decimal(click_detail.get("x"))
            y = convert_percent_to_decimal(click_detail.get("y"))

            if click_detail and isinstance(x, float) and isinstance(y, float):
                #self.move_at_percentage(x, y)
                screen_width, screen_height = pyautogui.size()
                x_pixel = int(screen_width * float(x))
                y_pixel = int(screen_height * float(y))

                pyautogui.moveTo(x_pixel, y_pixel)

        except Exception as e:
            print("[Operator][mouse] error:", e)

    def move_at_percentage(
        self,
        x_percentage,
        y_percentage,
        duration=0.2,
        circle_radius=50,
        circle_duration=0.5,
    ):
        try:
            screen_width, screen_height = pyautogui.size()
            x_pixel = int(screen_width * float(x_percentage))
            y_pixel = int(screen_height * float(y_percentage))

            pyautogui.moveTo(x_pixel, y_pixel, duration=duration)

            start_time = time.time()
            while time.time() - start_time < circle_duration:
                angle = ((time.time() - start_time) / circle_duration) * 2 * math.pi
                x = x_pixel + math.cos(angle) * circle_radius
                y = y_pixel + math.sin(angle) * circle_radius
                pyautogui.moveTo(x, y, duration=0.1)

            
        except Exception as e:
            print("[Operator][click_at_percentage] error:", e) # type: ignore