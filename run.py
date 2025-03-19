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
    new_width = width // 2
    new_height = height // 2
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


def capture_and_draw_grid(n, m, font_path='arial.ttf', font_size=40):
    # 擷取螢幕截圖
    screenshot = pyautogui.screenshot('screenshot.png')
    print(screenshot)
    img = screenshot
    draw = ImageDraw.Draw(img)

    # 計算每個區塊的寬度和高度
    width, height = img.size
    block_width = width // n
    block_height = height // m

    # 設定格線顏色和線寬
    grid_color = (200, 200, 200)  # 淺灰色
    grid_width = 1

    # 繪製垂直格線
    for i in range(1, n):
        x = i * block_width
        draw.line([(x, 0), (x, height)], fill=grid_color, width=grid_width)

    # 繪製水平格線
    for j in range(1, m):
        y = j * block_height
        draw.line([(0, y), (width, y)], fill=grid_color, width=grid_width)

    # 在每個區塊上添加數字標記
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    for i in range(n):
        for j in range(m):
            # 計算區塊的左上角座標
            left = i * block_width
            upper = j * block_height

            # 獲取文字的邊界框
            text = f'{i * m + j + 1}'
            bbox = draw.textbbox((left, upper), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 計算數字的位置，使其置中
            text_x = left + (block_width - text_width) // 2
            text_y = upper + (block_height - text_height) // 2

            # 在區塊上繪製數字
            draw.text((text_x, text_y), text, font=font, fill=(255, 1, 1))

    # 儲存或顯示結果圖片
    img.save('screenshot_with_grid_lines.png')


    

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
    num_iters = 50
    user_task = input("Enter your task for the agent: ")
    
    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API'))
    history = []
    for _ in range(num_iters):
        screenshot_path = capture_screenshot()
        #capture_and_draw_grid(32, 18)
        base64_screenshot = encode_image(screenshot_path)
        payload = [
                {
                    "role": "system",
                    "content":  [
                        {
                            "type": "text",
                            "text": prompts.get_system_prompt(objective=user_task)
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
        payload.extend(history)
        #print(payload)
        
        time.sleep(5)
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages= payload
            )
        except Exception as e:
            print(e)
            continue 
        content = response.choices[0].message.content

        print(content)
        if "```json" in content:
            content = content[7:-3]
            print(content)

        

        """
        history.append({
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
                })
        
        
        """
        history.append(
            {"role": "assistant", "content": [{ "type": "text", "text": content}]}
        )
        commands = json.loads(content)
        operate(commands)

main()