import os
import anthropic
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class AIService:
    """Service for interacting with Anthropic's Claude API."""
    
    def __init__(self):
        logger.debug("Initializing AIService")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY environment variable not found")
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not found. "
                "Please set it before running the application."
            )
        logger.debug("API key found, initializing Anthropic client")
        
        # Initialize client with latest API version
        self.client = anthropic.Anthropic(
            api_key=api_key,
            default_headers={"anthropic-version": "2023-06-01"}
        )
        
        # Use specific model version for stability and predictability
        self.model = "claude-3-opus-20240229"
        
        # Set optimal token limits
        self.max_tokens = 4000  # Default max tokens for responses
        self.max_context_tokens = 8000  # Maximum context window size
        
        logger.debug(f"AIService initialized with model={self.model}, max_tokens={self.max_tokens}")

    def generate_curriculum(self, topic: str, expertise_level: str) -> str:
        """Generate a structured curriculum for the given topic."""
        logger.debug(f"Generating curriculum for topic='{topic}', expertise_level='{expertise_level}'")
        try:
            # Create a focused system prompt
            system_prompt = (
                "You are an expert curriculum designer. Create a detailed, structured curriculum "
                "that is precisely tailored to the specified expertise level. Be concise but thorough. "
                "Focus on practical, actionable learning steps."
            )
            
            # Create a focused user message
            message_content = (
                f"Create a curriculum for learning {topic} at a {expertise_level} level.\n\n"
                "Structure it with these sections:\n"
                "1. Learning Objectives (3-5 key objectives)\n"
                "2. Prerequisites (essential background knowledge)\n"
                "3. Main Topics (with brief subtopics)\n"
                "4. Practical Exercises\n"
                "5. Key Resources\n\n"
                "Make all content specifically appropriate for {expertise_level} level learners."
            )

            logger.debug("Making API request to Anthropic")
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.7,  # Balanced between creativity and consistency
                system=system_prompt,
                messages=[
                    {"role": "user", "content": message_content}
                ]
            )
            
            logger.debug(f"Received response with ID: {message.id}")
            logger.debug(f"Input tokens: {message.usage.input_tokens}, Output tokens: {message.usage.output_tokens}")
            logger.debug(f"Stop reason: {message.stop_reason}")
            
            response_text = message.content[0].text
            logger.debug(f"Response preview: {response_text[:200]}...")
            return response_text

        except anthropic.APIError as e:
            logger.error(f"Anthropic API Error: {str(e)}", exc_info=True)
            raise ValueError(f"API Error: {str(e)}")
        except anthropic.APIConnectionError as e:
            logger.error(f"Anthropic Connection Error: {str(e)}", exc_info=True)
            raise ValueError(f"Connection Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise ValueError(f"Unexpected error: {str(e)}")

    def chat(self, messages: List[Dict[str, str]], curriculum: str) -> str:
        """Handle chat interactions with curriculum context."""
        logger.debug(f"Starting chat interaction with {len(messages)} messages")
        logger.debug(f"Curriculum length: {len(curriculum)} chars")
        
        try:
            # Create focused system prompt with curriculum context
            system_prompt = (
                "You are an expert tutor helping a student learn according to their curriculum. "
                "Keep responses focused and concise while being helpful. "
                "Reference specific parts of the curriculum when relevant. "
                "Guide the student through their learning journey in a structured way."
            )
            
            # Add curriculum as context but keep it concise
            curriculum_summary = curriculum[:2000] + "..." if len(curriculum) > 2000 else curriculum
            system_context = f"{system_prompt}\n\nCurrent curriculum:\n{curriculum_summary}"

            # Filter and optimize message history
            optimized_messages = self._optimize_message_history(messages)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.7,
                system=system_context,
                messages=optimized_messages
            )
            
            logger.debug(f"Received chat response with ID: {response.id}")
            logger.debug(f"Input tokens: {response.usage.input_tokens}, Output tokens: {response.usage.output_tokens}")
            logger.debug(f"Stop reason: {response.stop_reason}")
            
            response_text = response.content[0].text
            logger.debug(f"Chat response preview: {response_text[:200]}...")
            return response_text
            
        except anthropic.APIError as e:
            logger.error(f"Anthropic API Error in chat: {str(e)}", exc_info=True)
            raise ValueError(f"API Error: {str(e)}")
        except anthropic.APIConnectionError as e:
            logger.error(f"Anthropic Connection Error in chat: {str(e)}", exc_info=True)
            raise ValueError(f"Connection Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in chat: {str(e)}", exc_info=True)
            raise ValueError(f"Unexpected error: {str(e)}")

    def _optimize_message_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Optimize message history to reduce token usage while maintaining context."""
        # Keep only the last 10 messages to prevent context window overflow
        recent_messages = messages[-10:]
        
        # Ensure messages follow the correct format
        optimized = []
        for msg in recent_messages:
            # Ensure content isn't too long
            content = msg["content"]
            if len(content) > 1000:  # Arbitrary limit to prevent huge messages
                content = content[:997] + "..."
            
            optimized.append({
                "role": msg["role"],
                "content": content
            })
        
        return optimized
