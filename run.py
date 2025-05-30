from openai import OpenAI
import pyautogui
import time
import prompts
import base64 
from dotenv import load_dotenv
import os
from utils.operator import Operator
import json
from PIL import Image, ImageDraw, ImageFont
import io
import anthropic
from eval import eval
from utils.rag import RAGModel

def mark_cursor(img):
    cursor_x, cursor_y = pyautogui.position()
    draw = ImageDraw.Draw(img)
    radius = 20
    draw.ellipse((cursor_x - radius, cursor_y - radius, cursor_x + radius, cursor_y + radius), fill="red", outline="black", width=3)
    return img

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.resize(pyautogui.size())

    screenshot = mark_cursor(screenshot)
    screenshot = screenshot.convert("RGB")
    
    width, height = screenshot.size
    new_width = width 
    new_height = height 
    resized_image = screenshot.resize((new_width, new_height))

    buffer = io.BytesIO()
    
    resized_image.save(buffer, format="JPEG", optimize=True)

    # Save the compressed screenshot as a file (you can also adjust the quality for JPEG format)
    with open('screenshot.jpeg', 'wb') as f:
        f.write(buffer.getvalue())
    f.close()
    return "screenshot.jpeg"

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


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
            operator.click_mouse()
        elif operate_type == "move":
            x = operation.get("x")
            y = operation.get("y")
            click_detail = {"x": x, "y": y}
            operator.mouse(click_detail)
        elif operate_type == "done":
            summary = operation.get("summary")

            print("Done, summary:", summary)
            return True
        elif operate_type == "request":
            _ = input("Press any key to continue...")
        else:
            print("Invalid operation please do it again.")

        print(f"{operate_thought}")


def main():


    ragclient = RAGModel()
    ragclient.load_pdf('data/sage_tutorial.pdf')
    
    num_iters = 15
    user_task = input("Enter your task for the agent: ")
    
    load_dotenv()
    
    client = OpenAI(api_key=os.getenv('OPENAI_API'))
    trajectory = []
    error = ""
    for _ in range(num_iters):
        screenshot_path = capture_screenshot()
        base64_screenshot = encode_image(screenshot_path)
        context = ragclient.generate(prompts.get_system_prompt(objective=user_task, trajectory=trajectory, error=error))

        print(context)

        payload = [
                {
                    "role": "system",
                    "content":  [
                        {
                            "type": "text",
                            "text": prompts.get_rag_prompt(objective=user_task, trajectory=trajectory, error=error, context=context)
                        },
                        
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
                }
            ]
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages= payload
            )
        except Exception as e:
            print(e)
            continue 
        content = response.choices[0].message.content

        content = eval(content=content)

        print(content)
        trajectory.append(content)
        try:
            commands = json.loads(content)
        except Exception as e:
                print(e)
                continue
        operate(commands)
        time.sleep(1)
        
        # Error grounding 
        screenshot_path = capture_screenshot()
        base64_screenshot = encode_image(screenshot_path)
        payload = [
                    {
                        "role": "system",
                        "content":  [
                            {
                                "type": "text",
                                "text": prompts.get_error_grounding_prompt(objective=user_task, thought=commands)
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
                    }
                ]
        
        content = client.chat.completions.create(
            model="gpt-4o",
            messages=payload
        )
        print(error)
main()