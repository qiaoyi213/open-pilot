# Open-Pilot

Open-Pilot is a Python project designed to interact with a large language model (LLM) autonomously, performing various operations and tasks based on user-defined prompts. It can be extended to run a range of AI-driven tasks by processing user inputs and generating dynamic responses from the model.

## Features

- Autonomously interacts with a large language model.
- Supports custom prompts and dynamic input generation.
- Simple interface for running LLM-based tasks.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/qiaoyi213/open-pilot.git
    ```
2. Navigate to the project directory:
    ```bash
    cd open-pilot
    ```
3. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the program, use the `run.py` script. This script will execute a sequence of tasks using predefined or dynamically generated prompts.

1. Run the main script:
    ```bash
    python run.py
    ```

2. The script will interact with the LLM and perform tasks based on the prompts specified in `prompts.py`.

## File Structure

- **`run.py`**: Main entry point to execute the project logic.
- **`prompts.py`**: Contains the logic for generating and handling the prompts to be sent to the model.

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
