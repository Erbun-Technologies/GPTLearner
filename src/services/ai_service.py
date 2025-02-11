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
        self.client = anthropic.Anthropic(
            api_key=api_key,
            default_headers={"anthropic-version": "2023-06-01"}
        )
        self.model = "claude-3-opus-20240229"  # Using the latest model
        self.max_tokens = 4000  # Default max tokens
        self.curriculum = ""  # Add this line to store curriculum
        logger.debug(f"AIService initialized with model={self.model}, max_tokens={self.max_tokens}")

    def generate_curriculum(self, topic: str, expertise_level: str) -> str:
        """Generate a structured curriculum for the given topic."""
        logger.debug(f"Generating curriculum for topic='{topic}', expertise_level='{expertise_level}'")
        try:
            prompt = (
                "You are an expert curriculum designer. Create a detailed, structured "
                "curriculum that will help someone learn about the requested topic. "
                f"Topic: {topic}\nExpertise Level: {expertise_level}\n\n"
                "Format the curriculum in markdown with clear sections for:\n"
                "1. Learning Objectives\n"
                "2. Prerequisites\n"
                "3. Main Topics (with subtopics)\n"
                "4. Practical Exercises\n"
                "5. Resources\n\n"
                "Make sure the content is appropriate for the specified expertise level."
            )
            logger.debug(f"Generated prompt: {prompt[:200]}...")

            logger.debug("Making API request to Anthropic")
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
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
        """Handle chat interactions with curriculum context.
        
        Args:
            messages: List of message objects with role and content
            curriculum: The curriculum context to include
            
        Returns:
            The assistant's response text
        """
        self.curriculum = curriculum  # Store curriculum for use in chat
        logger.debug(f"Starting chat interaction with {len(messages)} messages")
        logger.debug(f"Curriculum length: {len(curriculum)} chars")
        logger.debug("Using default system prompt")

        # Extract system messages and user/assistant messages
        system_prompt = ("You are an expert tutor helping a student learn according to their curriculum. "
                        "Always reference the curriculum when appropriate, and guide the student through "
                        "their learning journey in a structured way. Be encouraging and supportive, "
                        "while ensuring accurate and in-depth knowledge transfer.")
        
        curriculum_content = f"Current curriculum:\n{curriculum}"

        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                temperature=0.7,
                system=f"{system_prompt}\n\n{curriculum_content}",  # Combined system prompts as top-level parameter
                messages=[
                    # Filter out system messages and only include user/assistant messages
                    msg for msg in messages if msg["role"] != "system"
                ]
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
