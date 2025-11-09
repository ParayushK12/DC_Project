"""
Mermaid Code Generator

This module generates Mermaid diagram code from PDF documents using:
1. PDF text extraction and summarization (via summary_refined module)
2. Mermaid code generation (via Mistral AI)
"""

import os
from typing import Optional, Dict, Any
from mistralai import Mistral
from dotenv import load_dotenv
from summary_refined import PDFSummarizer

class MermaidCodeGenerator:
    """Class to generate Mermaid diagram code from PDF documents"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-large-latest"):
        """
        Initialize the Mermaid Code Generator
        
        Args:
            api_key: Mistral API key (if None, will load from environment)
            model: Mistral model to use
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found. Please set it in environment variables or pass it directly.")
        
        # Initialize Mistral client
        self.model = model
        self.client = Mistral(api_key=self.api_key)
        
        # Initialize PDF summarizer
        self.summarizer = PDFSummarizer()
        
        # Default Mermaid generation prompt
        self.default_mermaid_prompt = """Generate a well-structured Mermaid flowchart code from the following text summary.

Requirements:
1. Use 'flowchart TD' (top-down) or 'flowchart LR' (left-right) syntax
2. Create meaningful node IDs (A, B, C... or descriptive names)
3. Use appropriate node shapes:
   - [Text] for processes/actions
   - (Text) for start/end points
   - {Text} for decisions/conditionals
   - [(Text)] for data/databases
   - [[Text]] for subroutines
4. Add clear edge labels using |label text| syntax
5. Group related concepts in subgraphs if applicable
6. Include basic styling if it enhances readability

Text Summary:
{summary}

Generate only valid Mermaid code (no explanations):"""

    def generate_mermaid_prompt(self, summary: str, custom_prompt: Optional[str] = None) -> str:
        """
        Generate the prompt for Mermaid code creation
        
        Args:
            summary: Text summary to convert
            custom_prompt: Custom prompt template (optional)
            
        Returns:
            Formatted prompt string
        """
        if custom_prompt:
            return custom_prompt.format(summary=summary)
        return self.default_mermaid_prompt.format(summary=summary)

    def generate_mermaid_code(self, summary: str, custom_prompt: Optional[str] = None) -> str:
        """
        Generate Mermaid code from text summary
        
        Args:
            summary: Text summary to convert
            custom_prompt: Custom prompt template (optional)
            
        Returns:
            Generated Mermaid code
            
        Raises:
            Exception: If Mermaid code generation fails
        """
        if not summary.strip():
            raise ValueError("Summary text is empty")
        
        try:
            # Generate the prompt
            prompt = self.generate_mermaid_prompt(summary, custom_prompt)
            
            # Call Mistral API
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ]
            )
            
            mermaid_code = chat_response.choices[0].message.content.strip()
            
            # Basic validation - check if it looks like Mermaid code
            if not any(keyword in mermaid_code.lower() for keyword in ['flowchart', 'graph', 'sequencediagram', 'classDiagram']):
                print("Warning: Generated code may not be valid Mermaid syntax")
            
            return mermaid_code
            
        except Exception as e:
            raise Exception(f"Failed to generate Mermaid code: {e}")

    def process_pdf_to_mermaid(self, pdf_path: str, custom_summary_prompt: Optional[str] = None, 
                              custom_mermaid_prompt: Optional[str] = None, 
                              save_to_file: bool = True, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete pipeline: PDF → Summary → Mermaid Code
        
        Args:
            pdf_path: Path to the PDF file
            custom_summary_prompt: Custom prompt for summarization (optional)
            custom_mermaid_prompt: Custom prompt for Mermaid generation (optional)
            save_to_file: Whether to save the result to a file
            output_file: Output file path (optional, auto-generated if None)
            
        Returns:
            Dictionary containing all results
            
        Raises:
            Exception: If any step in the pipeline fails
        """
        try:
            # Step 1: Generate summary from PDF
            print("Extracting and summarizing PDF...")
            summary_result = self.summarizer.summarize_pdf(pdf_path, custom_summary_prompt)
            
            # Step 2: Generate Mermaid code from summary
            print("Generating Mermaid code...")
            mermaid_code = self.generate_mermaid_code(summary_result['summary'], custom_mermaid_prompt)
            
            # Step 3: Save to file if requested
            if save_to_file:
                if not output_file:
                    # Auto-generate filename
                    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                    output_file = f"{base_name}_diagram.mmd"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(mermaid_code)
                print(f"Mermaid code saved to: {output_file}")
            
            return {
                'pdf_path': pdf_path,
                'summary': summary_result['summary'],
                'mermaid_code': mermaid_code,
                'output_file': output_file if save_to_file else None,
                'page_count': summary_result['page_count'],
                'text_length': len(summary_result['text_content'])
            }
            
        except Exception as e:
            raise Exception(f"PDF to Mermaid pipeline failed: {e}")

    def display_results(self, result: Dict[str, Any]) -> None:
        """
        Display the results in a formatted way
        
        Args:
            result: Result dictionary from process_pdf_to_mermaid
        """
        print("\n" + "="*60)
        print("MERMAID CODE GENERATION RESULTS")
        print("="*60)
        print(f"PDF File: {result['pdf_path']}")
        print(f"Pages Processed: {result['page_count']}")
        print(f"Text Length: {result['text_length']} characters")
        if result['output_file']:
            print(f"Output File: {result['output_file']}")
        
        print("\n" + "-"*30)
        print("SUMMARY:")
        print("-"*30)
        print(result['summary'])
        
        print("\n" + "-"*30)
        print("GENERATED MERMAID CODE:")
        print("-"*30)
        print(result['mermaid_code'])
        print("\n" + "="*60)

# Convenience functions
def generate_mermaid_from_pdf(pdf_path: str, output_file: Optional[str] = None) -> str:
    """
    Simple function to generate Mermaid code from PDF
    
    Args:
        pdf_path: Path to the PDF file
        output_file: Output file path (optional)
        
    Returns:
        Generated Mermaid code
    """
    generator = MermaidCodeGenerator()
    result = generator.process_pdf_to_mermaid(pdf_path, output_file=output_file)
    return result['mermaid_code']

def create_generator(api_key: Optional[str] = None, model: str = "mistral-large-latest") -> MermaidCodeGenerator:
    """
    Create a Mermaid Code Generator instance
    
    Args:
        api_key: Mistral API key (optional)
        model: Mistral model name
        
    Returns:
        MermaidCodeGenerator instance
    """
    return MermaidCodeGenerator(api_key=api_key, model=model)

# Main execution
if __name__ == "__main__":
    # Configuration
    pdf_path = "/home/darpan/Desktop/Blockdiagram/Chart-Generation-using-LLMs/docs/doc1.pdf"  # Update this path
    
    try:
        # Method 1: Using the class (recommended)
        generator = MermaidCodeGenerator()
        result = generator.process_pdf_to_mermaid(pdf_path)
        generator.display_results(result)
        
        # Method 2: Using the simple function
        # mermaid_code = generate_mermaid_from_pdf(pdf_path)
        # print(mermaid_code)
        
    except FileNotFoundError:
        print(f"Error: PDF file not found: {pdf_path}")
        print("Please update the pdf_path variable with a valid file path.")
    except Exception as e:
        print(f"Error: {e}")