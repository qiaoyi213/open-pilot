import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
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


# Set your OpenAI API key
def mark_cursor(img):
    cursor_x, cursor_y = pyautogui.position()
    draw = ImageDraw.Draw(img)
    radius = 20
    draw.ellipse((cursor_x - radius, cursor_y - radius, cursor_x + radius, cursor_y + radius), fill="red", outline="black", width=3)
    return img

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = mark_cursor(screenshot)
    screenshot.save('screenshot.png')
    return "screenshot.png"

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
            time.sleep(5)
        else:
            print("Invalid operation please do it again.")

        print(f"{operate_thought}")


class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.commands = ""
        self.history = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Chat with LLM')
        self.setGeometry(100, 100, 600, 400)

        # Layout
        self.layout = QVBoxLayout()

        # Chat display
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        # User input
        self.user_input = QTextEdit(self)
        self.layout.addWidget(self.user_input)

        # Send button
        self.send_button = QPushButton('Send', self)
        self.send_button.clicked.connect(self.handle_send)
        self.layout.addWidget(self.send_button)

        # Set the layout
        self.setLayout(self.layout)

    def handle_send(self):
        # Get the user input
        user_message = self.user_input.toPlainText().strip()

        if not user_message:
            return

        # Clear the input area
        self.user_input.clear()

        # Display the user's message in the chat
        self.chat_display.append(f'User: {user_message}')

        # Get the response from the LLM
        response = self.get_llm_response(user_message)

        # Display the LLM's response
        self.chat_display.append(f'LLM: {response}')
        
    def get_llm_response(self, message):
        try:
            load_dotenv()
            client = OpenAI(api_key=os.getenv('OPENAI_API'))
            screenshot_path = capture_screenshot()
            #capture_and_draw_grid(32, 18)
            base64_screenshot = encode_image('screenshot.png')
            payload = [
                    {
                        "role": "system",
                        "content":  [
                            {
                                "type": "text",
                                "text": prompts.get_system_prompt(objective=message)
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
            payload.extend(self.history)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages = payload
            )
            
            content = response.choices[0].message.content

            if "```json" in content:
                print(content)
                content = content[7:-3]
                
            print(content)
            self.history.append({"role": "assisant", "content": [
                {
                    "type": "text",
                    "text": content
                }
            ]})
            command = json.loads(content)
            
            operate(command)
            
            self.commands += response.choices[0].message.content + "\n"
            
            return content
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec_())
