function setupJsonModal() {
    const modalEl = document.getElementById('json-modal');
    if (!modalEl) return;
    const bsModal = new bootstrap.Modal(modalEl);
    const closeBtn = document.getElementById('close-json');
    if (closeBtn) {
        closeBtn.onclick = () => { bsModal.hide(); };
    }
    document.querySelectorAll('.json-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const pre = modalEl.querySelector('pre');
            try {
                const data = JSON.parse(btn.dataset.json);
                pre.textContent = JSON.stringify(data, null, 2);
            } catch (e) {
                pre.textContent = btn.dataset.json;
            }
            bsModal.show();
        });
    });
}

document.addEventListener('DOMContentLoaded', setupJsonModal);
