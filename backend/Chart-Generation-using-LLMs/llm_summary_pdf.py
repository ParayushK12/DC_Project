# # Install required packages if needed
# # pip install langchain[google-genai]

# import os
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.documents import Document
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from pdf_scanner_alternative import extract_with_pdfplumber
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()
# # If using environment variable for API Key
# api_key = os.getenv("GEMINI_API_KEY")
# # Initialize Gemini model (set to use Gemini, adjust model name as needed)
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)

# # The prompt template for diagram-relevant summary
# prompt = ChatPromptTemplate.from_template(
#     "From the given passage, produce a structured very concise summary, such that the summary contains only the most relevant nodes (people, objects, steps) and the connections (actions, dependencies, sequences) important for drawing a Mermaid diagram.\n\n{context}"
# )



# pdf_path = "Chart-Generation-using-LLMs/docs/doc3.pdf"  # Replace with your PDF file path
# texts = extract_with_pdfplumber(pdf_path)

# # Example input: Replace with your own text
# input_text = '\n'.join(texts)  # Combine all pages' text into one string


# # Convert the text to LangChain Document format
# documents = [Document(page_content=input_text)]

# # Create summarization chain
# chain = create_stuff_documents_chain(llm, prompt)

# # Run the summarization chain
# result = chain.invoke({"context": documents})

# print("Summary for diagram generation:")
# print(result)



import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdf_scanner_alternative import extract_with_pdfplumber
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)

class EnhancedPDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " "]
        )
        
        # Different prompts for different stages
        self.section_summary_prompt = ChatPromptTemplate.from_template(
            """Analyze this section of a research paper and identify:
            1. Key processes, methods, or workflows
            2. Important entities (systems, components, people, concepts)
            3. Relationships and dependencies between entities
            4. Sequential steps or procedures
            
            Focus on information that would be useful for creating a flowchart or process diagram.
            
            Section text: {context}
            
            Provide a structured summary focusing on diagram-relevant information:"""
        )
        
        self.final_mermaid_prompt = ChatPromptTemplate.from_template(
            """Based on these section summaries from a research paper, create a comprehensive Mermaid flowchart that captures:
            1. The main workflow/process described in the paper
            2. Key components and their relationships
            3. Decision points and branches
            4. Input/output flows
            
            Use appropriate Mermaid syntax with:
            - Different node shapes for different types (processes, decisions, data, etc.)
            - Clear labels and connections
            - Subgraphs for related components when appropriate
            
            Section summaries:
            {context}
            
            Generate a detailed Mermaid flowchart code without '''```mermaid''' tags."""
        )

    def process_long_pdf(self, pdf_path):
        # Extract text from PDF
        texts = extract_with_pdfplumber(pdf_path)
        full_text = '\n'.join(texts)
        
        # Split into manageable chunks
        chunks = self.text_splitter.split_text(full_text)
        
        # Process each chunk to get section summaries
        section_summaries = []
        section_chain = create_stuff_documents_chain(llm, self.section_summary_prompt)
        
        print(f"Processing {len(chunks)} sections...")
        for i, chunk in enumerate(chunks):
            print(f"Processing section {i+1}/{len(chunks)}")
            documents = [Document(page_content=chunk)]
            summary = section_chain.invoke({"context": documents})
            section_summaries.append(summary)
        
        # Combine summaries to create final Mermaid diagram
        combined_summaries = '\n\n'.join(section_summaries)
        final_documents = [Document(page_content=combined_summaries)]
        
        mermaid_chain = create_stuff_documents_chain(llm, self.final_mermaid_prompt)
        mermaid_code = mermaid_chain.invoke({"context": final_documents})
        
        return mermaid_code, section_summaries

if __name__ == "__main__":
    processor = EnhancedPDFProcessor()
    pdf_path = "Chart-Generation-using-LLMs/docs/doc1.pdf"
    
    mermaid_code, summaries = processor.process_long_pdf(pdf_path)
    
    print("Generated Mermaid Code:")
    print(mermaid_code)
    
    # Save to file
    with open("enhanced_output.mmd", "w") as f:
        f.write(mermaid_code)