/**
 * EdukaAngola - Home Global Map Initializer
 * Gere a visualização de todos os centros e filiais no mapa da página inicial.
 */

document.addEventListener('DOMContentLoaded', function() {
    const mapElement = document.getElementById('home-global-map');
    const recenterBtn = document.getElementById('btn-recenter');
    const apiKey = window.GOOGLE_MAPS_API_KEY || ""; // Assumindo que o context processor injeta isto

    if (!mapElement || !window.EdukaMaps) return;

    // Estilo Silver Premium para o mapa
    const silverStyle = [
        { "elementType": "geometry", "stylers": [{ "color": "#f5f5f5" }] },
        { "elementType": "labels.icon", "stylers": [{ "visibility": "off" }] },
        { "elementType": "labels.text.fill", "stylers": [{ "color": "#616161" }] },
        { "elementType": "labels.text.stroke", "stylers": [{ "color": "#f5f5f5" }] },
        { "featureType": "poi", "elementType": "geometry", "stylers": [{ "color": "#eeeeee" }] },
        { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#ffffff" }] },
        { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#c9c9c9" }] }
    ];

    window.EdukaMaps.load(apiKey).then(maps => {
        // Coordenadas padrão (Luanda)
        const defaultCenter = { lat: -8.839988, lng: 13.289437 };
        
        const map = new maps.Map(mapElement, {
            zoom: 4,
            center: defaultCenter,
            styles: silverStyle,
            disableDefaultUI: false,
            zoomControl: true,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: true
        });

        const infoWindow = new maps.InfoWindow();
        let markers = [];

        // Carregar dados da API
        fetch('/cursos/api/mapa-global/')
            .then(response => response.json())
            .then(data => {
                const pontos = data.pontos;
                
                pontos.forEach(ponto => {
                    const marker = new maps.Marker({
                        position: { lat: ponto.lat, lng: ponto.lng },
                        map: map,
                        title: ponto.nome,
                        icon: {
                            url: ponto.tipo === 'CENTRO' ? '/static/assets/images/icons/marker-primary.png' : '/static/assets/images/icons/marker-secondary.png',
                            scaledSize: new maps.Size(32, 32),
                            origin: new maps.Point(0, 0),
                            anchor: new maps.Point(16, 32)
                        }
                    });

                    // Caso os ícones personalizados não existam ainda, usar o padrão com cor
                    if (!ponto.has_custom_icon) {
                        marker.setIcon(null); // Volta ao padrão se necessário
                    }

                    marker.addListener('click', () => {
                        const content = `
                            <div class="map-info-card" style="padding: 10px; max-width: 200px; font-family: 'Inter', sans-serif;">
                                <img src="${ponto.imagem}" style="width: 100%; height: 100px; object-fit: cover; border-radius: 8px; mb-2;">
                                <h6 style="margin: 10px 0 5px; font-weight: 800; color: #1f1f1f;">${ponto.nome}</h6>
                                <p style="font-size: 12px; color: #666; margin-bottom: 10px;">
                                    <i class="feather-map-pin"></i> ${ponto.cidade} <br>
                                    <span class="badge bg-primary-opacity" style="font-size: 10px; padding: 2px 6px; border-radius: 10px; margin-top: 5px; display: inline-block;">
                                        ${ponto.total_cursos} cursos ativos
                                    </span>
                                </p>
                                <a href="${ponto.url}" class="rbt-btn btn-sm btn-gradient w-100 text-center" style="font-size: 11px; padding: 6px 10px; display: block; text-decoration: none; color: white; border-radius: 4px;">
                                    Ver Perfil Completo
                                </a>
                            </div>
                        `;
                        infoWindow.setContent(content);
                        infoWindow.open(map, marker);
                    });

                    markers.push(marker);
                });

                // Auto-localização do utilizador
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            const userPos = {
                                lat: position.coords.latitude,
                                lng: position.coords.longitude
                            };
                            map.setCenter(userPos);
                            map.setZoom(10);
                        },
                        () => {
                            console.log("Geolocalização negada ou falhou.");
                        }
                    );
                }
            });

        // Botão de Recentrar/Minha Localização
        if (recenterBtn) {
            recenterBtn.addEventListener('click', () => {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition((position) => {
                        const userPos = {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude
                        };
                        map.panTo(userPos);
                        map.setZoom(13);
                    });
                }
            });
        }
    }).catch(err => console.error("Erro ao carregar EdukaMaps na Home:", err));
});
