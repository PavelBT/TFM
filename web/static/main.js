function setupUploadForm() {
    const uploadForm = document.getElementById('upload-form');
    if (!uploadForm) return;
    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();
        document.getElementById('spinner').style.display = 'block';
        const form = e.target;
        setTimeout(function () {
            form.submit();
        }, 10);
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
    setupSaveButton(formType, fileUrl);
    setupImagePanZoom();
}

document.addEventListener('DOMContentLoaded', () => init(window.formType, window.fileUrl));
