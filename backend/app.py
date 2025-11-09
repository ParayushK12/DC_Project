from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import sys
import traceback
import re

# Add the path to your endtoend.py script

sys.path.append("/home/darpan/Desktop/Blockdiagram/Chart-Generation-using-LLMs")
from endtoend import pdf_to_mermaid_complete, text_to_mermaid_complete
from summary_refined import PDFSummarizer
# Note: import mermaid_code lazily inside endpoints to avoid import-time
# failures when model SDKs (e.g., mistralai) are not installed in the
# execution environment.

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend


@app.route('/', methods=['GET'])
def index():
    """Simple index route to help with debugging and to avoid 404 on root access."""
    return jsonify({
        'service': 'Blockdiagram backend',
        'endpoints': {
            '/api/process-pdf': 'POST (upload PDF file)',
            '/api/process-text': 'POST (send raw text as JSON {"text": "..."})',
            '/health': 'GET (health check)'
        },
        'notes': 'See README for usage. Use POST /api/process-pdf with form-data file=@your.pdf'
    })


@app.errorhandler(404)
def not_found(e):
    """Return JSON for 404s so clients get a helpful message instead of HTML."""
    return jsonify({
        'error': 'Not Found',
        'message': 'Requested URL was not found on the server.',
        'available_endpoints': ['/','/health','/api/process-pdf','/api/process-text']
    }), 404

@app.route('/api/process-pdf', methods=['POST'])
def process_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        # Create temporary file for the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            file.save(temp_pdf.name)
            temp_pdf_path = temp_pdf.name
        
        # Create temporary file for the output HTML
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w') as temp_html:
            temp_html_path = temp_html.name
        
        try:
            # Process the PDF using your endtoend.py function
            results = pdf_to_mermaid_complete(
                pdf_path=temp_pdf_path,
                output_file=temp_html_path
            )
            
            # Read the generated HTML content
            with open(temp_html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract just the Mermaid code from the <pre> tag
            mermaid_match = re.search(r'<pre class="mermaid">\s*(.*?)\s*</pre>', html_content, re.DOTALL)
            mermaid_code_for_display = mermaid_match.group(1).strip() if mermaid_match else results['mermaid_code']
            
            return jsonify({
                'success': True,
                'mermaid_code': mermaid_code_for_display,
                'raw_mermaid': results['mermaid_code'],
                'summary': results['summary'],
                'stats': {
                    'text_length': results['text_length'],
                    'summary_length': results['summary_length'],
                    'mermaid_length': results['mermaid_length']
                }
            })
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
            if os.path.exists(temp_html_path):
                os.unlink(temp_html_path)
                
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.route('/api/process-text', methods=['POST'])
def process_text():
    try:
        payload = request.get_json()
        if not payload or 'text' not in payload:
            return jsonify({'error': 'No text provided'}), 400

        text = payload.get('text', '')
        if not isinstance(text, str) or not text.strip():
            return jsonify({'error': 'Text must be a non-empty string'}), 400

        # Create temporary file for the output HTML
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w') as temp_html:
            temp_html_path = temp_html.name

        try:
            # Process the text using the text_to_mermaid_complete function
            results = text_to_mermaid_complete(
                input_text=text,
                output_file=temp_html_path
            )

            # Read the generated HTML content (if file was written)
            mermaid_code_for_display = results.get('mermaid_code')
            if os.path.exists(temp_html_path):
                try:
                    with open(temp_html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    mermaid_match = re.search(r'<pre class="mermaid">\s*(.*?)\s*</pre>', html_content, re.DOTALL)
                    mermaid_code_for_display = mermaid_match.group(1).strip() if mermaid_match else results.get('mermaid_code')
                except Exception:
                    # fallback to returned mermaid code if reading file fails
                    mermaid_code_for_display = results.get('mermaid_code')

            return jsonify({
                'success': True,
                'mermaid_code': mermaid_code_for_display,
                'raw_mermaid': results.get('mermaid_code'),
                'summary': results.get('summary'),
                'stats': {
                    'text_length': results.get('text_length'),
                    'summary_length': results.get('summary_length'),
                    'mermaid_length': results.get('mermaid_length')
                }
            })
        finally:
            if os.path.exists(temp_html_path):
                try:
                    os.unlink(temp_html_path)
                except Exception:
                    pass

    except Exception as e:
        print(f"Error processing text: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
