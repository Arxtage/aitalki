import os
import tempfile
import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        yield Path(tmp_file.name)
        # Cleanup
        try:
            os.unlink(tmp_file.name)
        except FileNotFoundError:
            pass


@pytest.fixture
def mock_database():
    """Mock database connection and session."""
    mock_db = Mock()
    mock_session = Mock()
    mock_db.get_session.return_value = mock_session
    return mock_db


@pytest.fixture
def mock_fastapi_app():
    """Mock FastAPI application instance."""
    from unittest.mock import MagicMock
    app = MagicMock()
    app.state = MagicMock()
    return app


@pytest.fixture
def mock_google_client():
    """Mock Google API clients (TTS, Gemini)."""
    mock_client = Mock()
    mock_client.synthesize_speech.return_value = Mock()
    mock_client.generate_content.return_value = Mock()
    return mock_client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    }


@pytest.fixture
def sample_audio_data():
    """Sample audio data for testing."""
    return b"fake_audio_data_for_testing"


@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    env_vars = {
        "DATABASE_URL": "postgresql://test:test@localhost:5432/testdb",
        "SECRET_KEY": "test-secret-key",
        "GOOGLE_API_KEY": "test-api-key",
        "DEBUG": "True"
    }
    
    # Store original values
    original_vars = {}
    for key, value in env_vars.items():
        original_vars[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield env_vars
    
    # Restore original values
    for key, original_value in original_vars.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_request():
    """Mock HTTP request object."""
    request = Mock()
    request.headers = {"Authorization": "Bearer test-token"}
    request.json.return_value = {"test": "data"}
    request.method = "POST"
    request.url = Mock()
    request.url.path = "/api/test"
    return request


@pytest.fixture
def mock_response():
    """Mock HTTP response object."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"message": "success"}
    response.headers = {"Content-Type": "application/json"}
    return response


@pytest.fixture(autouse=True)
def reset_mocks():
    """Automatically reset all mocks after each test."""
    yield
    # This fixture runs after each test to ensure clean state


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Mock application configuration."""
    config = {
        "database": {
            "url": "postgresql://test:test@localhost:5432/testdb",
            "echo": False
        },
        "security": {
            "secret_key": "test-secret-key",
            "algorithm": "HS256",
            "access_token_expire_minutes": 30
        },
        "google": {
            "api_key": "test-api-key",
            "project_id": "test-project"
        }
    }
    return config