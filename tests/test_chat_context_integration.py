import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.platform.services.chat import ChatService
from src.platform.services.context_tracker import ConversationContext

@pytest.mark.asyncio
class TestChatContextIntegration:
    
    @patch("src.platform.services.llm_gateway.llm_gateway.chat_completion")
    @patch("src.platform.services.orchestrator.proxie_orchestrator.run")
    async def test_extraction_and_prompt_injection(self, mock_orchestrator_run, mock_chat_completion):
        """Verify that info is extracted and passed to orchestrator"""
        chat_service = ChatService()
        
        # 1. Mock Extraction Response
        mock_extraction = MagicMock()
        mock_extraction.choices = [MagicMock()]
        mock_extraction.choices[0].message.content = '{"service_type": "haircut", "city": "Brooklyn"}'
        mock_chat_completion.return_value = mock_extraction
        
        # 2. Mock Orchestrator Run
        mock_orchestrator_run.return_value = (
            "I've got your haircut request in Brooklyn!",
            [],
            {"service_type": "haircut", "city": "Brooklyn"}
        )
        
        # 3. Simulate message
        session_id, response, data, draft, awaiting = await chat_service.handle_chat(
            session_id="test-session",
            message="I need a haircut in Brooklyn",
            role="consumer"
        )
        
        # Verify extraction was called
        mock_chat_completion.assert_called()
        
        # Verify orchestrator was called with the Correct Context
        args, kwargs = mock_orchestrator_run.call_args
        context = kwargs['context']
        assert context['service_type'] == "haircut"
        assert context['city'] == "Brooklyn"
