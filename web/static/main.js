async function fileToDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function showAlert(message, success = true) {
    return new Promise(resolve => {
        const box = document.getElementById('alert-container');
        if (!box) return resolve();
        box.textContent = message;
        box.className = success ? 'alert alert-success' : 'alert alert-error';
        box.style.display = 'block';
        setTimeout(() => {
            box.style.display = 'none';
            resolve();
        }, 3000);
    });
}

function prettify(key) {
    const str = key.replace(/_/g, ' ');
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function maybeParseJSON(value) {
    if (typeof value !== 'string') return value;
    const trimmed = value.trim();
    if ((trimmed.startsWith('{') && trimmed.endsWith('}')) ||
        (trimmed.startsWith('[') && trimmed.endsWith(']')))
    {
        try {
            return JSON.parse(trimmed);
        } catch (_) {
            return value;
        }
    }
    return value;
}

function renderFields(data, prefix = '') {
    let html = `<div class="${prefix ? 'subsection' : ''}">`;
    Object.entries(data).forEach(([key, value]) => {
        const fieldName = prefix ? `${prefix}.${key}` : key;
        value = maybeParseJSON(value);
        if (value && typeof value === 'object' && !Array.isArray(value)) {
            html += `<fieldset><legend class="section-title">${prettify(key)}</legend>`;
            html += renderFields(value, fieldName);
            html += `</fieldset>`;
        } else if (Array.isArray(value)) {
            html += `<fieldset><legend class="section-title">${prettify(key)}</legend>`;
            value.forEach((item, idx) => {
                const itemName = `${fieldName}[${idx}]`;
                if (item && typeof item === 'object') {
                    html += `<fieldset><legend class="section-title">${prettify(key)} ${idx + 1}</legend>`;
                    html += renderFields(item, itemName);
                    html += `</fieldset>`;
                } else {
                    html += `<div><label class="field-key">${prettify(key)} ${idx + 1}:` +
                        ` <input type="text" name="${itemName}" value="${item}"></label></div>`;
                }
            });
            html += `</fieldset>`;
        } else {
            html += `<div><label class="field-key">${prettify(key)}:` +
                ` <input type="text" name="${fieldName}" value="${value}"></label></div>`;
        }
    });
    html += '</div>';
    return html;
}

function resetResult(clearFileInput = true) {
    document.getElementById('preview-area').innerHTML = '';
    document.getElementById('form-area').innerHTML = '';
    const controls = document.getElementById('zoom-pan-controls');
    if (controls) controls.style.display = 'none';
    document.getElementById('save-btn').style.display = 'none';
    document.getElementById('edit-form').style.display = 'none';
    const resultContainer = document.getElementById('result-container');
    if (resultContainer) resultContainer.style.display = 'none';
    const fileInput = document.querySelector('#upload-form input[name="document"]');
    if (fileInput && clearFileInput) fileInput.value = '';
    window.formType = null;
    window.currentFileUrl = null;
}

function showPreview(file) {
    const previewArea = document.getElementById('preview-area');
    previewArea.innerHTML = '';
    const controls = document.getElementById('zoom-pan-controls');
    if (file.type === 'application/pdf') {
        const url = URL.createObjectURL(file);
        previewArea.innerHTML = `<iframe src="${url}" width="100%" height="600px"></iframe>`;
        if (controls) controls.style.display = 'none';
    } else {
        const reader = new FileReader();
        reader.onload = e => {
            previewArea.innerHTML = `<div id="image-container"><img id="preview-image" ` +
                `src="${e.target.result}" alt="Documento" style="max-width:100%;" /></div>`;
            if (controls) controls.style.display = 'block';
            setupImagePanZoom();
        };
        reader.readAsDataURL(file);
    }
}

function setupUploadForm() {
    const uploadForm = document.getElementById('upload-form');
    if (!uploadForm) return;
    const fileInput = uploadForm.querySelector('input[name="document"]');
    // Temporary controls for OCR comparison
    const refinerCheckbox = uploadForm.querySelector('#use-refiner');
    const ocrRadios = uploadForm.querySelectorAll('input[name="ocr_service"]');

    function updateRefinerState() {
        const selected = uploadForm.querySelector('input[name="ocr_service"]:checked');
        if (selected && selected.value === 'gemini') {
            if (refinerCheckbox) {
                refinerCheckbox.checked = true;
                refinerCheckbox.disabled = true;
            }
        } else if (refinerCheckbox) {
            refinerCheckbox.disabled = false;
        }
    }

    ocrRadios.forEach(r => r.addEventListener('change', updateRefinerState));
    updateRefinerState();
    fileInput.addEventListener('change', () => {
        if (!fileInput.files.length) return;
        const file = fileInput.files[0];
        // Keep the selected file in the input when resetting previous results
        resetResult(false);
        document.getElementById('result-container').style.display = 'flex';
        showPreview(file);
    });
    uploadForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        if (!fileInput.files.length) return;
        const file = fileInput.files[0];

        document.getElementById('spinner').style.display = 'block';
        document.getElementById('result-container').style.display = 'flex';
        document.getElementById('save-btn').style.display = 'none';
        document.querySelector('.form-section').classList.add('loading');

        showPreview(file);
        const fileUrl = await fileToDataURL(file);
        window.currentFileUrl = fileUrl;

        const formData = new FormData();
        formData.append('file', file);
        const selected = uploadForm.querySelector('input[name="ocr_service"]:checked');
        if (selected) formData.append('ocr_service', selected.value);
        if (refinerCheckbox) {
            formData.append('use_refiner', refinerCheckbox.checked ? 'true' : 'false');
        }

        try {
        const res = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });
            if (!res.ok) throw new Error('API error');
            const data = await res.json();
            window.formType = data.form_type;
            document.getElementById('form-area').innerHTML = renderFields(data.fields);
            document.getElementById('edit-form').style.display = 'block';
            document.getElementById('spinner').style.display = 'none';
            document.getElementById('save-btn').style.display = 'block';
            document.querySelector('.form-section').classList.remove('loading');
            setupSaveButton(window.formType, window.currentFileUrl);
        } catch (err) {
            console.error(err);
            document.getElementById('spinner').style.display = 'none';
            document.querySelector('.form-section').classList.remove('loading');
            alert('Error al procesar el documento');
        }
    });
}

function parsePath(key) {
    return key
        .replace(/\[(\d+)\]/g, ".$1")
        .split('.')
        .map(k => (k.match(/^\d+$/) ? Number(k) : k));
}

function buildPayload(form) {
    const result = {};
    const data = new FormData(form);
    for (const [key, value] of data.entries()) {
        const path = parsePath(key);
        let obj = result;
        for (let i = 0; i < path.length; i++) {
            const part = path[i];
            const isLast = i === path.length - 1;
            if (isLast) {
                obj[part] = value;
            } else {
                const nextPart = path[i + 1];
                if (typeof nextPart === 'number') {
                    if (!Array.isArray(obj[part])) obj[part] = [];
                } else {
                    if (!obj[part]) obj[part] = {};
                }
                obj = obj[part];
            }
        }
    }
    return result;
}

function setupSaveButton(formType, fileUrl) {
    const btn = document.getElementById('save-btn');
    if (!btn) return;
    btn.onclick = function () {
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
        })
            .then(res => res.json().then(data => ({ ok: res.ok, data })))
            .then(({ ok, data }) => {
                if (ok && data.status === 'ok') {
                    showAlert(data.message || 'Registro guardado', true)
                        .then(() => setTimeout(resetResult, 1000));
                } else {
                    throw new Error(data.message || 'Error al guardar');
                }
            })
            .catch(err => {
                console.error(err);
                showAlert(err.message || 'Error al guardar', false);
            });
    };
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

    const controls = document.getElementById('zoom-pan-controls');
    if (controls) {
        controls.style.display = 'block';
        controls.querySelector('#zoom-in').onclick = () => { scale = Math.min(scale + 0.1, 3); updateTransform(); };
        controls.querySelector('#zoom-out').onclick = () => { scale = Math.max(scale - 0.1, 0.5); updateTransform(); };
        controls.querySelector('#pan-left').onclick = () => { panX -= 20; updateTransform(); };
        controls.querySelector('#pan-right').onclick = () => { panX += 20; updateTransform(); };
        controls.querySelector('#pan-up').onclick = () => { panY -= 20; updateTransform(); };
        controls.querySelector('#pan-down').onclick = () => { panY += 20; updateTransform(); };
        controls.querySelector('#reset-pan-zoom').onclick = () => { scale = 1; panX = 0; panY = 0; updateTransform(); };
    }
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
