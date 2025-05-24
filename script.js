document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const resultsSection = document.getElementById('results');
    const downloadBtn = document.getElementById('downloadBtn');
    let compressedFileType = '.txt'; // Default to .txt
    const algorithmSelect = document.getElementById('algorithm');
    const algorithmSelectWrapper = document.getElementById('algorithmSelectWrapper');
    const qualitySelectWrapper = document.getElementById('qualitySelectWrapper');
    const qualitySelect = document.getElementById('quality');

    // Handle drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('highlight');
    }

    function unhighlight(e) {
        dropZone.classList.remove('highlight');
    }

    // Handle file drop
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Handle file selection via button
    document.querySelector('.btn-upload').addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('fileInput').click();
    });

    // Helper: Tampilkan opsi kompresi sesuai tipe file
    function updateAlgorithmOptions(file) {
        if (!file) return;
        const ext = file.name.split('.').pop().toLowerCase();
        // Reset
        algorithmSelectWrapper.style.display = 'block';
        qualitySelectWrapper.style.display = 'none';
        // Teks
        if (["txt"].includes(ext)) {
            algorithmSelect.innerHTML = `
                <option value="huffman">Huffman Coding (Teks)</option>
                <option value="rle">Run-Length Encoding (Teks)</option>
                <option value="lzw">LZW Compression (Teks)</option>
            `;
        } else if (["jpg","jpeg","png","webp"].includes(ext)) {
            algorithmSelect.innerHTML = `
                <option value="jpeg">JPEG (Gambar)</option>
                <option value="webp">WebP (Gambar)</option>
                <option value="png">PNG (Gambar)</option>
            `;
            qualitySelectWrapper.style.display = 'block';
        } else if (["pdf"].includes(ext)) {
            algorithmSelect.innerHTML = `<option value="pdf">PDF Compress</option>`;
        } else if (["docx"].includes(ext)) {
            algorithmSelect.innerHTML = `<option value="docx">DOCX Compress</option>`;
        } else if (["zip"].includes(ext)) {
            algorithmSelect.innerHTML = `<option value="zip">ZIP Compress</option>`;
        } else {
            algorithmSelect.innerHTML = `<option value="huffman">Huffman Coding (Teks)</option>`;
        }
    }

    // Update opsi saat file dipilih
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
        if (this.files && this.files[0]) {
            updateAlgorithmOptions(this.files[0]);
        }
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            updateAlgorithmOptions(file);
            const allowedTypes = [
                'text/plain',
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg',
                'image/jpg',
                'image/png',
                'image/webp',
                'application/zip',
            ];
            
            if (allowedTypes.includes(file.type)) {
                // Update UI to show selected file
                const uploadContent = dropZone.querySelector('.upload-content');
                uploadContent.innerHTML = `
                    <p>File terpilih: ${file.name}</p>
                    <p>Ukuran: ${formatFileSize(file.size)}</p>
                    <p>Format: ${file.type}</p>
                `;
            } else {
                alert('Mohon pilih file dengan format yang didukung (TXT, DOCX, PDF, JPG/JPEG).');
            }
        }
    }

    // Handle form submission
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const file = fileInput.files[0];
        if (!file) {
            alert('Mohon pilih file terlebih dahulu.');
            return;
        }
        const algorithm = algorithmSelect.value;
        let quality = 70;
        if (qualitySelectWrapper.style.display !== 'none') {
            quality = qualitySelect.value;
        }
        const formData = new FormData();
        formData.append('file', file);
        formData.append('algorithm', algorithm);
        formData.append('quality', quality);

        try {
            const response = await fetch('/compress', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                displayResults(result);
            } else {
                throw new Error('Gagal mengompresi file');
            }
        } catch (error) {
            alert('Terjadi kesalahan: ' + error.message);
        }
    });

    function displayResults(result) {
        document.getElementById('originalSize').textContent = formatFileSize(result.original_size);
        document.getElementById('compressedSize').textContent = formatFileSize(result.compressed_size);
        document.getElementById('compressionRatio').textContent = 
            `${((1 - result.compressed_size / result.original_size) * 100).toFixed(2)}%`;
        
        compressedFileType = result.file_type; // Store the file type

        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Handle download
    downloadBtn.addEventListener('click', async function() {
        try {
            const response = await fetch(`/download?ext=${compressedFileType}`); // Use stored file type
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `compressed_file${compressedFileType}`; // Use stored file type for filename
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
            } else {
                throw new Error('Gagal mengunduh file');
            }
        } catch (error) {
            alert('Terjadi kesalahan: ' + error.message);
        }
    });

    // Utility function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}); 