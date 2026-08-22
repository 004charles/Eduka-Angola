import { ArrowRight, MapPin, PackageCheck, Store } from "lucide-react";
import "./marketplace-shelf.css";

const formatarKz = (valor) => new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 0 }).format(Number(valor || 0)).replace(/,/g, " ") + " Kz";

export default function MarketplaceShelf({ products = [], onNavigate }) {
  if (!products.length) return null;
  const rail = [...products, ...products];
  return <section className="marketplace-shelf" aria-label="Mercado Edukangola">
    <div className="page-width marketplace-shelf-inner">
      <div className="marketplace-shelf-heading">
        <div>
          <span className="eyebrow muted"><PackageCheck size={14} /> Mercado Edukangola</span>
          <h2>Materiais para aprender melhor.</h2>
          <p>Tecnologia, livros e essenciais de estudo seleccionados em lojas parceiras de Luanda.</p>
        </div>
        <button className="marketplace-shelf-link" onClick={() => onNavigate("/mercado")}>Explorar o Mercado <ArrowRight size={16} /></button>
      </div>
      <div className="marketplace-rail-viewport">
        <div className="marketplace-rail">
          {rail.map((product, index) => <button className="marketplace-mini-product" onClick={() => onNavigate(product.detalhe_url)} key={`${product.id}-${index}`} aria-label={`Ver ${product.titulo}`}>
            <span className="marketplace-mini-image">{product.imagem_url ? <img src={product.imagem_url} alt="" /> : <PackageCheck size={25} />}</span>
            <span className="marketplace-mini-copy"><small>{product.categoria}</small><strong>{product.titulo}</strong><b>{product.preco_formatado || formatarKz(product.preco)}</b><em><Store size={11} /> {product.loja?.nome || "Loja parceira"}</em></span>
          </button>)}
        </div>
      </div>
      <div className="marketplace-shelf-footnote"><MapPin size={14} /> Entregas disponíveis em Luanda</div>
    </div>
  </section>;
}
