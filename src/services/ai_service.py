import os
import anthropic
import logging
from typing import List, Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler with formatting
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

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

    def chat(self, 
             messages: List[Dict[str, str]], 
             curriculum: str,
             system_prompt: Optional[str] = None) -> str:
        """Handle chat interactions with curriculum context.
        
        Args:
            messages: List of message objects with role and content
            curriculum: The curriculum context to include
            system_prompt: Optional system prompt to override default
            
        Returns:
            The assistant's response text
            
        Raises:
            ValueError: If there is an error calling the API
        """
        try:
            logger.debug(f"Starting chat interaction with {len(messages)} messages")
            logger.debug(f"Curriculum length: {len(curriculum)} chars")
            
            if system_prompt is None:
                logger.debug("Using default system prompt")
                system_prompt = (
                    "You are an expert tutor helping a student learn according to their curriculum. "
                    "Always reference the curriculum when appropriate, and guide the student through "
                    "their learning journey in a structured way. Be encouraging and supportive, "
                    "while ensuring accurate and in-depth knowledge transfer."
                )

            # Combine system prompt, curriculum context, and chat history
            full_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"Current curriculum:\n{curriculum}"},
                *messages
            ]
            
            logger.debug("Making chat API request to Anthropic")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.7,
                messages=full_messages
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
