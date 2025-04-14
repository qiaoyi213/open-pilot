import openai 
import os 
PROMPT = """
Your task is input cleaning. The input will contain some text and a array in jsonl format, the input will cause json.load cannot read the input correctlly.
Your job is ignore the text and output the jsonl format.

There are some helpful example: 
1. 
Input:
Based on the objective to open arxiv and select the newest paper, I'll take the following actions:
[
    { "thought": "I see a terminal with 'Open arxiv and select newest paper for me' displayed. I'll first open a web browser to access arxiv", "operation": "press", "keys": ["command", "space"] },
    { "thought": "I'll type 'Google Chrome' to launch the browser", "operation": "write", "content": "Google Chrome" },
    { "thought": "Now I'll launch Chrome by pressing enter", "operation": "press", "keys": ["enter"] },
    { "thought": "I'll focus on the address bar to type arxiv.org", "operation": "press", "keys": ["command", "l"] },
    { "thought": "Type the arxiv website address", "operation": "write", "content": "arxiv.org" },
    { "thought": "Press enter to go to the website", "operation": "press", "keys": ["enter"] }
]

Output:
[
    { "thought": "I see a terminal with 'Open arxiv and select newest paper for me' displayed. I'll first open a web browser to access arxiv", "operation": "press", "keys": ["command", "space"] },
    { "thought": "I'll type 'Google Chrome' to launch the browser", "operation": "write", "content": "Google Chrome" },
    { "thought": "Now I'll launch Chrome by pressing enter", "operation": "press", "keys": ["enter"] },
    { "thought": "I'll focus on the address bar to type arxiv.org", "operation": "press", "keys": ["command", "l"] },
    { "thought": "Type the arxiv website address", "operation": "write", "content": "arxiv.org" },
    { "thought": "Press enter to go to the website", "operation": "press", "keys": ["enter"] }
]

2. 
Input:
```
[
    { "thought": "I see a terminal with 'Open arxiv and select newest paper for me' displayed. I'll first open a web browser to access arxiv", "operation": "press", "keys": ["command", "space"] },
    { "thought": "I'll type 'Google Chrome' to launch the browser", "operation": "write", "content": "Google Chrome" },
    { "thought": "Now I'll launch Chrome by pressing enter", "operation": "press", "keys": ["enter"] },
    { "thought": "I'll focus on the address bar to type arxiv.org", "operation": "press", "keys": ["command", "l"] },
    { "thought": "Type the arxiv website address", "operation": "write", "content": "arxiv.org" },
    { "thought": "Press enter to go to the website", "operation": "press", "keys": ["enter"] }
]
```

Output: 
[
    { "thought": "I see a terminal with 'Open arxiv and select newest paper for me' displayed. I'll first open a web browser to access arxiv", "operation": "press", "keys": ["command", "space"] },
    { "thought": "I'll type 'Google Chrome' to launch the browser", "operation": "write", "content": "Google Chrome" },
    { "thought": "Now I'll launch Chrome by pressing enter", "operation": "press", "keys": ["enter"] },
    { "thought": "I'll focus on the address bar to type arxiv.org", "operation": "press", "keys": ["command", "l"] },
    { "thought": "Type the arxiv website address", "operation": "write", "content": "arxiv.org" },
    { "thought": "Press enter to go to the website", "operation": "press", "keys": ["enter"] }
]
"""

def eval(content):
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API'))
    payload = [
                {
                    "role": "system",
                    "content":  [
                        {
                            "type": "text",
                            "text": PROMPT
                        }
                    ]
                },
                
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": content
                        }
                    ]
                }
            ]
            
    response = client.chat.completions.create(
        model="gpt-4o",
        messages= payload
    )
    
    content = response.choices[0].message.content

    return content