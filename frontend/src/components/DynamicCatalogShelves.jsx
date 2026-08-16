import CourseShelf from "./CourseShelf";
import { backendUrl } from "../lib/backend-url";
import { etiquetaProduto, isVideoCurso, rotaDetalheProduto, textoRodapeProduto, tipoProduto } from "../lib/product-type";
import "./dynamic-catalog-shelves.css";

function normalizar(texto) {
  return (texto || "").toLocaleLowerCase("pt-PT").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function formatarMarca(texto) {
  return texto?.replace(/Eduka-Angola/gi, "Edukangola") ?? "";
}

function criarCartao(curso, proximaTurma) {
  return {
    ...curso,
    id: curso.id,
    category: curso.categoria,
    title: curso.titulo,
    centre: formatarMarca(curso.centro),
    productType: tipoProduto(curso),
    productLabel: etiquetaProduto(curso),
    mode: curso.modalidade,
    schedule: textoRodapeProduto(curso, proximaTurma),
    imageUrl: curso.imagem_url,
    detailUrl: rotaDetalheProduto(curso),
    inscricaoUrl: backendUrl(curso.inscricao_url),
    turma: proximaTurma,
  };
}

function construirColecoes(data, incluirCatalogo = true) {
  const turmasPorCurso = new Map();
  (data?.turmas_abertas || []).forEach((turma) => {
    const atual = turmasPorCurso.get(turma.id);
    if (!atual || turma.inicio < atual.inicio) turmasPorCurso.set(turma.id, turma);
  });

  const cartoes = (data?.cursos || []).map((curso) => criarCartao(curso, isVideoCurso(curso) ? null : turmasPorCurso.get(curso.id)));
  const formacoes = cartoes.filter((curso) => curso.productType !== "video");
  const videos = cartoes.filter((curso) => curso.productType === "video");
  const colecoes = [];

  const adicionarColecao = (colecao) => {
    if (colecao.courses.length > 1) colecoes.push({ ...colecao, courses: colecao.courses.slice(0, 10) });
  };

  if (incluirCatalogo && formacoes.length) {
    colecoes.push({
      id: "catalogo",
      eyebrow: "Catálogo real",
      title: "Formações com turma para explorar agora.",
      description: "Cursos presenciais, online e híbridos publicados por centros, com informação de turma, horários e vagas.",
      courses: formacoes,
      featured: true,
      autoAdvance: cartoes.length > 1,
    });
  }

  adicionarColecao({ id: "video-cursos", eyebrow: "Cursos em vídeo", title: "Aprenda ao seu ritmo, com compra única.", description: "Cursos em vídeo com aulas gravadas e acesso após compra ou acesso gratuito. Turmas só aparecem quando um centro disponibiliza acompanhamento.", courses: videos, featured: true, autoAdvance: videos.length > 1 });

  const porCategoria = formacoes.reduce((grupos, cartao) => {
    const chave = cartao.category || "Outras formações";
    grupos[chave] = [...(grupos[chave] || []), cartao];
    return grupos;
  }, {});

  adicionarColecao({
    id: "destaques",
    eyebrow: "Em destaque",
    title: "Cursos recomendados para explorar agora.",
    description: "Formações que os centros assinalaram como destaque no catálogo público.",
    courses: formacoes.filter((curso) => curso.destaque),
    featured: true,
    autoAdvance: true,
  });

  adicionarColecao({
    id: "novos-cursos",
    eyebrow: "Novas formações",
    title: "Recém-publicados na Edukangola.",
    description: "Cursos adicionados mais recentemente pelos centros de formação.",
    courses: [...formacoes].sort((a, b) => new Date(b.data_publicacao) - new Date(a.data_publicacao)),
  });

  adicionarColecao({
    id: "proximas-turmas",
    eyebrow: "Comece em breve",
    title: "Turmas que começam nos próximos dias.",
    description: "Explore vagas, horários e condições antes de avançar para a inscrição.",
    courses: [...formacoes].filter((curso) => curso.turma).sort((a, b) => a.turma.inicio.localeCompare(b.turma.inicio)),
  });

  Object.entries(porCategoria)
    .filter(([, cursos]) => cursos.length > 1)
    .sort(([categoriaA], [categoriaB]) => categoriaA.localeCompare(categoriaB, "pt-PT"))
    .forEach(([categoria, cursos]) => {
      adicionarColecao({
        id: `categoria-${normalizar(categoria).replace(/\s+/g, "-")}`,
        eyebrow: categoria,
        title: `Formações em ${categoria}.`,
        description: `Cursos publicados atualmente na área de ${categoria}.`,
        courses: cursos,
      });
    });

  adicionarColecao({
    id: "inscricao-gratuita",
    eyebrow: "Inscrição gratuita",
    title: "Comece sem pagamento no ato.",
    description: "Cursos que permitem avançar com inscrição gratuita ou pagamento posterior ao centro.",
    courses: formacoes.filter((curso) => curso.is_gratuito || (curso.pagamento?.valor_inicial || 0) === 0),
  });

  return { cartoes, colecoes };
}

export default function DynamicCatalogShelves({ data, loading, query, onAnnounce, collectionHref, limitCollections, includeCatalog = true }) {
  const { cartoes, colecoes } = construirColecoes(data, includeCatalog);
  const consulta = normalizar(query);
  const resultados = consulta
    ? cartoes.filter((curso) => normalizar(`${curso.title} ${curso.category} ${curso.centre} ${curso.mode}`).includes(consulta))
    : null;

  if (loading) {
    return <section id="catalogo" className="page-width catalog-state"><span className="eyebrow muted">Catálogo</span><h2>A carregar cursos publicados.</h2><p>Estamos a preparar as formações disponíveis no portal.</p></section>;
  }

  if (resultados) {
    if (!resultados.length) {
      return <section id="catalogo" className="page-width catalog-state"><span className="eyebrow muted">Pesquisa no catálogo</span><h2>Nenhum curso encontrado.</h2><p>Não existem cursos publicados que correspondam a “{query}”. Tente outra área ou termo de pesquisa.</p></section>;
    }
    return <CourseShelf id="catalogo" eyebrow="Pesquisa no catálogo" title={`Resultados para “${query}”.`} description={`${resultados.length} ${resultados.length === 1 ? "curso encontrado" : "cursos encontrados"} no catálogo público.`} courses={resultados} featured onAnnounce={onAnnounce} collectionHref={collectionHref} />;
  }

  if (!colecoes.length) {
    return <section id="catalogo" className="page-width catalog-state"><span className="eyebrow muted">Catálogo real</span><h2>Não existem cursos publicados neste momento.</h2><p>Quando um centro publicar um curso, ele aparecerá automaticamente nesta área.</p></section>;
  }

  return <>{colecoes.slice(0, limitCollections).map((colecao) => <CourseShelf key={colecao.id} {...colecao} onAnnounce={onAnnounce} collectionHref={collectionHref} />)}</>;
}
