# digitally embedded text extraction from PDF files
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text_by_page = []
    for page in reader.pages:
        text = page.extract_text()
        text_by_page.append(text)
    return text_by_page

if __name__ == "__main__":
    pdf_path = "Chart-Generation-using-LLMs/docs/doc1.pdf"  # Replace with your PDF file path
    texts = extract_text_from_pdf(pdf_path)
    for i, page_text in enumerate(texts, start=1):
        print(f"--- Page {i} ---")
        print(page_text)
        print()
