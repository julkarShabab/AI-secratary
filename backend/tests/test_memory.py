import pytest
from unittest.mock import MagicMock, patch
from app.memory.memory_manager import MemoryManager


def test_should_save_long_term_preference():
    manager = MemoryManager.__new__(MemoryManager)
    assert manager._should_save_long_term("I prefer morning meetings") is True

def test_should_save_long_term_manager():
    manager = MemoryManager.__new__(MemoryManager)
    assert manager._should_save_long_term("My manager is Sarah") is True

def test_should_not_save_long_term_casual():
    manager = MemoryManager.__new__(MemoryManager)
    assert manager._should_save_long_term("Check my emails") is False

def test_should_not_save_long_term_question():
    manager = MemoryManager.__new__(MemoryManager)
    assert manager._should_save_long_term("What meetings do I have today?") is False

def test_should_save_long_term_work():
    manager = MemoryManager.__new__(MemoryManager)
    assert manager._should_save_long_term("I work at a fintech startup") is True