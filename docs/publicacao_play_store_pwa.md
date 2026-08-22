# Publicação Android da Edukangola na Google Play

**Autor:** Manus AI  
**Objectivo:** distribuir a PWA Edukangola como aplicação Android através de uma Trusted Web Activity (TWA), mantendo `https://www.edukangola.com` como a única fonte de conteúdo e actualizações.

> A TWA abre a PWA instalada; por isso, uma actualização publicada no site é reflectida na aplicação sem ser necessário reenviar o AAB, desde que não altere a embalagem Android, permissões ou identidade da aplicação. Uma alteração dessas características exige uma nova versão Android. [1]

## Estado da preparação

| Área | Situação | Observação |
|---|---|---|
| Origem web | Preparada | `https://www.edukangola.com` publica o manifesto em `app.webmanifest`. |
| Identidade Android | Preparada | Nome **Edukangola** e pacote `com.edukangola.app`. |
| Projecto TWA | Preparado | `android-twa/twa-manifest.json` gerou a base Android sem chave privada. |
| Localização | Preparada | A delegação de geolocalização Android está activa para a funcionalidade de cursos próximos, sempre dependente do consentimento do utilizador. |
| Notificações e atalhos | Preparados | A embalagem activa a delegação de notificações e os atalhos publicados no manifesto PWA. |
| `assetlinks.json` | Pendente | O domínio devolve actualmente HTML nessa rota; precisa de JSON válido com a impressão SHA-256 final. |
| AAB assinado | Pendente | Depende de uma chave de envio protegida e da configuração de assinatura na Play Console. |

## Sequência segura de publicação

| Ordem | Acção | Resultado esperado |
|---:|---|---|
| 1 | Criar a aplicação **Edukangola** na Play Console com o pacote `com.edukangola.app`. | Aplicação em rascunho, ainda não pública. |
| 2 | Em **Integridade da aplicação**, activar **Play App Signing** e guardar a impressão SHA-256 do certificado de assinatura da aplicação. | A impressão que o Android aceitará para a associação do domínio. |
| 3 | Criar uma chave de envio (`android.keystore`) fora do Git e guardar as palavras-passe num gestor de palavras-passe institucional. | Chave privada recuperável e nunca exposta no repositório. |
| 4 | Substituir o marcador em `android-twa/assetlinks.json.template` pela impressão SHA-256 obtida no passo 2. | Ficheiro Digital Asset Links definitivo. |
| 5 | Copiar o resultado para `frontend/public/.well-known/assetlinks.json`, publicar manualmente no Vercel e verificar o cabeçalho `Content-Type: application/json`. | `https://www.edukangola.com/.well-known/assetlinks.json` devolve JSON, não a página React. |
| 6 | Executar `bubblewrap build --manifest=./twa-manifest.json` dentro de `android-twa`, sem guardar o AAB ou a chave no Git. | `app-release-bundle.aab` assinado. [2] |
| 7 | Enviar o AAB para **Teste interno** da Play Console. | Ligação de instalação para a equipa de validação. |
| 8 | Validar o comportamento real e só então avançar para teste fechado e produção. | Evidência de funcionamento antes da revisão pública. |

## Associação de domínio

O ficheiro final a publicar deve ter esta estrutura. O valor da impressão não pode ser inventado: deve ser a impressão SHA-256 real apresentada pela Play Console após a configuração da assinatura.

```json
[
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "com.edukangola.app",
      "sha256_cert_fingerprints": [
        "IMPRIMIR_A_SHA256_REAL_DO_CERTIFICADO_PLAY_AQUI"
      ]
    }
  }
]
```

> Sem uma associação Digital Asset Links válida, a aplicação Android abre a Edukangola como uma Custom Tab em vez da experiência TWA integrada. [1]

## Testes obrigatórios antes da produção

O teste interno permite distribuir rapidamente até **100 testadores** e deve ser o primeiro canal para a validação de qualidade. [3] Se a conta pessoal de programador foi criada depois de 13 de Novembro de 2023, a Google exige antes da produção um teste fechado com pelo menos **12 testadores activos durante 14 dias consecutivos**. [4]

| Fluxo | Critério de aceitação |
|---|---|
| Arranque | A aplicação abre `www.edukangola.com` sem barra do navegador depois de a associação ser validada. |
| Autenticação | Iniciar e terminar sessão funciona entre `www` e `api`, sem perder a sessão indevidamente. |
| Cursos próximos | O pedido Android de localização surge apenas após a intenção do utilizador; negar não bloqueia a descoberta manual. |
| Notificações | A preferência de notificações é respeitada; o pedido de permissão não é repetido de forma intrusiva. |
| Pagamentos | Os redireccionamentos de pagamento regressam à Edukangola e apresentam o estado correcto. |
| Navegação | Catálogo, cursos em vídeo, Mercado, área do aluno, perfil, mensagens e links externos têm retorno ou abertura adequados. |
| Actualização web | Uma alteração não-nativa publicada no Vercel é visível após a actualização normal da PWA, sem novo AAB. |

## Conteúdo da aplicação na Play Console

A página **Conteúdo da aplicação** exige declarações de privacidade, anúncios, acesso para revisão, público-alvo e classificação etária. A política de privacidade deve estar num URL activo e explicar os dados e permissões usados pela Edukangola. [5]

| Declaração | Informação a preparar para a Edukangola |
|---|---|
| Política de privacidade | URL público da política já publicada no site, actualizado para cobrir conta, pagamentos, localização, notificações e histórico de aprendizagem. |
| Acesso de aplicações | Credenciais de revisão funcionais ou instruções exactas para o revisor aceder às áreas protegidas. |
| Dados e permissões | Justificação clara de localização para centros/cursos próximos e de notificações para avisos opt-in. |
| Anúncios | Declarar com precisão a presença de patrocínios educativos internos se forem apresentados como publicidade. [5] |
| Público-alvo | Declarar a faixa etária real. A TWA alerta para atenção adicional quando a aplicação se destina a menores de 13 anos. |
| Monetização | Rever a política Play aplicável a subscrições e conteúdos digitais antes do lançamento público; a configuração TWA actual não integra Play Billing. |

## Actualizações posteriores

As alterações ao site, dados, cursos, catálogo e conteúdos em vídeo permanecem no fluxo web normal: revisão, *commit*, *push* e publicação manual no Vercel. A aplicação instalada reflecte essas actualizações porque carrega o mesmo domínio. Uma nova versão AAB só deve ser criada ao alterar o pacote, certificado, permissões nativas, cor/ícone da embalagem, recursos TWA ou dependências Android.

## Referências

[1] [Chrome for Developers — Quick start to Trusted Web Activities](https://developer.chrome.com/docs/android/trusted-web-activity/quick-start)  
[2] [GoogleChromeLabs — Bubblewrap CLI: criar e compilar o projecto](https://github.com/GoogleChromeLabs/bubblewrap/tree/main/packages/cli)  
[3] [Google Play Console Help — Configurar teste interno, fechado ou aberto](https://support.google.com/googleplay/android-developer/answer/9845334?hl=pt-BR)  
[4] [Google Play Console Help — Requisitos de teste para contas pessoais](https://support.google.com/googleplay/android-developer/answer/14151465?hl=pt-BR)  
[5] [Google Play Console Help — Preparar a aplicação para revisão](https://support.google.com/googleplay/android-developer/answer/9859455?hl=pt-BR)
