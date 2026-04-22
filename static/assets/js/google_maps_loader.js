/**
 * Google Maps Async Loader - EdukaAngola
 * Este script garante que o SDK do Google Maps seja carregado apenas uma vez e de forma assíncrona.
 */

window.EdukaMaps = (function() {
    let googleMapsPromise = null;

    /**
     * Carrega o SDK do Google Maps
     * @param {string} apiKey - Chave da API (injetada via context processor)
     * @param {string[]} libraries - Lista de bibliotecas (padrao: ['places'])
     * @returns {Promise}
     */
    function load(apiKey, libraries = ['places']) {
        if (typeof google !== 'undefined' && google.maps) {
            return Promise.resolve(google.maps);
        }

        if (googleMapsPromise) {
            return googleMapsPromise;
        }

        googleMapsPromise = new Promise((resolve, reject) => {
            const callbackName = `initGoogleMaps_${Math.random().toString(36).substr(2, 9)}`;
            
            window[callbackName] = () => {
                delete window[callbackName];
                resolve(google.maps);
            };

            const script = document.createElement('script');
            const libs = libraries.join(',');
            script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=${libs}&callback=${callbackName}`;
            script.async = true;
            script.defer = true;
            script.onerror = () => {
                googleMapsPromise = null;
                reject(new Error('Erro ao carregar o SDK do Google Maps. Verifique a ligação ou a chave da API.'));
            };
            
            document.head.appendChild(script);
        });

        return googleMapsPromise;
    }

    return {
        load: load
    };
})();
