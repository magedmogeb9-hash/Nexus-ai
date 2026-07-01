// AIForge - Main JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // Auto-hide alerts after 4s
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });

    // Confirm before delete
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', e => {
            if (!confirm(el.dataset.confirm)) e.preventDefault();
        });
    });

    // Training status polling
    const statusCards = document.querySelectorAll('[data-project-id]');
    if (statusCards.length > 0) {
        setInterval(() => {
            statusCards.forEach(card => {
                const id = card.dataset.projectId;
                fetch(`/api/project-status/${id}`)
                    .then(r => r.json())
                    .then(data => {
                        const badge = card.querySelector('.badge');
                        if (badge) {
                            badge.className = `badge badge-${data.status}`;
                            badge.textContent = data.status;
                        }
                    }).catch(() => {});
            });
        }, 5000);
    }
});
