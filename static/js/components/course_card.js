(function() {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function updateAllSyncIcons(cursoId, modelName, isAdded) {
        // Sync all icons for the same course on the page (e.g. if it appears in two carousels)
        const allButtons = document.querySelectorAll(`.favorite-btn[data-curso-id="${cursoId}"][data-model="${modelName}"]`);
        allButtons.forEach(btn => {
            if (isAdded) {
                btn.classList.add('favorito-ativo');
            } else {
                btn.classList.remove('favorito-ativo');
            }
        });
    }

    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.favorite-btn');
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        const cursoId = btn.getAttribute('data-curso-id');
        const modelName = btn.getAttribute('data-model');
        const isCurrentlyFavorited = btn.classList.contains('favorito-ativo');
        
        let url = '';
        let body = null;

        if (modelName === 'Curso_video') {
            url = '/curso_video/api/toggle_favorito/';
            body = JSON.stringify({ 'curso_id': cursoId });
        } else {
            url = `/cursos/favorito/${cursoId}/`;
            body = JSON.stringify({}); 
        }

        const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

        // Optimistic UI change (Sync all icons for this course instantly)
        updateAllSyncIcons(cursoId, modelName, !isCurrentlyFavorited);

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: body
        })
        .then(response => {
            if (response.status === 403) {
                throw new Error('Não autorizado ou falta Token CSRF');
            }
            if (!response.ok) throw new Error('Falha na comunicação com o servidor');
            return response.json();
        })
        .then(data => {
            // Confirm the actual status from server
            if (data.status === 'added') {
                updateAllSyncIcons(cursoId, modelName, true);
            } else if (data.status === 'removed') {
                updateAllSyncIcons(cursoId, modelName, false);
            } else {
                updateAllSyncIcons(cursoId, modelName, isCurrentlyFavorited);
                if (data.message) alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error updating favorite:', error);
            updateAllSyncIcons(cursoId, modelName, isCurrentlyFavorited);
            // alert('Erro ao processar favorito. Por favor, tente novamente.');
        });
    }, true);
})();
