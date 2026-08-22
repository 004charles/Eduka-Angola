# Ajuste de interface pública — subscrição de vídeo

Foi verificada a referência visual enviada em 21/08/2026. A interface pública mostrava a mensagem: “Não existe um plano disponível neste momento. A administração pode configurá-lo no Django Admin.”

Esta referência expõe um detalhe técnico interno e não deve aparecer para alunos ou visitantes. Quando não houver um plano activo, a interface deve informar apenas que as subscrições estarão disponíveis em breve e oferecer um caminho de retorno ao catálogo.

Também foi registada a necessidade de manter a faixa de produtos da página inicial dentro do mesmo contentor, largura e ritmo visual das restantes secções da Edukangola.

Na pré-visualização local, a secção Mercado Edukangola foi localizada na página inicial após as prateleiras de cursos. A validação final deve confirmar que a faixa animada permanece confinada ao contentor visual da página, sem ocupar a largura total do ecrã.

A medição no navegador confirmou o alinhamento: em um ecrã de 1280 px, o contentor Mercado Edukangola tem 1180 px e começa em 43 px, exactamente como o contentor padrão da página. A faixa de produtos deixou, portanto, de ocupar toda a largura do ecrã.

Na referência dos cartões de cursos, os valores actualmente surgem como “Inscrição”, “Preço total” e uma linha textual de pagamento. O ajuste solicitado é tornar a mensalidade explícita quando existir, no formato “valor Kz/mês”. Também foi observado que, em cartões de título mais longo, o ícone de guardar no rodapé fica visualmente separado e parcialmente cortado; o rodapé deve permanecer alinhado na base de todos os cartões.

Na pré-visualização local após o ajuste, os cartões do catálogo exibiram o rodapé completo com o ícone de guardar visível e alinhado à direita. Os cartões presentes não tinham mensalidade configurada, por isso continuaram a mostrar “Inscrição: Sem taxa” e “Preço total: 0 Kz”; o formato “Kz/mês” está reservado aos cursos que tiverem mensalidade definida.

A medição directa confirmou que os cartões do catálogo usam uma margem inferior consistente de 12 px para o botão de guardar. Dois cartões de outra prateleira usam uma composição distinta e serão mantidos fora desta medição; a interface visível do catálogo, alvo do ajuste, mantém o botão totalmente dentro do rodapé.

A captura do separador confirmou que o navegador apresentava o ícone genérico de página. O símbolo oficial da Edukangola já existe em `eduka-mark.png`, e o ícone PWA de 192 px usa o mesmo símbolo sobre fundo escuro. A correcção deve acrescentar explicitamente o favicon ao documento público e usar a versão com boa legibilidade para separadores claros e escuros.

Depois da correcção, o documento carregado declara explicitamente os ícones `icon` e `shortcut icon`, ambos apontando para o símbolo oficial de 192 px com versão de cache. O manifesto PWA já utilizava o mesmo conjunto de ícones, portanto as instalações existentes ficam coerentes com o separador do navegador.
