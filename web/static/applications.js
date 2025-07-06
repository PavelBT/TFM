function setupJsonModal() {
    const modal = document.getElementById('json-modal');
    if (!modal) return;
    const closeBtn = document.getElementById('close-json');
    if (closeBtn) {
        closeBtn.onclick = () => { modal.style.display = 'none'; };
    }
    document.querySelectorAll('.json-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const pre = modal.querySelector('pre');
            try {
                const data = JSON.parse(btn.dataset.json);
                pre.textContent = JSON.stringify(data, null, 2);
            } catch (e) {
                pre.textContent = btn.dataset.json;
            }
            modal.style.display = 'block';
        });
    });
}

document.addEventListener('DOMContentLoaded', setupJsonModal);
