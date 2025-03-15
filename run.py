from openai import OpenAI
import pyautogui
import time
from prompts import SYSTEM_PROMPT
import base64 
from dotenv import load_dotenv

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save('screenshot.png')
    return "screenshot.png"

def operate(command):
    """
    - click_left
    - click_right
    - move [x] [y]
    - scroll [up or down]
    - wait
    - double_click_left
    - type [words]
    """
    print("OPERATE COMMAND:", command)
    if command == "click_left":
        pyautogui.click()
    elif command == "click_right":
        pyautogui.click(button='right')
    elif command.split()[0] == "move":
        x = int(command.split()[1])
        y = int(command.split()[2])
        pyautogui.moveTo(x, y)
    elif command == "scroll up":
        pyautogui.scroll(500)  
    elif command == "scroll down":
        pyautogui.scroll(-500)
    elif command == "wait":
        time.sleep(5)
    elif command == "double_click_left":
        pyautogui.doubleClick()
    elif command.split()[0] == "type":
        word = command[5:]
        pyautogui.write(word)
    else:
        print("Invalid operation")
    
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')




def main():
    num_iters = 50
    user_task = input("Enter your task for the agent: ")
    
    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API'))
    commands = ""
    for _ in range(num_iters):
        screenshot_path = capture_screenshot()
        base64_screenshot = encode_image(screenshot_path)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content":  [
                        {
                            "type": "text",
                            "text": SYSTEM_PROMPT
                        },
                        {
                            "type": "text",
                            "text": f'Current cursor position is {pyautogui.position()}. The size of window is {pyautogui.size()}'
                            
                        },
                        {
                            "type": "text",
                            "text": f'All thought and command you have done are {commands}'
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f'Task: {user_task}'
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_screenshot}"
                            }
                        }
                    ]
                        
                },
                
            ]
        )
        print(response.choices[0].message.content)
        command = response.choices[0].message.content.split("Action: ")[1]
        operate(command)
        commands += response.choices[0].message.content + "\n"
main()