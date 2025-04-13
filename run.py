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
def mark_cursor(img):
    cursor_x, cursor_y = pyautogui.position()
    draw = ImageDraw.Draw(img)
    radius = 20
    draw.ellipse((cursor_x - radius, cursor_y - radius, cursor_x + radius, cursor_y + radius), fill="red", outline="black", width=3)
    return img

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = mark_cursor(screenshot)
    screenshot = screenshot.convert("RGB")
    width, height = screenshot.size
    new_width = width // 3
    new_height = height // 3
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
            operate_detail = click_detail

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
    num_iters = 10
    user_task = input("Enter your task for the agent: ")
    
    load_dotenv()
    provider = "Anthropic"
    if provider == "OpenAI":
        client = OpenAI(api_key=os.getenv('OPENAI_API'))
    else:
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API'))

    trajectory = []
    error = ""
    for _ in range(num_iters):
        screenshot_path = capture_screenshot()
        #capture_and_draw_grid(32, 18)
        base64_screenshot = encode_image(screenshot_path)
        if provider == "OpenAI":
            payload = [
                    {
                        "role": "system",
                        "content":  [
                            {
                                "type": "text",
                                "text": prompts.get_system_prompt(objective=user_task, trajectory=trajectory, error=error)
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
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages= payload
                )
            except Exception as e:
                print(e)
                continue 
            
            content = response.choices[0].message.content
        else:
            message = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                temperature=1,
                system=prompts.get_system_prompt(objective=user_task, trajectory=trajectory, error=error),
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompts.get_user_prompt()
                            },
                            {   
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_screenshot
                                }
                            }
                        ]
                    }
                ]
            )

            content = message.content[0].text

        print(content)
        if "```json" in content:
            content = content[7:-3]
            print(content)

        
        trajectory.append(content)

        commands = json.loads(content)
        operate(commands)
        time.sleep(5)
        
        # Error grounding 
        screenshot_path = capture_screenshot()
        #capture_and_draw_grid(32, 18)
        base64_screenshot = encode_image(screenshot_path)
        if provider == "OpenAI":
            payload = [
                    {
                        "role": "system",
                        "content":  [
                            {
                                "type": "text",
                                "text": prompts.get_error_grounding_prompt(thought=commands, screenshot=base64_screenshot)
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
            error = response.choices[0].message.content
        else:
            message = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                temperature=1,
                system=prompts.get_error_grounding_prompt(thought=commands),
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {   
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_screenshot
                                }
                            }
                        ]
                    }
                ]
                
            )

            error = message.content[0].text
        
        print(error)
main()