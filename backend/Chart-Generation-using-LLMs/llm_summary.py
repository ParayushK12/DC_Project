# Install required packages if needed
# pip install langchain[google-genai]

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# If using environment variable for API Key
api_key = os.getenv("GEMINI_API_KEY")


# Initialize Gemini model (set to use Gemini, adjust model name as needed)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)

# The prompt template for diagram-relevant summary
prompt = ChatPromptTemplate.from_template(
    "From the given passage, produce a structured very concise summary, such that the summary contains only the most relevant nodes (people, objects, steps) and the connections (actions, dependencies, sequences) important for drawing a Mermaid diagram.\n\n{context}"
)





# Example input: Replace with your own text
input_text = '''Alice meets Bob in Paris. They discuss project X and make decisions about funding and deadlines.
Bob travels to Berlin to talk with Carol about implementation. Carol sends updates to Alice. '''


# Convert the text to LangChain Document format
documents = [Document(page_content=input_text)]

# Create summarization chain
chain = create_stuff_documents_chain(llm, prompt)

# Run the summarization chain
result = chain.invoke({"context": documents})

print("Summary for diagram generation:")
print(result)
