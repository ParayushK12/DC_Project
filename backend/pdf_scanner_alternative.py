# Alternative PDF text extraction methods

def extract_with_pdfplumber(pdf_path):
    """Using pdfplumber - often better for complex layouts"""
    import pdfplumber
    
    text_by_page = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            text_by_page.append(text if text else "[No text found]")
    return text_by_page

# def extract_with_pymupdf(pdf_path):
#     """Using PyMuPDF (fitz) - good for various PDF types"""
#     import fitz  # PyMuPDF
    
#     text_by_page = []
#     doc = fitz.open(pdf_path)
#     for page_num in range(doc.page_count):
#         page = doc[page_num]
#         text = page.get_text()
#         text_by_page.append(text if text else "[No text found]")
#     doc.close()
#     return text_by_page

# def extract_with_pdfminer(pdf_path):
#     """Using pdfminer3k - handles complex encodings well"""
#     from pdfminer.high_level import extract_text
    
#     try:
#         text = extract_text(pdf_path)
#         # Split by form feed character (page breaks)
#         pages = text.split('\f')
#         return [page.strip() for page in pages if page.strip()]
#     except Exception as e:
#         print(f"Error with pdfminer: {e}")
#         return []

if __name__ == "__main__":
    pdf_path = "Chart-Generation-using-LLMs/docs/doc1.pdf"
    

    try:
        texts = extract_with_pdfplumber(pdf_path)
        for i, page_text in enumerate(texts, start=1):
            print(f"--- Page {i} ---")
            print(page_text)
            print()
    except ImportError:
        print("pdfplumber not installed. Install with: pip install pdfplumber")
    except Exception as e:
        print(f"pdfplumber failed: {e}")
    
    # print("\n=== Trying PyMuPDF ===")
    # try:
    #     texts = extract_with_pymupdf(pdf_path)
    #     for i, page_text in enumerate(texts, start=1):
    #         print(f"--- Page {i} ---")
    #         print(page_text[:200] + "..." if len(page_text) > 200 else page_text)
    #         print()
    # except ImportError:
    #     print("PyMuPDF not installed. Install with: pip install PyMuPDF")
    # except Exception as e:
    #     print(f"PyMuPDF failed: {e}")