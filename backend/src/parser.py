import json
import re
import logging
from typing import Dict, Any, Tuple

class ResearchResponseParser:
    """
    A parser for extracting structured research responses from RAG system outputs.
    Focuses on parsing JSON structures and handling mixed-format responses.
    """
    
    @staticmethod
    def parse(text: str) -> Dict[str, Any]:
        """
        Main parsing method that processes responses from the RAG agent.
        
        Args:
            text (str): Raw response text from the agent, which may contain:
                      - JSON structures with backticks
                      - Tool call information
                      - Textual content
                      - Mixed formats
            
        Returns:
            Dict[str, Any]: Structured response with keys:
                          - topic: Research topic
                          - summary: Main content summary
                          - sources: List of information sources
                          - tools_used: List of tools utilized
                          - entities: List of entities from the BaseModel (if provided)
        """
        try:
            # Handle case where input is already a dictionary
            if isinstance(text, dict):
                return ResearchResponseParser._validate_structure(text)
            
            # Extract JSON structure from the response
            json_part, text_content = ResearchResponseParser._extract_both_parts(text)
            
            parsed_data = {}
            
            # Parse JSON component if available
            if json_part:
                try:
                    parsed_data = json.loads(json_part)
                except json.JSONDecodeError as e:
                    logging.warning(f"JSON parsing failed: {e}")
                    # If JSON parsing fails, use text content as summary
                    parsed_data = {"summary": text_content or text}
            else:
                # No JSON found, use entire text as summary
                parsed_data = {"summary": text}
            
            # Validate and ensure all required fields are present
            return ResearchResponseParser._validate_structure(parsed_data)
            
        except Exception as e:
            logging.error(f"Comprehensive parsing error: {e}")
            return ResearchResponseParser._create_error_response(str(e))
    
    @staticmethod
    def _extract_both_parts(text: str) -> Tuple[str, str]:
        """
        Extracts JSON structure and additional text content from mixed response.
        
        Args:
            text (str): Raw response text that may contain JSON and free text
            
        Returns:
            Tuple[str, str]: (json_part, text_content)
                           - json_part: Extracted JSON string or empty string
                           - text_content: Remaining text content after JSON
        """
        json_part = ""
        text_content = ""
        
        if not text:
            return json_part, text_content
        
        # Pattern 1: JSON with code block backticks (```json { ... } ```)
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            json_part = json_match.group(1).strip()
            text_content = text[json_match.end():].strip()
            return json_part, text_content
        
        # Pattern 2: Simple JSON object without backticks
        json_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if json_match:
            json_part = json_match.group(1).strip()
            text_content = text[json_match.end():].strip()
            return json_part, text_content
        
        # Pattern 3: No JSON found, entire text is content
        text_content = text.strip()
        return json_part, text_content
    
    
    
    @staticmethod
    def _clean_text_content(text: str) -> str:
        """
        Cleans and formats text content for better presentation.
        
        Args:
            text (str): Raw text content
            
        Returns:
            str: Cleaned and formatted text
        """
        if not text:
            return ""
        
        # Remove numbered list markers at line starts
        cleaned = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
        
        # Normalize line breaks and whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        
        # Remove tool call artifacts if present
        cleaned = re.sub(r'\[\{.*?\}\]\s*\n?', '', cleaned)
        
        return cleaned.strip()
    
    @staticmethod
    def _validate_structure(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates and ensures the response structure contains all required fields.
        Entities are taken directly from the BaseModel without extraction.
        
        Args:
            data (Dict[str, Any]): Parsed data to validate
            
        Returns:
            Dict[str, Any]: Validated and complete structure
        """
        if not isinstance(data, dict):
            return ResearchResponseParser._create_error_response("Response is not a valid dictionary")
        
        # Ensure all required fields are present with proper types
        # Entities are taken as-is from the BaseModel response
        validated = {
            "topic": str(data.get("topic", "Unknown Topic")),
            "summary": str(data.get("summary", "No summary available")),
            "sources": ResearchResponseParser._ensure_list(data.get("sources")),
            "tools_used": ResearchResponseParser._ensure_list(data.get("tools_used")),
            "entities": ResearchResponseParser._ensure_list(data.get("entities", []))  # Use entities from BaseModel
        }
        
        return validated
    
    @staticmethod
    def _ensure_list(value: Any) -> list:
        """
        Ensures the value is a list, converting if necessary.
        
        Args:
            value (Any): Value to convert to list
            
        Returns:
            list: Valid list
        """
        if value is None:
            return []
        elif isinstance(value, list):
            return value
        elif isinstance(value, str):
            return [value] if value.strip() else []
        else:
            return [str(value)]
    
    @staticmethod
    def _create_error_response(error_message: str) -> Dict[str, Any]:
        """
        Creates a standardized error response structure.
        
        Args:
            error_message (str): Error description
            
        Returns:
            Dict[str, Any]: Error response structure
        """
        return {
            "topic": "Parsing Error", 
            "summary": f"Could not parse the response: {error_message}",
            "sources": [],
            "tools_used": [],
            "entities": []
        }