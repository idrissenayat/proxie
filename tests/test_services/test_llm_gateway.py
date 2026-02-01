"""
Unit tests for LLMGateway.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from litellm.utils import ModelResponse

from src.platform.services.llm_gateway import LLMGateway


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = Mock()
    redis_mock.get.return_value = None
    redis_mock.setex = Mock()
    return redis_mock


@pytest.fixture
def llm_gateway(mock_redis):
    """Create LLMGateway instance with mocked Redis."""
    with patch('src.platform.services.llm_gateway.redis') as mock_redis_module:
        mock_redis_module.from_url.return_value = mock_redis
        gateway = LLMGateway()
        gateway.redis_client = mock_redis
        return gateway


@pytest.fixture
def sample_messages():
    """Sample messages for LLM completion."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return ModelResponse(
        id="test-id",
        choices=[{
            "message": {
                "role": "assistant",
                "content": "I'm doing well, thank you!"
            },
            "finish_reason": "stop"
        }],
        usage={
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
    )


class TestLLMGateway:
    """Test LLMGateway functionality."""
    
    def test_initialization(self, mock_redis):
        """Test LLMGateway initialization."""
        with patch('src.platform.services.llm_gateway.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            gateway = LLMGateway()
            
            assert gateway.cache_enabled is True
            assert gateway.primary_model is not None
            assert gateway.fallback_model is not None
    
    def test_cache_key_generation(self, llm_gateway, sample_messages):
        """Test cache key generation."""
        cache_key = llm_gateway._get_cache_key(
            "gemini/gemini-2.0-flash",
            sample_messages
        )
        
        assert cache_key.startswith("llm_cache:")
        assert len(cache_key) > 10
    
    def test_cache_key_deterministic(self, llm_gateway, sample_messages):
        """Test that cache key is deterministic."""
        key1 = llm_gateway._get_cache_key(
            "gemini/gemini-2.0-flash",
            sample_messages
        )
        key2 = llm_gateway._get_cache_key(
            "gemini/gemini-2.0-flash",
            sample_messages
        )
        
        assert key1 == key2
    
    def test_cache_key_different_for_different_messages(self, llm_gateway):
        """Test that different messages produce different cache keys."""
        messages1 = [{"role": "user", "content": "Hello"}]
        messages2 = [{"role": "user", "content": "Goodbye"}]
        
        key1 = llm_gateway._get_cache_key("model", messages1)
        key2 = llm_gateway._get_cache_key("model", messages2)
        
        assert key1 != key2
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, llm_gateway, sample_messages, mock_redis):
        """Test cache hit scenario."""
        # Mock cached response
        cached_response = {
            "id": "cached-id",
            "choices": [{
                "message": {"role": "assistant", "content": "Cached response"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8}
        }
        mock_redis.get.return_value = json.dumps(cached_response)
        
        with patch('src.platform.services.llm_gateway.SessionLocal') as mock_db:
            with patch('src.platform.services.llm_gateway.settings') as mock_settings:
                mock_settings.ENVIRONMENT = "production"
                mock_settings.GOOGLE_API_KEY = "real-key"
                mock_settings.LLM_CACHE_ENABLED = True
                mock_db.return_value.__enter__.return_value = Mock()
                mock_db.return_value.__exit__.return_value = None
            
            result = await llm_gateway.chat_completion(
                messages=sample_messages,
                use_cache=True
            )
            
            # Should return cached response
            assert result is not None
            mock_redis.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, llm_gateway, sample_messages, mock_redis, mock_llm_response):
        """Test cache miss scenario."""
        mock_redis.get.return_value = None  # Cache miss
        
        from src.platform.services.llm_gateway import settings as gateway_settings
        
        with patch('src.platform.services.llm_gateway.SessionLocal') as mock_db:
            mock_db.return_value.__enter__.return_value = Mock()
            mock_db.return_value.__exit__.return_value = None
            
            with patch('src.platform.services.llm_gateway.litellm.acompletion', new=AsyncMock(return_value=mock_llm_response)):
                with patch('src.platform.services.llm_gateway.track_llm_usage'):
                    with patch('src.platform.services.llm_gateway.LLMUsageService') as mock_usage:
                        # Use patch.object to modify the actual settings instance
                        with patch.object(gateway_settings, 'ENVIRONMENT', 'production'), \
                             patch.object(gateway_settings, 'GOOGLE_API_KEY', 'real-key'), \
                             patch.object(gateway_settings, 'LLM_CACHE_ENABLED', True):
                            
                            mock_usage.return_value.is_over_budget.return_value = False
                            mock_usage.return_value.record_usage = Mock()
                        
                            result = await llm_gateway.chat_completion(
                                messages=sample_messages,
                                use_cache=True
                            )
                            
                            # Should call LLM
                            assert result is not None
                            # Should save to cache
                            mock_redis.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_budget_check_blocks_request(self, llm_gateway, sample_messages):
        """Test that budget check blocks requests over limit."""
        with patch('src.platform.services.llm_gateway.SessionLocal') as mock_db:
            mock_session = Mock()
            mock_db.return_value.__enter__.return_value = mock_session
            mock_db.return_value.__exit__.return_value = None
            
            with patch('src.platform.services.llm_gateway.LLMUsageService') as mock_usage:
                mock_usage.return_value.is_over_budget.return_value = True
                
                with pytest.raises(Exception, match="LLM usage limit exceeded"):
                    await llm_gateway.chat_completion(
                        messages=sample_messages,
                        user_id="user_123"
                    )
    
    @pytest.mark.asyncio
    async def test_fallback_on_primary_failure(self, llm_gateway, sample_messages, mock_llm_response):
        """Test fallback to secondary model on primary failure."""
        mock_redis = Mock()
        mock_redis.get.return_value = None
        llm_gateway.redis_client = mock_redis
        
        with patch('src.platform.services.llm_gateway.SessionLocal') as mock_db:
            mock_db.return_value.__enter__.return_value = Mock()
            mock_db.return_value.__exit__.return_value = None
            
            with patch('src.platform.services.llm_gateway.LLMUsageService') as mock_usage:
                with patch('src.platform.services.llm_gateway.settings') as mock_settings:
                    mock_settings.ENVIRONMENT = "production"
                    mock_settings.GOOGLE_API_KEY = "dummy"
                    
                    mock_usage.return_value.is_over_budget.return_value = False
                    mock_usage.return_value.record_usage = Mock()
                    
                    with patch('src.platform.services.llm_gateway.litellm.acompletion') as mock_completion:
                        # Primary fails
                        mock_completion.side_effect = [
                            Exception("Primary model failed"),
                            mock_llm_response  # Fallback succeeds
                        ]
                        
                        with patch('src.platform.services.llm_gateway.track_llm_usage'):
                            result = await llm_gateway.chat_completion(
                                messages=sample_messages
                            )
                            
                            # Should have called completion twice (primary + fallback)
                            assert mock_completion.call_count == 2
                            assert result is not None
    
    @pytest.mark.asyncio
    async def test_mock_mode_enabled(self, llm_gateway, sample_messages):
        """Test mock mode when API key is missing."""
        with patch('src.platform.services.llm_gateway.settings') as mock_settings:
            mock_settings.ENVIRONMENT = "test"
            mock_settings.GOOGLE_API_KEY = ""
            
            with patch('src.platform.services.llm_gateway.SessionLocal') as mock_db:
                mock_db.return_value.__enter__.return_value = Mock()
                mock_db.return_value.__exit__.return_value = None
                
                with patch('src.platform.services.llm_gateway.LLMUsageService') as mock_usage:
                    mock_usage.return_value.is_over_budget.return_value = False
                    
                    result = await llm_gateway.chat_completion(
                        messages=sample_messages
                    )
                    
                    # Should return mock response
                    assert result is not None
                    assert hasattr(result, 'choices')
    
    @pytest.mark.asyncio
    async def test_redis_connection_failure_handled(self):
        """Test that Redis connection failure is handled gracefully."""
        with patch('src.platform.services.llm_gateway.redis') as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Redis connection failed")
            
            # Should not raise exception
            gateway = LLMGateway()
            assert gateway.cache_enabled is False
            assert gateway.redis_client is None
    
    @pytest.mark.asyncio
    async def test_cache_disabled(self, llm_gateway, sample_messages, mock_llm_response):
        """Test behavior when cache is disabled."""
        llm_gateway.cache_enabled = False
        
        with patch('src.platform.services.llm_gateway.SessionLocal') as mock_db:
            mock_db.return_value.__enter__.return_value = Mock()
            mock_db.return_value.__exit__.return_value = None
            
            with patch('src.platform.services.llm_gateway.LLMUsageService') as mock_usage:
                mock_usage.return_value.is_over_budget.return_value = False
                mock_usage.return_value.record_usage = Mock()
                
                with patch('src.platform.services.llm_gateway.litellm.acompletion', new=AsyncMock(return_value=mock_llm_response)):
                    with patch('src.platform.services.llm_gateway.track_llm_usage'):
                        result = await llm_gateway.chat_completion(
                            messages=sample_messages,
                            use_cache=False
                        )
                        
                        # Should not check cache
                        assert result is not None
                        llm_gateway.redis_client.get.assert_not_called()
