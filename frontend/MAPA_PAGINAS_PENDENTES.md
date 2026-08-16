# Mapa de Migração: Versão Django Antiga → Frontend React

## Escopo da análise

Este mapa compara as rotas públicas e de aluno existentes no Django com as rotas já implementadas no frontend React da Edukangola. O **GestorEduka** e o painel operacional dos centros não entram nesta migração, pois devem continuar no Django conforme a decisão do projeto.

## Já migrado para React

| Área | Rotas React atuais | Situação |
|---|---|---|
| Descoberta pública | `/` | Página inicial com campanhas, categorias, cursos e centros publicados. |
| Catálogo | `/cursos` | Filtros de produto, categoria, província, turma e condição de pagamento. |
| Curso presencial | `/cursos/:id` | Detalhe, turmas, vagas, condições e recomendados. |
| Vídeo-curso | `/video-cursos/:slug` | Detalhe, aulas, turma de acompanhamento quando existe e compra/acesso. |
| Centros, visão inicial | `/centros` | Centros em destaque e encaminhamento para o diretório legado. |
| Informação do processo | `/como-funciona` | Explicação do percurso de inscrição. |
| Autenticação | `/entrar`, `/criar-conta`, `/verificar-email`, `/recuperar-palavra-passe`, `/redefinir-palavra-passe` | Telas React integradas ao Django, com cursos em destaque. |
| Checkout | `/inscrever/:id`, `/comprar/:slug` | Inscrição presencial e compra/acesso de vídeo-curso com resumo prévio. |

## Páginas prioritárias que ainda faltam

| Prioridade | Página/experiência React a criar | Rota Django antiga de referência | Motivo |
|---|---|---|---|
| P0 | **Área do aluno — painel inicial** | `/auth/aluno/` e `/auth/aluno/dashboard/` | É o destino natural depois de login, inscrição e compra. Deve reunir cursos, inscrições pendentes, pagamentos e próximos passos. |
| P0 | **Os meus cursos** | `/auth/aluno/cursos/` | Permite ver formações presenciais e vídeo-cursos já associados ao aluno. |
| P0 | **Ambiente de aprendizagem de vídeo** | `/curso_video/:slug/aula/:id/` | Falta a página em que o aluno efetivamente vê aulas, acompanha progresso, toma notas e faz exercícios. |
| P0 | **Estado da inscrição e confirmação de pagamento** | `/cursos/pagamento/:id/`, `/pagamento/sucesso/`, `/pagamento/cancelado/` | A Prontu confirma o pagamento, mas o retorno ainda usa páginas Django antigas. É importante criar confirmações React claras. |
| P0 | **Comprovativo/ficha de inscrição** | `/auth/aluno/inscricao/:id/ficha/` e `/cursos/comprovante_inscricao/:id/` | O aluno deve consultar, descarregar ou partilhar a ficha depois de se inscrever. |

## Segunda etapa recomendada

| Prioridade | Página/experiência React a criar | Rota Django antiga de referência | Observação |
|---|---|---|---|
| P1 | **Perfil e configurações do aluno** | `/auth/aluno/perfil/`, `/auth/aluno/configuracoes/`, `/auth/conta_aluno/` | Dados pessoais, contacto, localização, palavra-passe e preferências. |
| P1 | **Favoritos** | `/auth/aluno/favoritos/` | Guardar formações para decidir mais tarde. |
| P1 | **Certificados do aluno** | Emissão em `/curso_video/emitir-certificado/:slug/` e validação em `/curso_video/verificar-certificado/:codigo/` | Deve ter área de certificados emitidos e página pública de validação. |
| P1 | **Avaliações e comentários** | Rotas de comentários de curso e vídeo-curso | O backend já suporta comentários, mas a interface React ainda não os apresenta. |
| P1 | **Diretório e perfil completo de centro** | `/cursos/instituicoes/`, `/cursos/centro/:id/cursos/` | A página React mostra centros em destaque, mas o diretório completo e o perfil de cada centro ainda apontam ao Django. |

## Páginas institucionais ainda no Django

| Página | Rota antiga | Decisão sugerida |
|---|---|---|
| Sobre a Edukangola | `/sobre/` | Migrar depois da área do aluno. |
| Contacto | `/contato/` | Migrar depois da área do aluno; pode incluir formulário React. |
| Perguntas frequentes | `/faq/` | Migrar junto com contacto e páginas institucionais. |
| Blog | `/blog/` | Módulo independente; não bloqueia cursos e inscrições. |
| Bolsas | `/fundo-bolsas/` e `/bolsas/` | Produto próprio, recomendado para uma fase posterior. |
| Carreiras/vagas | `/carreira/vagas/` | Produto próprio, recomendado para uma fase posterior. |
| Escolas e orientação escolar | `/escolas/` | Produto próprio, recomendado para uma fase posterior. |

## Fora do escopo desta migração

O **GestorEduka**, os painéis de instrutores, administração, gestão de turmas, presenças, notas, finanças e operação dos centros continuam no Django. A regra é usar o React para a jornada pública e do aluno, preservando o GestorEduka como sistema operacional dos centros.

## Sequência recomendada

> **1. Área do aluno → 2. Meus cursos → 3. Player/ambiente de aprendizagem → 4. Confirmação e comprovativos → 5. Perfil, favoritos e certificados → 6. Centros completos → 7. Páginas institucionais.**

Esta ordem fecha o ciclo principal: descobrir curso, criar conta, inscrever/comprar, pagar, aprender e acompanhar o próprio percurso.
