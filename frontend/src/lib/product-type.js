export function isVideoCurso(course) {
  return Boolean(course?.is_video);
}

export function tipoProduto(course) {
  if (isVideoCurso(course)) return "video";
  return "presencial";
}

export function etiquetaProduto(course) {
  const tipo = tipoProduto(course);
  if (tipo === "video") return "Curso em vídeo";
  return "Presencial com turma";
}

export function acaoProduto(course) {
  if (!isVideoCurso(course)) return "Ver curso e turmas";
  return course?.is_gratuito ? "Aceder gratuitamente" : "Comprar curso em vídeo";
}

export function textoRodapeProduto(course, turma) {
  if (isVideoCurso(course)) return course?.pagamento?.agora || "Acesso a confirmar";
  return turma ? `Início ${turma.inicio_formatado}` : "Turma a confirmar";
}

export function rotaDetalheProduto(course) {
  return isVideoCurso(course) ? `/video-cursos/${course.video_slug}` : `/cursos/${course.id}`;
}
