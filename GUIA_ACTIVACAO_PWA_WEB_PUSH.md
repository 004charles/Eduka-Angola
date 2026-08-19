# Guia de Activação — PWA e Web Push da Edukangola

**Objectivo.** Este guia activa a experiência instalada da Edukangola e o envio próprio de notificações para dispositivos, sem Firebase, sem redes publicitárias externas e sem guardar chaves no GitHub.

> O manifesto é a fonte de metadados que o navegador usa ao instalar uma PWA, incluindo nome, ícones, cores e modo de apresentação. A implementação utiliza `display: standalone`, ícones PNG 192/512 e atalhos de entrada. [1]

## Componentes entregues

| Componente | Implementação | Estado de activação |
|---|---|---|
| Instalação PWA | `app.webmanifest`, ícones PNG, metadados Apple e `service-worker.js` | Pronto no código. |
| Navegação autónoma | Manifesto `standalone`, área segura e navegação móvel existente | Pronto no código. |
| Cache offline prudente | Estrutura da aplicação e recursos estáticos; API, sessão, inscrições e pagamentos ficam sempre dependentes do servidor | Pronto no código. |
| Web Push próprio | Service worker, subscrição autenticada, preferência do aluno, modelo `SubscricaoWebPush` e entrega VAPID por `pywebpush` | Requer chaves VAPID no ambiente. |
| Patrocínios educativos | Conteúdo gerido em `Publicidade`, filtrado para destinos internos e identificado como “Patrocinado” | Pronto no código. |

O canal Push exige um service worker activo; a subscrição produz um endpoint e chaves de encriptação específicos do dispositivo. Esses dados são tratados como dados sensíveis da subscrição e não são expostos no contrato público. [2]

## 1. Gerar e guardar o par VAPID

No computador seguro do operador, fora do repositório, execute os comandos seguintes. O ficheiro PEM deve ficar no gestor de segredos ou numa área privada do provedor, nunca em `.env` versionado, anexos públicos, capturas de ecrã ou GitHub.

```bash
mkdir -p /caminho-seguro/edukangola-vapid
vapid --gen --private-key /caminho-seguro/edukangola-vapid/edukangola-vapid.pem
vapid --applicationServerKey --private-key /caminho-seguro/edukangola-vapid/edukangola-vapid.pem
```

O segundo comando imprime a chave pública base64url. A primeira operação já foi validada tecnicamente no ambiente de desenvolvimento, sem persistir chaves no projecto.

| Variável de ambiente | Valor | Exposição permitida |
|---|---|---|
| `VAPID_PUBLIC_KEY` | Saída de `--applicationServerKey` | Pode ser enviada ao navegador autenticado apenas pelo endpoint de estado. |
| `VAPID_PRIVATE_KEY` | Conteúdo completo do PEM privado | **Apenas no gestor de segredos do servidor**. |
| `VAPID_SUBJECT` | Por exemplo, `mailto:suporte@edukangola.com` | Configuração pública de contacto do operador. |

VAPID identifica o servidor aplicacional perante o serviço Push com uma chave de assinatura e permite declarar um contacto do operador através da alegação `sub`. [3]

## 2. Aplicar no ambiente de produção

Depois de registar as três variáveis no painel seguro do provedor, execute a migração e reinicie o processo Django.

```bash
python3 manage.py migrate
python3 manage.py check
```

Não altere a chave VAPID depois de haver subscrições activas. Uma alteração invalida as subscrições restringidas à chave anterior e obriga cada dispositivo a voltar a autorizar as notificações. [3]

## 3. Validação por aluno

O aluno deve entrar na sua conta, abrir **Área do aluno → Preferências**, escolher **Activar notificações** e aceitar a autorização do navegador. Depois, o botão **Testar** cria uma notificação persistente de sistema e envia uma notificação ao dispositivo activo. A escolha é explícita, por dispositivo, e pode ser revertida no mesmo ecrã.

| Resultado esperado | Como confirmar |
|---|---|
| Subscrição guardada | O painel Django mostra uma `Subscrição Web Push` activa para o aluno. |
| Preferência ligada | `PreferenciaNotificacaoAluno.receber_push` fica activa. |
| Teste entregue | A notificação “Notificações Edukangola activas” aparece no dispositivo. |
| Cancelamento funcional | O botão “Desactivar” inactiva a subscrição actual no Django e cancela-a no navegador. |

## 4. Política de entrega

As notificações existentes da plataforma continuam a criar registos `NotificacaoAluno`. Depois da confirmação da transacção, cada novo registo pode ser entregue aos dispositivos activos do respectivo aluno. Falhas `404`/`410` invalidam a subscrição; três falhas consecutivas também a desactivam. A criação principal da notificação nunca falha por causa de Web Push.

| Incluído | Deliberadamente excluído |
|---|---|
| Novidades de cursos, turmas, livros, eventos e aprendizagem que respeitem as preferências existentes | Dados de pagamento, palavras-passe, documentação pessoal, resultado de candidaturas sensíveis e conteúdo que exija sessão para ser entendido. |
| Um clique abre uma rota interna da Edukangola | Redireccionamentos de patrocinadores externos. |
| Patrocínios educativos declarados e internos | Redes externas, pixels de seguimento e perfis publicitários de alunos. |

## 5. Diagnóstico rápido

| Sintoma | Verificação e acção |
|---|---|
| A opção informa que o ambiente ainda não está configurado | Confirmar as três variáveis VAPID e reiniciar Django. |
| O navegador não pede permissão | Confirmar HTTPS, service worker activo e que a permissão não está previamente bloqueada nas definições do site. |
| O teste não chega | Consultar o registo Django, verificar a subscrição activa e tentar novamente após abrir a PWA. |
| Um dispositivo antigo deixa de receber | A subscrição é automaticamente inactivada após resposta `404`/`410` ou três falhas; o aluno pode reactivar no ecrã de preferências. |
| O patrocínio não aparece | Criar/activar um registo `Publicidade` na posição `GERAL` com URL começada por `/`. URLs externas são recusadas pela API pública. |

## Referências

[1] [MDN — Web application manifest](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest)

[2] [MDN — Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)

[3] [IETF RFC 8292 — Voluntary Application Server Identification (VAPID) for Web Push](https://datatracker.ietf.org/doc/html/rfc8292)
