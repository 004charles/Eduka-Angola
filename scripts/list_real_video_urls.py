from cursos_app.models import Curso

field_names = {field.name for field in Curso._meta.get_fields()}
if 'video_previa_url' in field_names:
    for curso in Curso.objects.exclude(video_previa_url__isnull=True).exclude(video_previa_url='').values('titulo', 'video_previa_url')[:20]:
        print(curso)
else:
    print('NO_VIDEO_PREVIEW_FIELD')
