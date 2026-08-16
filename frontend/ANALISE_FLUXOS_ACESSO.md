# Análise dos fluxos de acesso e matrícula

## Estado atual confirmado

O backend Django permite iniciar uma inscrição presencial sem sessão. O visitante escolhe a turma e fornece nome, e-mail e telefone; o sistema cria ou reutiliza um perfil de aluno associado ao e-mail. Se existir valor a pagar no ato, é criada uma inscrição pendente e o visitante é encaminhado para o checkout Prontu. Se o valor a pagar for zero, a vaga é confirmada automaticamente.

O vídeo-curso segue uma regra diferente: o endpoint de compra atual exige uma sessão de aluno antes de criar o pagamento ou liberar o acesso gratuito. A confirmação de pagamentos ocorre na camada `PaymentService`, que ativa a inscrição presencial ou adiciona o aluno ao vídeo-curso após receber a confirmação do gateway.

## Interface observada

A tela de login já contém e-mail, palavra-passe, recuperação de palavra-passe e ligação para criar conta. Contudo, mostra opções Google e SMS sem integração correspondente e o rótulo "E-mail ou telemóvel" não corresponde à validação atual, que autentica pelo e-mail. O cadastro solicita apenas nome, e-mail, palavra-passe e confirmação, depois exige verificação do e-mail por código antes de ativar a conta.

A revisão visual confirmou que ambas as telas têm uma base limpa e concentrada, mas ainda usam azul como cor predominante e grafias antigas de marca. A página de login não explica quando o aluno deve entrar em vez de avançar como visitante; a de cadastro não informa que haverá uma verificação por e-mail nem que a conta poderá ser usada para acompanhar compras e inscrições. Os botões Google e SMS são apresentados como ações disponíveis, mas não têm integração funcional.

> A inscrição presencial é publicada sob o prefixo `/cursos/`; por isso, a rota correta é `/cursos/ficha_inscricao/<curso_id>/`. Uma tentativa sem esse prefixo devolve 404 e não representa falha do fluxo do aluno no frontend React, que já utiliza a URL reversa gerada pelo backend.

## Direção de simplificação

O percurso recomendado deverá preservar a inscrição direta de visitante para cursos presenciais e apresentar o cadastro como opcional depois da confirmação. Para vídeo-cursos, a compra deve permitir recolher somente os dados indispensáveis, criar uma conta temporária ou ativar uma conta existente e conduzir o aluno diretamente ao pagamento. Em ambos os casos, o ecrã posterior à ação deve explicar em linguagem simples: o que foi reservado ou comprado, quanto é pago agora, o que acontece depois e como voltar ao curso.

## Confirmação presencial observada

A ficha atual já reúne a turma, os dados essenciais do visitante e o resumo de cobrança numa única página, o que é uma boa base. Contudo, ela apresenta uma navegação completa do portal, indicadores de três passos e uma grande quantidade de informação simultânea. Também mostra valores monetários com casas decimais técnicas, como `21600.00000 Kz`, em vez de uma apresentação clara em kwanzas.

O botão principal diz apenas "Confirmar e Avançar". Antes de o aluno o acionar, a interface deveria afirmar de forma direta que a vaga ficará reservada, o valor que será levado ao pagamento seguro e o que acontece se o pagamento não for concluído. A escolha de turma também deve continuar visível no resumo depois de selecionada, junto ao horário, local e vagas.

## Validação das novas telas React

A compilação inicial das novas rotas React terminou sem erros e o backend reconhece os novos contratos JSON. Durante a primeira abertura de `/entrar`, a página ficou em branco. A investigação identificou a ausência da importação explícita de `useState` no novo componente de autenticação; a importação foi adicionada e a rota será validada novamente no navegador antes de concluir a alteração.

Após a correção, as rotas React `/entrar` e `/criar-conta` renderizaram corretamente em desktop, reutilizando a navegação, tipografia, paleta roxa, fundo claro e rodapé do portal público. O login mostra apenas ações reais — e-mail, palavra-passe, recuperação e criação de conta — e o cadastro explica que será enviado um código para confirmar o e-mail. Os dois ecrãs mantêm o suporte ao modo escuro da aplicação por meio dos mesmos tokens visuais globais.

Na primeira abertura de `/inscrever/21`, o navegador apresentou uma tela em branco. A renderização do checkout deve ser diagnosticada antes de considerar esta etapa concluída; os contratos Django e a compilação de produção já foram aceites pelo verificador, portanto a investigação concentra-se no carregamento do servidor de desenvolvimento ou numa referência da página React.

A causa foi a ausência das importações de estado no componente de checkout React. Depois da correção, os checkouts de inscrição presencial e de vídeo-curso renderizaram corretamente. A inscrição presencial apresenta turma, vagas, campos de nome/e-mail/WhatsApp e um resumo de `21 600 Kz`; o vídeo-curso pede apenas nome e e-mail, mostra o preço de `15 000 Kz` e explica que as aulas serão desbloqueadas depois do pagamento. Em ambos os percursos, o aluno vê o preço antes de avançar e não encontra uma exigência de login prévio.

## Validação final

Foram executados com sucesso cinco testes automatizados: login React, cadastro React, confirmação de e-mail, inscrição presencial de visitante e acesso gratuito de visitante a vídeo-curso. O `manage.py check` não reportou problemas e a compilação do Vite foi concluída com sucesso. O aviso de dimensão do bundle permanece apenas como recomendação de otimização futura; não impede a execução dos percursos implementados.

## Refinamento de composição

As telas de entrada e cadastro foram reorganizadas numa composição centrada: mensagem curta no topo, benefícios compactos e cartão de formulário no centro da página. A validação visual confirmou que a tela de entrada preserva contraste, foco no formulário e ligação de retorno ao catálogo. A nova animação usa uma transição breve de opacidade e deslocamento vertical no conteúdo, com elementos de fundo lentos e discretos; ela é desativada para utilizadores que indicarem preferência por movimento reduzido.

Ao selecionar **Criar conta** a partir do cartão de entrada, o formulário atual executa uma saída curta e o cadastro entra no mesmo cartão centralizado. A rota é atualizada apenas depois dos 180 ms de saída, evitando uma mudança visual abrupta. A mesma regra é aplicada às ligações internas de autenticação, incluindo voltar a entrar, recuperar palavra-passe e voltar ao cadastro.

As páginas de autenticação deixaram de renderizar o rodapé público e a composição desktop foi compactada de forma controlada. Depois de ajustar a altura disponível à barra superior, a verificação do navegador confirmou `0` pixels abaixo do viewport na tela de login, sem barra de rolagem vertical. Em ecrãs móveis ou mais baixos, a página continua a poder crescer para preservar campos e ações acessíveis.

## Correção de cadastro pelo React

O erro genérico apresentado no cadastro era causado pela proteção CSRF do Django: a origem temporária usada pelo frontend React não constava das origens confiáveis e o backend devolvia uma página HTML de erro `403` em vez de JSON. Foi adicionada a origem segura `https://*.manus.computer` à configuração CSRF, além das origens locais de desenvolvimento. A validação real, feita pelo proxy no navegador, voltou `200` com `{"ok": true, "requires_verification": true}`. Também foi incluído um teste automatizado que verifica essa origem e o token CSRF, evitando regressão.

## Login editorial com formações em destaque

A tela de entrada foi redesenhada como uma composição de dois painéis: à esquerda, uma formação publicada em destaque; à direita, o formulário de acesso simples. A validação visual confirmou que o painel usa dados reais do catálogo, incluindo imagem, tipo de produto, título, descrição, categoria e centro. Os indicadores inferiores permitem trocar uma formação de cada vez; o teste manual passou de “Bem-estar e Saúde Mental no Trabalho” para “Higiene e Segurança Alimentar” sem alterar o formulário. A tela continua sem rolagem vertical em desktop.

O mesmo painel foi validado na criação de conta, onde os quatro campos continuam totalmente visíveis e a página mantém `0` pixels abaixo do viewport. A verificação do console do navegador não reportou erros após introduzir a rotação de cursos.

## Área do Aluno

A rota React `/aluno` foi validada para visitantes: ela apresenta uma mensagem clara de acesso restrito e um botão que encaminha para `/entrar?next=/aluno`. O percurso preserva o destino pretendido para que, depois da autenticação, o aluno seja encaminhado para a sua área pessoal.

Com a conta de demonstração, o login devolveu corretamente para `/aluno`. O painel carregou a inscrição presencial real, incluindo o curso, o centro, a turma, data e horário de início, estado “Aceita” e a ficha de inscrição. Os contadores também refletiram os dados existentes: um curso ativo, nenhuma inscrição pendente e nenhum certificado emitido.

Os cartões do catálogo foram verificados com os 22 produtos publicados. Cada cartão apresenta agora o valor real a pagar no momento e a condição informada pelo centro ou vídeo-curso, por exemplo “Taxa de inscrição”, “Taxa de inscrição + 1ª mensalidade”, “Preço total do curso”, “Sem pagamento no ato” ou “Acesso sem pagamento”. A validação confirmou que vídeo-cursos pagos, formações gratuitas e pagamentos posteriores são diferenciados sem usar valores simulados.
