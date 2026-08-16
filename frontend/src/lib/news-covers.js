function browserSafeImageUrl(url) {
  if (!url) return null;
  try {
    const parsed = new URL(url, window.location.origin);
    return parsed.origin === window.location.origin ? parsed.href : `${parsed.pathname}${parsed.search}`;
  } catch {
    return url;
  }
}

export function newsCover(post = {}) {
  const uploadedCover = browserSafeImageUrl(post.imagem_capa);
  if (uploadedCover) return uploadedCover;
  const category = String(post.categoria?.slug || post.categoria?.nome || "").toLowerCase();
  if (post.tipo_conteudo === "video") {
    const covers = ["/news/video-1.jpg", "/news/video-2.jpg", "/news/video-3.jpg"];
    return covers[Number(post.id || 0) % covers.length];
  }
  if (category.includes("tecn")) return "/news/technology.jpg";
  if (category.includes("carreira")) return "/news/career.png";
  if (category.includes("comun")) return "/news/community.png";
  return "/news/education.jpg";
}
