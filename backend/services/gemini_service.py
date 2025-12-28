"""
Google Gemini API Integration Service
Generates textual explanations of deforestation findings
"""
import google.generativeai as genai
from pathlib import Path
import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class GeminiExplainer:
    """Generate AI-powered explanations using Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini API client
        
        Args:
            api_key: Google Gemini API key
            model_name: Model to use
        """
        if not api_key:
            raise ValueError("GEMINI_API_KEY not provided")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Initialized Gemini model: {model_name}")
    
    def create_prompt(self, metrics: Dict) -> str:
        """
        Create prompt for Gemini based on detection metrics
        
        Args:
            metrics: Dictionary of deforestation metrics
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a forest monitoring expert analyzing deforestation detection results from satellite imagery analysis.

**Detection Metrics:**
- Total deforested area: {metrics['deforested_area_m2']:.2f} m² ({metrics['deforested_area_hectares']:.2f} hectares)
- Forest loss percentage: {metrics['forest_loss_percentage']:.2f}%
- Number of deforestation patches: {metrics['number_of_patches']}
- Largest contiguous patch: {metrics['largest_patch_m2']:.2f} m² ({metrics['largest_patch_hectares']:.2f} hectares)
- Intact forest remaining: {metrics['intact_forest_hectares']:.2f} hectares
- Total forest area: {metrics['total_area_hectares']:.2f} hectares

**Analysis Required:**
Please provide a comprehensive analysis addressing the following:

1. **Magnitude Assessment**: How much deforestation occurred? Is this significant?

2. **Spatial Distribution**: Based on the number and size of patches, describe the spatial pattern of deforestation. Are changes concentrated or dispersed?

3. **Pattern Analysis**: What do the patch characteristics suggest about the type of deforestation?
   - Large contiguous patches may indicate planned clearing
   - Many small patches may suggest gradual encroachment
   - Linear patterns may indicate road construction or logging

4. **Human Activity Assessment**: Based on the spatial patterns, is this deforestation likely human-driven or natural? Explain your reasoning.

5. **Confidence Score**: Provide a confidence score (0-100) for this analysis based on:
   - Clarity of the patterns
   - Amount of forest loss detected
   - Consistency of the metrics

**Important Guidelines:**
- Base your analysis ONLY on the provided metrics
- Do not speculate about causes not supported by the data
- Do not mention specific locations or regions beyond what's in the data
- Be factual and grounded in the quantitative evidence
- Keep your response concise but comprehensive (300-400 words)

Provide your analysis in a clear, professional tone suitable for forest management stakeholders."""

        return prompt
    
    def generate_explanation(self, metrics: Dict) -> Dict:
        """
        Generate explanation using Gemini API
        
        Args:
            metrics: Dictionary of deforestation metrics
            
        Returns:
            Dictionary with explanation text and confidence score
        """
        try:
            logger.info("Generating explanation with Gemini API...")
            
            # Create prompt
            prompt = self.create_prompt(metrics)
            
            # Generate response
            response = self.model.generate_content(prompt)
            explanation_text = response.text
            
            # Extract confidence score from the response
            confidence_score = self.extract_confidence_score(explanation_text)
            
            result = {
                "explanation": explanation_text,
                "confidence_score": confidence_score,
                "model": "gemini-2.0-flash-exp",
                "status": "success"
            }
            
            logger.info(f"Explanation generated (confidence: {confidence_score})")
            return result
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return {
                "explanation": f"Error generating explanation: {str(e)}",
                "confidence_score": 0,
                "model": "gemini-2.0-flash-exp",
                "status": "error"
            }
    
    def extract_confidence_score(self, text: str) -> int:
        """
        Extract confidence score from Gemini response
        
        Args:
            text: Response text
            
        Returns:
            Confidence score (0-100)
        """
        # Look for patterns like "confidence: 85" or "85/100" or "85%"
        import re
        
        patterns = [
            r'confidence[:\s]+(\d+)',
            r'(\d+)/100',
            r'(\d+)%',
            r'score[:\s]+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                if 0 <= score <= 100:
                    return score
        
        # Default confidence based on metrics quality
        return 75
    
    def save_explanation(self, explanation: Dict, output_path: Path):
        """
        Save explanation to JSON file
        
        Args:
            explanation: Explanation dictionary
            output_path: Where to save
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(explanation, f, indent=2)
        
        logger.info(f"Explanation saved: {output_path}")


if __name__ == "__main__":
    # Test with sample metrics
    logging.basicConfig(level=logging.INFO)
    
    sample_metrics = {
        "deforested_area_m2": 125000,
        "deforested_area_hectares": 12.5,
        "forest_loss_percentage": 5.2,
        "number_of_patches": 8,
        "largest_patch_m2": 45000,
        "largest_patch_hectares": 4.5,
        "intact_forest_hectares": 227.5,
        "total_area_hectares": 240
    }
    
    # This would require a valid API key
    print("GeminiExplainer ready for use")
    print("\nSample prompt:")
    explainer = GeminiExplainer("dummy_key")
    print(explainer.create_prompt(sample_metrics))
