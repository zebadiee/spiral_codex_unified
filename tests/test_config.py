"""
🧪 Configuration Testing Rituals
================================

Tests for the organic configuration system, ensuring environment
variables, validation, and healing patterns work correctly.
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from pydantic import ValidationError

from spiral_core.config import SpiralSettings, create_env_template


class TestSpiralSettings:
    """Test the core configuration class."""
    
    def test_default_settings(self):
        """Test default configuration values."""
        settings = SpiralSettings()
        
        assert settings.app_name == "Spiral Codex Organic OS"
        assert settings.environment == "development"
        assert settings.debug is True
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.api_prefix == "/api/v1"
        assert settings.log_level == "INFO"
        assert settings.max_spiral_depth == 7
    
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        with mock.patch.dict(os.environ, {
            "SPIRAL_APP_NAME": "Test Spiral",
            "SPIRAL_PORT": "9000",
            "SPIRAL_DEBUG": "false",
            "SPIRAL_LOG_LEVEL": "debug"
        }):
            settings = SpiralSettings()
            assert settings.app_name == "Test Spiral"
            assert settings.port == 9000
            assert settings.debug is False
            assert settings.log_level == "DEBUG"
    
    def test_environment_validation(self):
        """Test environment validation with healing."""
        with mock.patch.dict(os.environ, {"SPIRAL_ENVIRONMENT": "invalid_env"}):
            settings = SpiralSettings()
            # Should heal to development
            assert settings.environment == "development"
    
    def test_debug_auto_disable_in_production(self):
        """Test debug auto-disable in production."""
        with mock.patch.dict(os.environ, {
            "SPIRAL_ENVIRONMENT": "production",
            "SPIRAL_DEBUG": "true"
        }):
            settings = SpiralSettings()
            assert settings.environment == "production"
            assert settings.debug is False  # Should be auto-disabled
    
    def test_secret_key_validation_in_production(self):
        """Test secret key validation in production."""
        with mock.patch.dict(os.environ, {
            "SPIRAL_ENVIRONMENT": "production",
            "SPIRAL_SECRET_KEY": "spiral-development-key-change-in-production"
        }):
            with pytest.raises(ValidationError) as exc_info:
                SpiralSettings()
            
            assert "HEALING REQUIRED" in str(exc_info.value)
            assert "Secret key must be changed" in str(exc_info.value)
    
    def test_valid_secret_key_in_production(self):
        """Test valid secret key in production."""
        with mock.patch.dict(os.environ, {
            "SPIRAL_ENVIRONMENT": "production",
            "SPIRAL_SECRET_KEY": "super-secure-production-key-12345"
        }):
            settings = SpiralSettings()
            assert settings.secret_key == "super-secure-production-key-12345"
    
    def test_log_level_validation(self):
        """Test log level validation with healing."""
        with mock.patch.dict(os.environ, {"SPIRAL_LOG_LEVEL": "invalid"}):
            settings = SpiralSettings()
            assert settings.log_level == "INFO"  # Should heal to INFO
        
        with mock.patch.dict(os.environ, {"SPIRAL_LOG_LEVEL": "warning"}):
            settings = SpiralSettings()
            assert settings.log_level == "WARNING"  # Should be uppercased
    
    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from string."""
        with mock.patch.dict(os.environ, {
            "SPIRAL_CORS_ORIGINS": "http://localhost:3000,http://example.com,https://app.domain.com"
        }):
            settings = SpiralSettings()
            expected = ["http://localhost:3000", "http://example.com", "https://app.domain.com"]
            assert settings.cors_origins == expected
    
    def test_directory_creation(self):
        """Test that directories are created if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "test_data"
            temp_path = Path(temp_dir) / "test_temp"
            
            with mock.patch.dict(os.environ, {
                "SPIRAL_DATA_DIRECTORY": str(data_path),
                "SPIRAL_TEMP_DIRECTORY": str(temp_path)
            }):
                settings = SpiralSettings()
                
                # Directories should be created
                assert data_path.exists()
                assert temp_path.exists()
                assert settings.data_directory == data_path
                assert settings.temp_directory == temp_path
    
    def test_port_validation(self):
        """Test port number validation."""
        with mock.patch.dict(os.environ, {"SPIRAL_PORT": "999"}):
            with pytest.raises(ValidationError):
                SpiralSettings()  # Port too low
        
        with mock.patch.dict(os.environ, {"SPIRAL_PORT": "70000"}):
            with pytest.raises(ValidationError):
                SpiralSettings()  # Port too high
    
    def test_spiral_depth_validation(self):
        """Test spiral depth validation."""
        with mock.patch.dict(os.environ, {"SPIRAL_MAX_SPIRAL_DEPTH": "15"}):
            with pytest.raises(ValidationError):
                SpiralSettings()  # Too deep


class TestSettingsMethods:
    """Test configuration helper methods."""
    
    def test_is_development(self):
        """Test development mode detection."""
        with mock.patch.dict(os.environ, {"SPIRAL_ENVIRONMENT": "development"}):
            settings = SpiralSettings()
            assert settings.is_development() is True
            assert settings.is_production() is False
    
    def test_is_production(self):
        """Test production mode detection."""
        with mock.patch.dict(os.environ, {
            "SPIRAL_ENVIRONMENT": "production",
            "SPIRAL_SECRET_KEY": "secure-production-key"
        }):
            settings = SpiralSettings()
            assert settings.is_production() is True
            assert settings.is_development() is False
    
    def test_get_database_url_default(self):
        """Test default database URL generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(os.environ, {"SPIRAL_DATA_DIRECTORY": temp_dir}):
                settings = SpiralSettings()
                db_url = settings.get_database_url()
                
                assert db_url.startswith("sqlite:///")
                assert "spiral_codex.db" in db_url
    
    def test_get_database_url_custom(self):
        """Test custom database URL."""
        custom_url = "postgresql://user:pass@localhost/spiral_codex"
        with mock.patch.dict(os.environ, {"SPIRAL_DATABASE_URL": custom_url}):
            settings = SpiralSettings()
            assert settings.get_database_url() == custom_url
    
    def test_get_redis_url(self):
        """Test Redis URL retrieval."""
        redis_url = "redis://localhost:6379/0"
        with mock.patch.dict(os.environ, {"SPIRAL_REDIS_URL": redis_url}):
            settings = SpiralSettings()
            assert settings.get_redis_url() == redis_url
        
        # Test default (None)
        settings = SpiralSettings()
        assert settings.get_redis_url() is None
    
    def test_model_dump_safe(self):
        """Test safe model export without sensitive data."""
        with mock.patch.dict(os.environ, {
            "SPIRAL_SECRET_KEY": "secret-key",
            "SPIRAL_DATABASE_URL": "postgresql://user:pass@localhost/db",
            "SPIRAL_REDIS_URL": "redis://localhost:6379/0"
        }):
            settings = SpiralSettings()
            safe_data = settings.model_dump_safe()
            
            # Sensitive fields should be masked
            assert safe_data["secret_key"] == "***MASKED***"
            assert safe_data["database_url"] == "***MASKED***"
            assert safe_data["redis_url"] == "***MASKED***"
            
            # Non-sensitive fields should be intact
            assert safe_data["app_name"] == settings.app_name
            assert safe_data["environment"] == settings.environment


class TestEnvironmentFile:
    """Test environment file template generation."""
    
    def test_create_env_template(self):
        """Test environment template file creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = Path(temp_dir) / ".env.template"
            
            create_env_template(str(template_path))
            
            assert template_path.exists()
            
            content = template_path.read_text()
            assert "🌀 Spiral Codex Organic OS" in content
            assert "SPIRAL_APP_NAME=" in content
            assert "SPIRAL_SECRET_KEY=" in content
            assert "SPIRAL_DATABASE_URL=" in content
            assert "change-in-production" in content
    
    def test_env_template_completeness(self):
        """Test that env template includes all major config options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = Path(temp_dir) / ".env.template"
            
            create_env_template(str(template_path))
            content = template_path.read_text()
            
            # Check for major sections
            sections = [
                "Application Settings",
                "Server Configuration", 
                "API Configuration",
                "Database Configuration",
                "Security Configuration",
                "Agent Configuration",
                "Feature Flags"
            ]
            
            for section in sections:
                assert section in content


class TestConfigIntegration:
    """Integration tests for configuration system."""
    
    def test_env_file_loading(self):
        """Test loading configuration from .env file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            
            # Create a test .env file
            env_content = """
SPIRAL_APP_NAME=Test App
SPIRAL_PORT=8080
SPIRAL_DEBUG=false
SPIRAL_ENVIRONMENT=testing
SPIRAL_LOG_LEVEL=WARNING
"""
            env_file.write_text(env_content)
            
            # Change working directory to temp dir
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                settings = SpiralSettings()
                
                assert settings.app_name == "Test App"
                assert settings.port == 8080
                assert settings.debug is False
                assert settings.environment == "testing"
                assert settings.log_level == "WARNING"
                
            finally:
                os.chdir(original_cwd)
    
    def test_environment_precedence(self):
        """Test that environment variables take precedence over .env file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            
            # Create .env file with one value
            env_file.write_text("SPIRAL_PORT=8080\n")
            
            # Set different value in environment
            with mock.patch.dict(os.environ, {"SPIRAL_PORT": "9000"}):
                original_cwd = os.getcwd()
                try:
                    os.chdir(temp_dir)
                    settings = SpiralSettings()
                    
                    # Environment variable should win
                    assert settings.port == 9000
                    
                finally:
                    os.chdir(original_cwd)
    
    def test_case_insensitive_env_vars(self):
        """Test case-insensitive environment variable handling."""
        with mock.patch.dict(os.environ, {
            "spiral_app_name": "Lowercase Test",
            "SPIRAL_PORT": "8080"
        }):
            settings = SpiralSettings()
            # Both should work due to case_sensitive=False
            assert settings.app_name == "Lowercase Test"
            assert settings.port == 8080


class TestConfigValidation:
    """Test configuration validation and error handling."""
    
    def test_invalid_types_healing(self):
        """Test healing of invalid data types."""
        with mock.patch.dict(os.environ, {
            "SPIRAL_PORT": "not_a_number",
            "SPIRAL_DEBUG": "not_a_boolean"
        }):
            with pytest.raises(ValidationError):
                SpiralSettings()  # Should fail validation
    
    def test_allowed_hosts_set_handling(self):
        """Test allowed hosts as set type."""
        settings = SpiralSettings()
        assert isinstance(settings.allowed_hosts, set)
        assert "localhost" in settings.allowed_hosts
    
    def test_extra_fields_allowed(self):
        """Test that extra configuration fields are allowed."""
        with mock.patch.dict(os.environ, {"SPIRAL_CUSTOM_FIELD": "custom_value"}):
            settings = SpiralSettings()
            # Should not raise error due to extra='allow'
            # Note: In real usage, you'd access via settings.__dict__ or similar


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for configuration in realistic scenarios."""
    
    def test_development_defaults(self):
        """Test development environment defaults."""
        with mock.patch.dict(os.environ, {"SPIRAL_ENVIRONMENT": "development"}):
            settings = SpiralSettings()
            
            assert settings.is_development()
            assert settings.debug is True
            assert settings.reload is True
            assert settings.enable_api_docs is True
    
    def test_production_security(self):
        """Test production security settings."""
        with mock.patch.dict(os.environ, {
            "SPIRAL_ENVIRONMENT": "production",
            "SPIRAL_SECRET_KEY": "secure-production-key-xyz",
            "SPIRAL_DEBUG": "true"  # Should be overridden
        }):
            settings = SpiralSettings()
            
            assert settings.is_production()
            assert settings.debug is False  # Auto-disabled
            assert settings.secret_key == "secure-production-key-xyz"
    
    def test_complete_configuration_flow(self):
        """Test complete configuration loading and usage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create directories
            data_dir = Path(temp_dir) / "data"
            temp_dir_path = Path(temp_dir) / "tmp"
            
            with mock.patch.dict(os.environ, {
                "SPIRAL_ENVIRONMENT": "testing",
                "SPIRAL_DATA_DIRECTORY": str(data_dir),
                "SPIRAL_TEMP_DIRECTORY": str(temp_dir_path),
                "SPIRAL_DATABASE_URL": f"sqlite:///{data_dir}/test.db"
            }):
                settings = SpiralSettings()
                
                # Verify directories were created
                assert data_dir.exists()
                assert temp_dir_path.exists()
                
                # Verify database URL
                assert settings.get_database_url().endswith("test.db")
                
                # Verify safe export
                safe_data = settings.model_dump_safe()
                assert "***MASKED***" in safe_data["database_url"]


# === Fixtures ===
@pytest.fixture(autouse=True)
def clean_environment():
    """Clean up environment variables after each test."""
    # Store original environment
    original_env = dict(os.environ)
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
