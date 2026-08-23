# Inventário de páginas HTML/Django e React

## Conclusão

A experiência principal da Edukangola já é entregue pelo React. O encaminhamento principal entrega ao React as rotas públicas, a área do aluno, o GestorEduka, cursos, vídeo, centros, Biblioteca, Mercado, eventos, blog, pagamento e autenticação moderna.

Ainda existem muitos templates HTML no repositório. Eles dividem-se entre páginas legadas de compatibilidade, áreas que não pertencem ao lançamento actual e documentos/e-mails que **devem continuar HTML**. A existência do ficheiro `.html` não significa, por si só, que o aluno actual está a ver HTML.

## Já React na jornada principal

| Jornada | Rotas React |
|---|---|
| Público | `/`, `/cursos`, `/cursos/:id`, `/centros`, `/centros/:id`, `/como-funciona`, `/sobre`, `/para-centros`, `/blog`, `/eventos`, `/mercado`, `/biblioteca` |
| Conta e aluno | `/entrar`, `/criar-conta`, `/verificar-email`, `/recuperar-palavra-passe`, `/redefinir-palavra-passe`, `/aluno`, `/aluno/historico`, `/aluno/mensagens`, `/aluno/configuracoes`, `/aluno/certificados` |
| Inscrição e pagamento | `/inscrever/:id`, `/comprar/:slug`, `/pagamento/sucesso`, `/pagamento/cancelado`, `/mercado/pedidos` |
| Cursos em vídeo | `/cursos-em-video`, `/video-cursos/:slug`, `/aprender/video/:slug` |
| GestorEduka | `/gestoreduka/*`, excepto o endpoint de login legado que redirecciona para o backend quando necessário |

## HTML activo que ainda merece decisão ou migração

| Área | Rotas/páginas HTML ainda existentes | Prioridade |
|---|---|---|
| Autenticação e aluno legados | `usuarios/templates/login*.html`, `cadastro_*.html`, `esqueci_senha.html`, `redefinir_senha.html`, `verificar_codigo.html`, `aluno/*.html`, `aluno_base.html`, `user_profile.html`; expostos sob `/auth/...` | **Alta**: manter apenas como compatibilidade temporária, redireccionar links antigos para as rotas React e remover depois de confirmar ausência de uso. |
| Curso em vídeo legado | `cursovideoapp/templates/video/home.html`, `lista_cursos.html`, `detalhe_curso.html`, `ver_aula.html`, `orientador_ia.html`, `analytics_mercado.html`; expostos em `/curso_video/...` | **Alta**: a experiência oficial já é React. Estes caminhos devem redireccionar para `/cursos-em-video`, `/video-cursos/:slug` e `/aprender/video/:slug`, preservando somente APIs e ferramentas operacionais necessárias. |
| Portal de instrutor legado | `instrutores_app/templates/instrutores/*.html`, com dashboard, cursos, aulas, alunos, exercícios, login e candidatura | **Média/decisão de produto**: a estratégia actual é formador como aluno qualificado, sem dashboard independente. Deve ser retirado ou reconstruído apenas se a área voltar a fazer parte do produto. |
| Escolas | `escolas/templates/escolas/*.html` e `escolas/admin/*.html`, com onboarding, perfis, gestão de cursos, galeria e parcerias | **Média**: é um módulo paralelo que não está integrado no menu React principal. Decidir se será produto futuro ou se deve ficar escondido até ganhar uma versão React coerente. |
| Carreira, estágios e bolsas | `carreira/templates/carreira/*.html`, `estagio/templates/estagio/*.html`, `bolsas/templates/bolsas/candidatar.html` | **Média/baixa**: manter fora da campanha de lançamento. Migrar para React apenas depois de confirmar que estas ofertas serão públicas no MVP. |
| Centro antigo | `centro_formacao/templates/home_centro.html` e templates antigos de GestorEduka | **Baixa**: o GestorEduka React substitui a operação principal. Os templates podem ser mantidos como fallback técnico até haver limpeza planeada. |
| Blog legado | `blog/templates/lista_posts.html`, `detalhe_post.html`, busca, categoria e tag | **Baixa**: o blog público React já é a experiência oficial; os templates servem ligações e administração antigas. |

## HTML que deve permanecer

| Tipo | Exemplos | Razão |
|---|---|---|
| E-mails | `templates/emails/*.html`, `pagamentos/templates/pagamentos/email_*.html` | E-mail exige HTML próprio e não deve ser React de browser. |
| Documentos e comprovativos | `usuarios/templates/usuarios/ficha_inscricao_pdf.html`, `gestoreduka/templates/gestor/financeiro/recibo.html`, `templates/mockup_certificado.html` | São renderizações para PDF, impressão ou e-mail. |
| Administração técnica | `templates/admin/*`, `templates/unfold/*` | São necessários para gestão operacional interna, não para a experiência pública. |
| Resiliência | `templates/404.html`, `templates/500.html`, `templates/offline.html` | São fallbacks do servidor quando o React não pode carregar. |
| Fragmentos | `templates/components/*`, `usuarios/templates/include/*`, `gestoreduka/templates/include/*` | São peças de compatibilidade, não páginas completas do produto. |

## Ordem recomendada

1. Redireccionar os links legados de aluno, autenticação e `/curso_video/*` para React; medir durante um período curto se algum fluxo depende deles.
2. Remover ou desligar o portal antigo de instrutor, em coerência com o novo modelo de formador elegível a partir da conta de aluno.
3. Decidir explicitamente o futuro de Escolas, Carreira, Estágios e Bolsas antes de gastar esforço em migração visual.
4. Apenas depois, eliminar templates e views não utilizados. Não eliminar e-mails, recibos, PDFs, admin ou páginas de erro.
