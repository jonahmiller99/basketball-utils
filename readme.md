# College Basketball Box Plus Minus (BPM) Calculator

This repository contains code for calculating the Box Plus Minus (BPM) statistic for college basketball players. The BPM is a basketball statistic originally created by Daniel Myers, which provides a comprehensive measure of a player's contribution to the game, relative to an average division one player. For a detailed explanation of BPM, you can refer to this Sports Reference article: https://www.sports-reference.com/blog/2020/02/introducing-bpm-2-0/

This project aims to calculate this statistic based on a formula and spreadsheet provided by Bart Torvik.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Acknowledgments](#acknowledgments)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.x
- pip

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/jonahmiller99/basketball-utils.git
    ```

2. Navigate to the project directory:

    ```bash
    cd basketball-utils
    ```


3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use the `BpmCalculator` class, you can import it as follows:

```python
from src.playerBpm import BpmCalculator

# Your code here
```


## Testing

To run tests, navigate to the project directory and run:

```bash
pytest
```

## Acknowledgments

- This module was created with the assistance of a spreadsheet provided by Bart Torvik who runs the analytics site: https://barttorvik.com
