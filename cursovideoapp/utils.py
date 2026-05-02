import re
import requests
from django.conf import settings

def get_youtube_video_id(url):
    """
    Extrai o ID do vídeo de um URL do YouTube.
    Suporta formatos: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID, etc.
    """
    if not url:
        return None
    
    regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_youtube_playlist_id(url):
    """
    Extrai o ID da playlist de um URL do YouTube.
    """
    if not url:
        return None
    match = re.search(r"[&?]list=([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None

def parse_youtube_duration(duration_str):
    """
    Converte uma duração ISO 8601 (ex: PT5M30S) em segundos.
    """
    if not duration_str:
        return 0
    
    # Regex para capturar Horas, Minutos e Segundos
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration_str)
    
    if not match:
        return 0
        
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return (hours * 3600) + (minutes * 60) + seconds

def fetch_youtube_metadata(url):
    """
    Consulta a API do YouTube para obter o título e a duração do vídeo.
    """
    video_id = get_youtube_video_id(url)
    if not video_id:
        return None
        
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if not api_key:
        return None
        
    api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet,contentDetails"
    
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                item = data['items'][0]
                snippet = item.get('snippet', {})
                content_details = item.get('contentDetails', {})
                
                return {
                    'titulo': snippet.get('title'),
                    'descricao': snippet.get('description'),
                    'duracao_segundos': parse_youtube_duration(content_details.get('duration')),
                    'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url')
                }
    except Exception as e:
        print(f"Erro ao consultar API do YouTube: {e}")
        
    return None

def fetch_playlist_videos(playlist_url):
    """
    Retorna uma lista de metadados de todos os vídeos de uma playlist.
    """
    playlist_id = get_youtube_playlist_id(playlist_url)
    if not playlist_id:
        return []
        
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    videos = []
    next_page_token = None
    
    while True:
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&maxResults=50&playlistId={playlist_id}&key={api_key}"
        if next_page_token:
            url += f"&pageToken={next_page_token}"
            
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"Erro YouTube API (Status {response.status_code}): {response.text}")
                break
                
            data = response.json()
            items = data.get('items', [])
            
            # Para cada item, precisamos buscar a duração separadamente (playlistItems não traz duração total)
            # Ou podemos fazer um batch request para 'videos' com os IDs coletados
            video_ids = [item['contentDetails']['videoId'] for item in items]
            
            # Busca metadados detalhados (duração) para este lote de 50 vídeos
            details_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails,snippet&id={','.join(video_ids)}&key={api_key}"
            details_res = requests.get(details_url, timeout=10)
            details_data = details_res.json()
            
            details_map = {v['id']: v for v in details_data.get('items', [])}
            
            for item in items:
                v_id = item['contentDetails']['videoId']
                d = details_map.get(v_id, {})
                
                videos.append({
                    'titulo': item['snippet']['title'],
                    'video_url': f"https://www.youtube.com/watch?v={v_id}",
                    'duracao_segundos': parse_youtube_duration(d.get('contentDetails', {}).get('duration')),
                    'ordem': item['snippet']['position'] + 1
                })
                
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
        except Exception as e:
            print(f"Erro ao buscar playlist: {e}")
            break
            
    return videos
