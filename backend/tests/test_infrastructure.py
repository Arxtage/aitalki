"""
Validation tests to verify the testing infrastructure is properly configured.
"""
import pytest
import sys
import os
from pathlib import Path


def test_python_version():
    """Test that we're running on a supported Python version."""
    assert sys.version_info >= (3, 8), f"Python 3.8+ required, got {sys.version_info}"


def test_pytest_working():
    """Test that pytest is working correctly."""
    assert True


def test_pytest_markers():
    """Test that custom pytest markers are defined."""
    # This would fail if markers aren't properly configured
    pytest.mark.unit
    pytest.mark.integration
    pytest.mark.slow


@pytest.mark.unit
def test_unit_marker():
    """Test unit test marker."""
    assert 1 + 1 == 2


@pytest.mark.integration
def test_integration_marker():
    """Test integration test marker."""
    assert "hello" + " world" == "hello world"


@pytest.mark.slow
def test_slow_marker():
    """Test slow test marker."""
    import time
    start = time.time()
    time.sleep(0.01)  # Very short sleep for validation
    assert time.time() - start >= 0.01


def test_project_structure():
    """Test that the expected project structure exists."""
    backend_dir = Path(__file__).parent.parent
    app_dir = backend_dir / "app"
    
    assert backend_dir.exists(), "Backend directory should exist"
    assert app_dir.exists(), "App directory should exist"
    assert (app_dir / "__init__.py").exists(), "App should have __init__.py"
    assert (app_dir / "main.py").exists(), "Main app file should exist"


def test_fixtures_available(temp_dir, sample_user_data):
    """Test that custom fixtures from conftest.py are available."""
    # Test temp_dir fixture
    assert temp_dir.exists()
    assert temp_dir.is_dir()
    
    # Test sample_user_data fixture
    assert isinstance(sample_user_data, dict)
    assert "id" in sample_user_data
    assert "username" in sample_user_data
    assert "email" in sample_user_data


def test_mock_fixtures(mock_database, mock_config):
    """Test that mock fixtures are working."""
    # Test mock_database
    assert hasattr(mock_database, "get_session")
    
    # Test mock_config
    assert isinstance(mock_config, dict)
    assert "database" in mock_config
    assert "security" in mock_config


def test_environment_isolation(mock_env_vars):
    """Test that environment variable mocking works."""
    assert os.environ["SECRET_KEY"] == "test-secret-key"
    assert os.environ["DEBUG"] == "True"


def test_async_support(event_loop):
    """Test that async test support is working."""
    import asyncio
    
    async def async_function():
        await asyncio.sleep(0.001)
        return "async_result"
    
    result = event_loop.run_until_complete(async_function())
    assert result == "async_result"


def test_temp_file_fixture(temp_file):
    """Test that temporary file fixture works."""
    assert temp_file.exists() is False or temp_file.is_file()
    
    # Write to temp file
    temp_file.write_text("test content")
    assert temp_file.read_text() == "test content"


def test_coverage_excluded_lines():
    """Test that coverage exclusion patterns work by having excluded code."""
    if __name__ == "__main__":  # pragma: no cover
        pass  # This should be excluded from coverage


class TestInfrastructureClass:
    """Test that test class discovery works."""
    
    def test_class_method(self):
        """Test that methods in test classes are discovered."""
        assert hasattr(self, '__class__')
    
    @pytest.mark.unit
    def test_marked_class_method(self):
        """Test that marked methods in classes work."""
        assert True