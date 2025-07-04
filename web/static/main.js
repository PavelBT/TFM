async function fileToDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function prettify(key) {
    const str = key.replace(/_/g, ' ');
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function renderFields(data, prefix = '') {
    let html = `<div class="${prefix ? 'subsection' : ''}">`;
    Object.entries(data).forEach(([key, value]) => {
        const fieldName = prefix ? `${prefix}.${key}` : key;
        if (value && typeof value === 'object' && !Array.isArray(value)) {
            html += `<fieldset><legend class="section-title">${prettify(key)}</legend>`;
            html += renderFields(value, fieldName);
            html += `</fieldset>`;
        } else {
            html += `<div><label class="field-key">${prettify(key)}:` +
                ` <input type="text" name="${fieldName}" value="${value}"></label></div>`;
        }
    });
    html += '</div>';
    return html;
}

function showPreview(file) {
    const previewArea = document.getElementById('preview-area');
    previewArea.innerHTML = '';
    if (file.type === 'application/pdf') {
        const url = URL.createObjectURL(file);
        previewArea.innerHTML = `<iframe src="${url}" width="100%" height="600px"></iframe>`;
    } else {
        const reader = new FileReader();
        reader.onload = e => {
            previewArea.innerHTML = `<div id="image-container"><img id="preview-image" ` +
                `src="${e.target.result}" alt="Documento" style="max-width:100%;" /></div>`;
            setupImagePanZoom();
        };
        reader.readAsDataURL(file);
    }
}

function setupUploadForm() {
    const uploadForm = document.getElementById('upload-form');
    if (!uploadForm) return;
    uploadForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const fileInput = uploadForm.querySelector('input[name="document"]');
        if (!fileInput.files.length) return;
        const file = fileInput.files[0];

        document.getElementById('spinner').style.display = 'block';
        document.getElementById('result-container').style.display = 'flex';
        document.getElementById('save-btn').style.display = 'none';

        showPreview(file);
        const fileUrl = await fileToDataURL(file);
        window.currentFileUrl = fileUrl;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('http://localhost:8000/api/analyze', {
                method: 'POST',
                body: formData
            });
            if (!res.ok) throw new Error('API error');
            const data = await res.json();
            window.formType = data.form_type;
            document.getElementById('form-area').innerHTML = renderFields(data.fields);
            document.getElementById('spinner').style.display = 'none';
            document.getElementById('save-btn').style.display = 'block';
            setupSaveButton(window.formType, window.currentFileUrl);
        } catch (err) {
            console.error(err);
            document.getElementById('spinner').style.display = 'none';
            alert('Error al procesar el documento');
        }
    });
}

function buildPayload(form) {
    const result = {};
    const data = new FormData(form);
    for (const [key, value] of data.entries()) {
        const keys = key.split('.');
        let obj = result;
        keys.forEach((k, idx) => {
            if (idx === keys.length - 1) {
                obj[k] = value;
            } else {
                if (!obj[k]) obj[k] = {};
                obj = obj[k];
            }
        });
    }
    return result;
}

function setupSaveButton(formType, fileUrl) {
    const btn = document.getElementById('save-btn');
    if (!btn) return;
    btn.addEventListener('click', function () {
        const form = document.getElementById('edit-form');
        const payload = {
            form_type: formType,
            fields: buildPayload(form),
            file_url: fileUrl || ''
        };
        fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).then(r => r.json()).then(() => {
            alert('Datos enviados para guardar');
        });
    });
}

function setupImagePanZoom() {
    const img = document.getElementById('preview-image');
    if (!img) return;
    let scale = 1;
    let panX = 0;
    let panY = 0;
    let startX = 0;
    let startY = 0;
    let dragging = false;

    function updateTransform() {
        img.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
    }

    img.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.1 : -0.1;
        scale = Math.min(Math.max(0.5, scale + delta), 3);
        updateTransform();
    });

    img.addEventListener('mousedown', (e) => {
        dragging = true;
        startX = e.clientX - panX;
        startY = e.clientY - panY;
    });

    window.addEventListener('mousemove', (e) => {
        if (!dragging) return;
        panX = e.clientX - startX;
        panY = e.clientY - startY;
        updateTransform();
    });

    window.addEventListener('mouseup', () => {
        dragging = false;
    });
}

function init(formType, fileUrl) {
    setupUploadForm();
    if (formType && fileUrl) {
        setupSaveButton(formType, fileUrl);
        setupImagePanZoom();
        document.getElementById('result-container').style.display = 'flex';
    }
}

document.addEventListener('DOMContentLoaded', () => init(window.formType, window.fileUrl));
