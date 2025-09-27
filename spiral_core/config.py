"""
🌀 Spiral Codex Configuration - The Organic Settings Foundation
===============================================================

Environment-driven configuration with healing patterns and organic defaults.
Supports .env files, environment variables, and development overrides.

Configuration Philosophy:
- Development should flow naturally without friction
- Production settings emerge from environment naturally
- All secrets are externalized and never committed
- Healing defaults prevent system breakdown
"""

import os
from pathlib import Path
from typing import List, Optional, Set

from pydantic import BaseSettings, Field, validator


class SpiralSettings(BaseSettings):
    """
    🌀 Spiral Codex Configuration
    
    Organic configuration that adapts to environment while maintaining
    healing defaults. All sensitive values are externalized.
    """
    
    # === Core Application Settings ===
    app_name: str = Field(default="Spiral Codex Organic OS", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="development", description="Runtime environment")
    debug: bool = Field(default=True, description="Debug mode (auto-disabled in production)")
    
    # === Server Configuration ===
    host: str = Field(default="0.0.0.0", description="Server bind host")
    port: int = Field(default=8000, ge=1000, le=65535, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on code changes")
    workers: int = Field(default=1, ge=1, le=16, description="Worker processes")
    
    # === API Configuration ===
    api_prefix: str = Field(default="/api/v1", description="API path prefix")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    max_request_size: int = Field(default=16 * 1024 * 1024, description="Max request size in bytes")
    rate_limit_requests: int = Field(default=100, description="Requests per minute limit")
    
    # === Database Configuration ===
    database_url: Optional[str] = Field(
        default=None, 
        description="Database connection URL (if using database)"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    connection_pool_size: int = Field(default=5, ge=1, le=50, description="DB connection pool size")
    
    # === Redis/Cache Configuration ===
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection URL for caching/sessions"
    )
    cache_ttl: int = Field(default=300, ge=1, description="Default cache TTL in seconds")
    
    # === Logging Configuration ===
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="structured", description="Log format: 'simple' or 'structured'")
    log_file: Optional[str] = Field(default=None, description="Log file path (stdout if None)")
    
    # === Security Configuration ===
    secret_key: str = Field(
        default="spiral-development-key-change-in-production",
        description="Secret key for signing (MUST change in production)"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    jwt_expiry_hours: int = Field(default=24, ge=1, description="JWT token expiry in hours")
    allowed_hosts: Set[str] = Field(
        default={"localhost", "127.0.0.1", "0.0.0.0"},
        description="Allowed host headers"
    )
    
    # === Agent Configuration ===
    agent_timeout: int = Field(default=30, ge=1, le=300, description="Agent processing timeout")
    max_spiral_depth: int = Field(default=7, ge=1, le=10, description="Maximum spiral depth")
    agent_stats_persist: bool = Field(default=True, description="Persist agent statistics")
    
    # === Feature Flags ===
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    enable_health_checks: bool = Field(default=True, description="Enable health check endpoints")
    enable_api_docs: bool = Field(default=True, description="Enable API documentation")
    enable_cors: bool = Field(default=True, description="Enable CORS middleware")
    
    # === File System Configuration ===
    data_directory: Path = Field(default=Path("./data"), description="Data storage directory")
    temp_directory: Path = Field(default=Path("./tmp"), description="Temporary files directory")
    max_file_size: int = Field(default=100 * 1024 * 1024, description="Max file upload size")
    
    class Config:
        """Pydantic configuration for organic environment loading."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = "SPIRAL_"
        
        # Allow extra fields for extensibility
        extra = "allow"
    
    @validator("environment")
    def validate_environment(cls, v):
        """Ensure environment is a known value."""
        valid_envs = {"development", "testing", "staging", "production"}
        if v.lower() not in valid_envs:
            return "development"  # Healing default
        return v.lower()
    
    @validator("debug")
    def auto_disable_debug_in_production(cls, v, values):
        """Automatically disable debug mode in production for security."""
        if values.get("environment") == "production":
            return False
        return v
    
    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        """Ensure secret key is changed in production."""
        env = values.get("environment", "development")
        if env == "production" and "development" in v:
            raise ValueError(
                "🔥 HEALING REQUIRED: Secret key must be changed in production! "
                "Set SPIRAL_SECRET_KEY environment variable."
            )
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Ensure log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        return v.upper() if v.upper() in valid_levels else "INFO"
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("data_directory", "temp_directory")
    def ensure_directories_exist(cls, v):
        """Create directories if they don't exist (healing pattern)."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    def get_database_url(self) -> str:
        """Get database URL with healing default."""
        if self.database_url:
            return self.database_url
        
        # Healing default: SQLite for development
        db_path = self.data_directory / "spiral_codex.db"
        return f"sqlite:///{db_path}"
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL if configured."""
        return self.redis_url
    
    def model_dump_safe(self) -> dict:
        """Export settings without sensitive values."""
        data = self.dict()
        
        # Remove or mask sensitive fields
        sensitive_fields = {"secret_key", "database_url", "redis_url"}
        for field in sensitive_fields:
            if field in data and data[field]:
                data[field] = "***MASKED***"
        
        return data


# === Environment File Creation Helper ===
def create_env_template(path: str = ".env.template"):
    """
    Create an environment file template with all available settings.
    This helps developers understand available configuration options.
    """
    template_content = '''# 🌀 Spiral Codex Organic OS - Environment Configuration
# =====================================================================
# Copy this file to `.env` and customize values for your environment
# Never commit .env files containing secrets to version control

# === Application Settings ===
SPIRAL_APP_NAME="Spiral Codex Organic OS"
SPIRAL_APP_VERSION="1.0.0"
SPIRAL_ENVIRONMENT=development
SPIRAL_DEBUG=true

# === Server Configuration ===
SPIRAL_HOST=0.0.0.0
SPIRAL_PORT=8000
SPIRAL_RELOAD=true
SPIRAL_WORKERS=1

# === API Configuration ===
SPIRAL_API_PREFIX=/api/v1
SPIRAL_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
SPIRAL_MAX_REQUEST_SIZE=16777216
SPIRAL_RATE_LIMIT_REQUESTS=100

# === Database Configuration ===
# SPIRAL_DATABASE_URL=sqlite:///./data/spiral_codex.db
# SPIRAL_DATABASE_URL=postgresql://user:pass@localhost/spiral_codex
SPIRAL_DATABASE_ECHO=false
SPIRAL_CONNECTION_POOL_SIZE=5

# === Redis/Cache Configuration ===
# SPIRAL_REDIS_URL=redis://localhost:6379/0
SPIRAL_CACHE_TTL=300

# === Logging Configuration ===
SPIRAL_LOG_LEVEL=INFO
SPIRAL_LOG_FORMAT=structured
# SPIRAL_LOG_FILE=./logs/spiral_codex.log

# === Security Configuration (CRITICAL - CHANGE IN PRODUCTION!) ===
SPIRAL_SECRET_KEY=spiral-development-key-change-in-production
SPIRAL_JWT_ALGORITHM=HS256
SPIRAL_JWT_EXPIRY_HOURS=24
SPIRAL_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# === Agent Configuration ===
SPIRAL_AGENT_TIMEOUT=30
SPIRAL_MAX_SPIRAL_DEPTH=7
SPIRAL_AGENT_STATS_PERSIST=true

# === Feature Flags ===
SPIRAL_ENABLE_METRICS=true
SPIRAL_ENABLE_HEALTH_CHECKS=true
SPIRAL_ENABLE_API_DOCS=true
SPIRAL_ENABLE_CORS=true

# === File System Configuration ===
SPIRAL_DATA_DIRECTORY=./data
SPIRAL_TEMP_DIRECTORY=./tmp
SPIRAL_MAX_FILE_SIZE=104857600
'''
    
    with open(path, "w") as f:
        f.write(template_content)
    
    print(f"🌀 Environment template created at: {path}")
    print("📝 Copy to .env and customize for your environment")


# === Global Settings Instance ===
# This creates a singleton settings instance that loads from environment
settings = SpiralSettings()

# Create environment template on first import if it doesn't exist
if not os.path.exists(".env.template") and settings.is_development():
    create_env_template()
