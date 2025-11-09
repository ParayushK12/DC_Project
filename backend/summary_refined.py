"""
PDF Summary Module for Diagram Generation

This module provides functions to extract text from PDFs and generate
structured summaries suitable for creating Mermaid diagrams.
"""

import os
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from pdf_scanner_alternative import extract_with_pdfplumber
from dotenv import load_dotenv

class PDFSummarizer:
    """Class to handle PDF text extraction and summarization for diagram generation"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the PDF Summarizer
        
        Args:
            api_key: Gemini API key (if None, will load from environment)
            model_name: Gemini model to use
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in environment variables or pass it directly.")
        
        # Initialize Gemini model
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=self.api_key
            )
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini model: {e}")
        
        # Default prompt template for diagram-relevant summary
        self.default_prompt = ChatPromptTemplate.from_template(
            """From the given passage, produce a structured very concise summary that contains only the most relevant:
            - Entities (people, objects, systems, concepts)
            - Relationships (actions, dependencies, sequences, connections)  
            - Processes (steps, workflows, interactions)
            
            Focus on information that would be important for creating a flowchart or Mermaid diagram.
            
            Text: {context}"""
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of text content by page
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If text extraction fails
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            texts = extract_with_pdfplumber(pdf_path)
            if not texts or not any(text.strip() for text in texts):
                raise Exception("No text could be extracted from the PDF")
            return texts
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {e}")
    
    def generate_summary(self, text_content: str, custom_prompt: Optional[str] = None) -> str:
        """
        Generate summary from text content
        
        Args:
            text_content: Text content to summarize
            custom_prompt: Custom prompt template (optional)
            
        Returns:
            Generated summary text
            
        Raises:
            Exception: If summary generation fails
        """
        if not text_content.strip():
            raise ValueError("Text content is empty")
        
        try:
            # Use custom prompt if provided, otherwise use default
            if custom_prompt:
                prompt = ChatPromptTemplate.from_template(custom_prompt + "\n\n{context}")
            else:
                prompt = self.default_prompt
            
            # Convert text to LangChain Document format
            documents = [Document(page_content=text_content)]
            
            # Create summarization chain
            chain = create_stuff_documents_chain(self.llm, prompt)
            
            # Run the summarization chain
            result = chain.invoke({"context": documents})
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to generate summary: {e}")
    
    def summarize_pdf(self, pdf_path: str, custom_prompt: Optional[str] = None) -> dict:
        """
        Complete pipeline: Extract text from PDF and generate summary
        
        Args:
            pdf_path: Path to the PDF file
            custom_prompt: Custom prompt template (optional)
            
        Returns:
            Dictionary containing:
            - 'pdf_path': Path to the processed PDF
            - 'text_content': Extracted text content
            - 'summary': Generated summary
            - 'page_count': Number of pages processed
            
        Raises:
            Exception: If any step in the pipeline fails
        """
        try:
            # Extract text from PDF
            texts = self.extract_text_from_pdf(pdf_path)
            
            # Combine all pages' text into one string
            combined_text = '\n'.join(texts)
            
            # Generate summary
            summary = self.generate_summary(combined_text, custom_prompt)
            
            return {
                'pdf_path': pdf_path,
                'text_content': combined_text,
                'summary': summary,
                'page_count': len(texts)
            }
            
        except Exception as e:
            raise Exception(f"PDF summarization pipeline failed: {e}")

# Convenience functions for backward compatibility and easy usage
def create_summarizer(api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash") -> PDFSummarizer:
    """
    Create a PDF Summarizer instance
    
    Args:
        api_key: Gemini API key (optional)
        model_name: Gemini model name
        
    Returns:
        PDFSummarizer instance
    """
    return PDFSummarizer(api_key=api_key, model_name=model_name)

def summarize_pdf_simple(pdf_path: str, custom_prompt: Optional[str] = None) -> str:
    """
    Simple function to get summary from PDF (creates summarizer internally)
    
    Args:
        pdf_path: Path to the PDF file
        custom_prompt: Custom prompt template (optional)
        
    Returns:
        Generated summary text
    """
    summarizer = create_summarizer()
    result = summarizer.summarize_pdf(pdf_path, custom_prompt)
    return result['summary']

# Main execution (for standalone testing)
if __name__ == "__main__":
    # Example usage when run as standalone script
    pdf_path = "docs/doc1.pdf"  # Update path as needed
    
    try:
        # Method 1: Using the class
        summarizer = PDFSummarizer()
        result = summarizer.summarize_pdf(pdf_path)
        
        print("="*50)
        print("PDF SUMMARIZATION RESULT")
        print("="*50)
        print(f"PDF Path: {result['pdf_path']}")
        print(f"Pages Processed: {result['page_count']}")
        print(f"Text Length: {len(result['text_content'])} characters")
        print("\nSUMMARY:")
        print("-"*30)
        print(result['summary'])
        
        # Method 2: Using the simple function
        # summary = summarize_pdf_simple(pdf_path)
        # print(summary)
        
    except Exception as e:
        print(f"Error: {e}")