from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
import heapq
from collections import Counter
import json
import tempfile
import io
from PIL import Image
import docx
import PyPDF2
import zipfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text):
    # Count frequency of each character
    freq = Counter(text)
    
    # Create priority queue
    heap = [HuffmanNode(char, freq) for char, freq in freq.items()]
    heapq.heapify(heap)
    
    # Build Huffman tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        internal = HuffmanNode(None, left.freq + right.freq)
        internal.left = left
        internal.right = right
        
        heapq.heappush(heap, internal)
    
    return heap[0]

def build_huffman_codes(root, current_code="", codes=None):
    if codes is None:
        codes = {}
    
    if root is None:
        return
    
    if root.char is not None:
        codes[root.char] = current_code if current_code else "0"
    
    build_huffman_codes(root.left, current_code + "0", codes)
    build_huffman_codes(root.right, current_code + "1", codes)
    
    return codes

def huffman_compress(text):
    if not text:
        return "", {}
    
    # Build Huffman tree and codes
    root = build_huffman_tree(text)
    codes = build_huffman_codes(root)
    
    # Encode text
    encoded = ''.join(codes[char] for char in text)
    
    # Pad encoded text to make it byte-aligned
    padding = (8 - len(encoded) % 8) % 8
    encoded += '0' * padding
    
    # Convert to bytes
    encoded_bytes = bytearray()
    for i in range(0, len(encoded), 8):
        byte = encoded[i:i+8]
        encoded_bytes.append(int(byte, 2))
    
    return bytes(encoded_bytes), codes, padding

def rle_compress(text):
    if not text:
        return ""
    
    compressed = []
    count = 1
    current = text[0]
    
    for char in text[1:]:
        if char == current:
            count += 1
        else:
            compressed.append(f"{count}{current}")
            current = char
            count = 1
    
    compressed.append(f"{count}{current}")
    return ''.join(compressed)

def lzw_compress(text):
    if not text:
        return []
    
    # Initialize dictionary with all possible characters
    dictionary = {chr(i): i for i in range(256)}
    dict_size = 256
    
    result = []
    current = ""
    
    for char in text:
        current_char = current + char
        if current_char in dictionary:
            current = current_char
        else:
            result.append(dictionary[current])
            dictionary[current_char] = dict_size
            dict_size += 1
            current = char
    
    if current:
        result.append(dictionary[current])
    
    return result

def compress_image(image_data, quality=85):
    """Compress JPEG image"""
    img = Image.open(io.BytesIO(image_data))
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    return output.getvalue()

def compress_pdf(pdf_data):
    """Compress PDF file"""
    input_pdf = io.BytesIO(pdf_data)
    output_pdf = io.BytesIO()
    
    reader = PyPDF2.PdfReader(input_pdf)
    writer = PyPDF2.PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
    
    writer.write(output_pdf)
    return output_pdf.getvalue()

def compress_docx(docx_data):
    """Compress DOCX file"""
    # DOCX is already a ZIP file, we'll recompress it
    input_docx = io.BytesIO(docx_data)
    output_docx = io.BytesIO()
    
    with zipfile.ZipFile(input_docx, 'r') as zin:
        with zipfile.ZipFile(output_docx, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                zout.writestr(item, zin.read(item.filename))
    
    return output_docx.getvalue()

def compress_jpeg(file_stream, quality=70):
    image = Image.open(file_stream)
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    return output

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    algorithm = request.form.get('algorithm', 'huffman')
    quality = int(request.form.get('quality', 70))
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = {'.txt', '.docx', '.pdf', '.jpg', '.jpeg', '.png', '.webp', '.zip'}
    if file_ext not in allowed_extensions:
        return jsonify({'error': 'File type not supported'}), 400
    
    file_data = file.read()
    original_size = len(file_data)
    
    # Kompresi sesuai pilihan user
    if file_ext == '.txt':
        content = file_data.decode('utf-8')
        if algorithm == 'huffman':
            compressed_data, codes, padding = huffman_compress(content)
            compressed_size = len(compressed_data)
            metadata = {'codes': codes, 'padding': padding}
            with open(os.path.join(app.config['UPLOAD_FOLDER'], 'compression_metadata.json'), 'w') as f:
                json.dump(metadata, f)
        elif algorithm == 'rle':
            compressed_data = rle_compress(content)
            compressed_size = len(compressed_data.encode('utf-8'))
        elif algorithm == 'lzw':
            compressed_data = lzw_compress(content)
            compressed_size = len(str(compressed_data).encode('utf-8'))
        else:
            return jsonify({'error': 'Invalid algorithm selected'}), 400
    elif file_ext in {'.jpg', '.jpeg', '.png', '.webp'}:
        img = Image.open(io.BytesIO(file_data))
        output = io.BytesIO()
        if algorithm == 'jpeg':
            img = img.convert('RGB')
            img.save(output, format='JPEG', quality=quality, optimize=True)
            out_ext = '.jpg'
        elif algorithm == 'webp':
            img.save(output, format='WEBP', quality=quality, optimize=True)
            out_ext = '.webp'
        elif algorithm == 'png':
            img.save(output, format='PNG', optimize=True)
            out_ext = '.png'
        else:
            return jsonify({'error': 'Invalid algorithm for image'}), 400
        compressed_data = output.getvalue()
        compressed_size = len(compressed_data)
        file_ext = out_ext
    elif file_ext == '.pdf':
        compressed_data = compress_pdf(file_data)
        compressed_size = len(compressed_data)
    elif file_ext == '.docx':
        compressed_data = compress_docx(file_data)
        compressed_size = len(compressed_data)
    elif file_ext == '.zip':
        try:
            input_zip = io.BytesIO(file_data)
            output_zip = io.BytesIO()
            with zipfile.ZipFile(input_zip, 'r') as zin:
                with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        zout.writestr(item, zin.read(item.filename))
            compressed_data = output_zip.getvalue()
            compressed_size = len(compressed_data)
        except Exception as e:
            return jsonify({'error': f'File ZIP tidak valid atau rusak: {str(e)}'}), 400
    else:
        return jsonify({'error': 'Unsupported file type'}), 400
    
    output_filename = 'compressed' + file_ext
    with open(os.path.join(app.config['UPLOAD_FOLDER'], output_filename), 'wb') as f:
        f.write(compressed_data)
    
    return jsonify({
        'original_size': original_size,
        'compressed_size': compressed_size,
        'file_type': file_ext
    })

@app.route('/download')
def download():
    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], 'compressed' + request.args.get('ext', '.txt')),
        as_attachment=True,
        download_name='compressed' + request.args.get('ext', '.txt')
    )

if __name__ == '__main__':
    app.run(debug=True) 