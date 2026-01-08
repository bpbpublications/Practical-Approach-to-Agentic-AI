# PracticalApproachToAgenticAI

This project contains the code examples from the book "Practical Approach to Agentic AI".

## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

* Python 3.10+
* Poetry

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/your_username_/PracticalApproachToAgenticAI.git
   ```
2. Install Python packages
   ```sh
   poetry install --no-root
   ```

## Usage

To run the examples, you can use `poetry run`. For example, to run the `ner_with_ollama.py` python example in Chapter 3:

```sh
poetry run python src/Chapter3/ner_with_ollama.py
```
Similarly, to run chainlit based examples, such as `nudge_customer_bot_chainlit_app.py` in Chapter 10, use below command:
```sh
poetry run chainlit run src/Chapter10/agentframework/nudge_customer_bot_chainlit_app.py --port 8099
```
