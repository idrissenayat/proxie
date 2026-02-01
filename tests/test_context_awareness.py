import pytest
from src.platform.services.context_tracker import ConversationContext, ContextSource

class TestContextAwareness:
    
    def test_geographic_sync(self):
        """Verify city syncs to location for requirements"""
        context = ConversationContext()
        context.update_from_extraction({"city": "Brooklyn"}, ContextSource.CURRENT_MESSAGE)
        
        assert context.location == "Brooklyn"
        missing = context.get_missing_required("service_request")
        assert "location" not in missing
        
        # Test address sync
        context = ConversationContext()
        context.update_from_extraction({"address": "123 Main St, NY"}, ContextSource.CURRENT_MESSAGE)
        summary = context.get_known_summary()
        assert "location" in summary
        assert summary["location"] == "123 Main St, NY"
    
    def test_profile_loading(self):
        """Verify profile data is loaded into context"""
        context = ConversationContext()
        profile = {
            "name": "Maya",
            "email": "maya@test.com",
            "default_location": "Brooklyn"
        }
        context.update_from_profile(profile)
        
        assert context.name == "Maya"
        assert context.default_location == "Brooklyn"
    
    def test_extraction_updates_context(self):
        """Verify extracted info is added to context"""
        context = ConversationContext()
        extracted = {
            "service_type": "haircut",
            "location": "Williamsburg",
            "budget_max": 50
        }
        context.update_from_extraction(extracted, ContextSource.CURRENT_MESSAGE)
        
        assert context.service_type == "haircut"
        assert context.location == "Williamsburg"
        assert context.budget_max == 50
    
    def test_update_from_current_message(self):
        """Verify current message updates existing values (corrections)"""
        context = ConversationContext()
        context.location = "Brooklyn"
        
        extracted = {"location": "Manhattan"}
        context.update_from_extraction(extracted, ContextSource.CURRENT_MESSAGE)
        
        assert context.location == "Manhattan"

    def test_missing_required_fields(self):
        """Verify correct identification of missing required fields"""
        context = ConversationContext()
        context.service_type = "haircut"
        # location is missing
        
        missing = context.get_missing_required("service_request")
        assert "location" in missing
        assert "service_type" not in missing
    
    def test_known_summary(self):
        """Verify known summary excludes None values"""
        context = ConversationContext()
        context.name = "Test"
        context.service_type = "cleaning"
        # location is None
        
        summary = context.get_known_summary()
        assert "name" in summary
        assert "service_type" in summary
        assert "location" not in summary
