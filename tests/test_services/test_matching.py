"""
Unit tests for MatchingService.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.orm import Session

from src.platform.services.matching import MatchingService
from src.platform.schemas.request import ServiceRequestCreate, RequestLocation, RequestTiming, RequestBudget, RequestRequirements


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def matching_service(mock_db):
    """Create MatchingService instance."""
    return MatchingService(mock_db)


@pytest.fixture
def sample_request():
    """Sample service request for testing."""
    return ServiceRequestCreate(
        consumer_id=str(uuid4()),
        raw_input="I need a haircut for curly hair in Brooklyn",
        service_category="hairstylist",
        service_type="haircut",
        requirements=RequestRequirements(description="curly hair specialist"),
        location=RequestLocation(city="Brooklyn", neighborhood="Bed-Stuy"),
        timing=RequestTiming(urgency="specific_date"),
        budget=RequestBudget(min=60, max=80, currency="USD")
    )


@pytest.fixture
def mock_providers():
    """Mock provider objects."""
    provider1 = Mock()
    provider1.id = uuid4()
    provider1.status = "active"
    provider1.location = {"city": "Brooklyn"}
    
    provider2 = Mock()
    provider2.id = uuid4()
    provider2.status = "active"
    provider2.location = {"city": "Brooklyn"}
    
    return [provider1, provider2]


class TestMatchingService:
    """Test MatchingService functionality."""
    
    @pytest.mark.asyncio
    async def test_find_providers_dev_environment(self, matching_service, sample_request, mock_providers):
        """In dev/test environment, should return all active providers."""
        with patch('src.platform.services.matching.settings') as mock_settings:
            mock_settings.ENVIRONMENT = "development"
            
            # Mock query
            mock_query = Mock()
            matching_service.db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value.all.return_value = mock_providers
            
            result = await matching_service.find_providers(sample_request)
            
            assert len(result) == 2
            assert result[0] == mock_providers[0].id
            assert result[1] == mock_providers[1].id
    
    @pytest.mark.asyncio
    async def test_find_providers_with_semantic_matching(self, matching_service, sample_request, mock_providers):
        """Should use semantic matching when enabled."""
        with patch('src.platform.services.matching.settings') as mock_settings:
            mock_settings.ENVIRONMENT = "production"
            
            with patch('src.platform.services.matching.embedding_service') as mock_embedding:
                # Mock embedding
                mock_embedding.get_embedding = AsyncMock(return_value=[0.1] * 3072)
                
                # Mock query chain
                mock_query = Mock()
                matching_service.db.query.return_value = mock_query
                mock_query.filter.return_value = mock_query
                mock_query.join.return_value = mock_query
                mock_query.order_by.return_value = mock_query
                mock_query.distinct.return_value = mock_query
                mock_query.limit.return_value.all.return_value = mock_providers
                
                result = await matching_service.find_providers(sample_request, use_semantic=True)
                
                # Verify embedding was called
                mock_embedding.get_embedding.assert_called_once()
                assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_find_providers_keyword_fallback(self, matching_service, sample_request, mock_providers):
        """Should fallback to keyword matching when semantic fails."""
        with patch('src.platform.services.matching.settings') as mock_settings:
            mock_settings.ENVIRONMENT = "production"
            
            with patch('src.platform.services.matching.embedding_service') as mock_embedding:
                # Mock embedding failure
                mock_embedding.get_embedding = AsyncMock(side_effect=Exception("Embedding failed"))
                
                # Mock query chain
                mock_query = Mock()
                matching_service.db.query.return_value = mock_query
                mock_query.filter.return_value = mock_query
                mock_query.join.return_value = mock_query
                mock_query.distinct.return_value = mock_query
                mock_query.limit.return_value.all.return_value = mock_providers
                
                result = await matching_service.find_providers(sample_request, use_semantic=True)
                
                # Should still return results using keyword fallback
                assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_find_providers_without_semantic(self, matching_service, sample_request, mock_providers):
        """Should use keyword matching when semantic is disabled."""
        with patch('src.platform.services.matching.settings') as mock_settings:
            mock_settings.ENVIRONMENT = "production"
            
            # Mock query chain
            mock_query = Mock()
            matching_service.db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.join.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.limit.return_value.all.return_value = mock_providers
            
            result = await matching_service.find_providers(sample_request, use_semantic=False)
            
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_update_provider_embedding(self, matching_service):
        """Should update provider embedding successfully."""
        provider_id = uuid4()
        mock_provider = Mock()
        mock_provider.id = provider_id
        mock_provider.business_name = "Test Salon"
        mock_provider.bio = "Expert hairstylist"
        mock_provider.specializations = ["curly hair"]
        
        mock_service = Mock()
        mock_service.name = "Haircut"
        
        # Mock database queries
        matching_service.db.query.return_value.get.return_value = mock_provider
        matching_service.db.query.return_value.filter.return_value.all.return_value = [mock_service]
        
        with patch('src.platform.services.matching.embedding_service') as mock_embedding:
            mock_embedding.get_embedding = AsyncMock(return_value=[0.1] * 3072)
            
            await matching_service.update_provider_embedding(provider_id)
            
            # Verify embedding was generated
            mock_embedding.get_embedding.assert_called_once()
            # Verify commit was called
            matching_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_provider_embedding_provider_not_found(self, matching_service):
        """Should handle provider not found gracefully."""
        provider_id = uuid4()
        
        # Mock provider not found
        matching_service.db.query.return_value.get.return_value = None
        
        # Should not raise exception
        await matching_service.update_provider_embedding(provider_id)
        
        # Should not call commit
        matching_service.db.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_provider_embedding_embedding_failure(self, matching_service):
        """Should handle embedding generation failure gracefully."""
        provider_id = uuid4()
        mock_provider = Mock()
        mock_provider.id = provider_id
        mock_provider.business_name = "Test Salon"
        mock_provider.bio = None
        mock_provider.specializations = []
        
        matching_service.db.query.return_value.get.return_value = mock_provider
        matching_service.db.query.return_value.filter.return_value.all.return_value = []
        
        with patch('src.platform.services.matching.embedding_service') as mock_embedding:
            mock_embedding.get_embedding = AsyncMock(side_effect=Exception("API Error"))
            
            # Should not raise exception
            await matching_service.update_provider_embedding(provider_id)
            
            # Should not call commit on failure
            matching_service.db.commit.assert_not_called()
    
    def test_matching_service_initialization(self, mock_db):
        """Test MatchingService initialization."""
        service = MatchingService(mock_db)
        assert service.db == mock_db
