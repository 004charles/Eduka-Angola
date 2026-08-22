# Ajuste de interface pública — subscrição de vídeo

Foi verificada a referência visual enviada em 21/08/2026. A interface pública mostrava a mensagem: “Não existe um plano disponível neste momento. A administração pode configurá-lo no Django Admin.”

Esta referência expõe um detalhe técnico interno e não deve aparecer para alunos ou visitantes. Quando não houver um plano activo, a interface deve informar apenas que as subscrições estarão disponíveis em breve e oferecer um caminho de retorno ao catálogo.

Também foi registada a necessidade de manter a faixa de produtos da página inicial dentro do mesmo contentor, largura e ritmo visual das restantes secções da Edukangola.

Na pré-visualização local, a secção Mercado Edukangola foi localizada na página inicial após as prateleiras de cursos. A validação final deve confirmar que a faixa animada permanece confinada ao contentor visual da página, sem ocupar a largura total do ecrã.

A medição no navegador confirmou o alinhamento: em um ecrã de 1280 px, o contentor Mercado Edukangola tem 1180 px e começa em 43 px, exactamente como o contentor padrão da página. A faixa de produtos deixou, portanto, de ocupar toda a largura do ecrã.
