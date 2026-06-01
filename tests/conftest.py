import sys
from pathlib import Path

import pytest


@pytest.fixture
def sample_question():
    return "What is the current price of AAPL?"
