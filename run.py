from openai import OpenAI
import pyautogui
import time
import prompts
import base64 
from dotenv import load_dotenv
import os
from utils.operator import Operator
import json

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save('screenshot.png')
    return "screenshot.png"

def operate(commands):
    operator = Operator()
    for operation in commands:
        operate_type = operation['operation']
        operate_thought = operation['thought']
        operate_detail = ""

        if operate_type == "press" or operate_type == "hotkey":
            keys = operation['keys']
            operate_detail = keys
            operator.press(keys)
            
        elif operate_type == "write":
            content = operation["content"]
            operate_detail = content
            operator.write(content)
        elif operate_type == "click":
            x = operation.get("x")
            y = operation.get("y")
            click_detail = {"x": x, "y": y}
            operate_detail = click_detail

            operator.mouse(click_detail)
        elif operate_type == "done":
            summary = operation.get("summary")

            print("Done, summary:", summary)
            return True

        else:
            print("Invalid operation please do it again.")

        print(f"{operate_thought}")
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
                            "text": prompts.get_system_prompt(objective=user_task)
                        },
                        {
                            "type": "text",
                            "text": f'The actions that you are made are {commands}'
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompts.get_user_prompt()
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
        content = response.choices[0].message.content

        if "```json" in content:
            print(content)
            content = content[7:-3]
            
        print(content)
        commands = json.loads(content)
        
        operate(commands)
        commands += response.choices[0].message.content + "\n"
main()