# Edukangola Android — Trusted Web Activity

Este directório contém a configuração rastreável da embalagem Android da PWA pública `https://www.edukangola.com`.

## Identidade definida

| Campo | Valor |
|---|---|
| Nome da aplicação | Edukangola |
| Identificador Android | `com.edukangola.app` |
| Origem validada | `https://www.edukangola.com` |
| Modo de abertura | Standalone |
| Versão inicial | `1.0.0` (código 1) |
| Recursos incluídos | Notificações, atalhos e geolocalização delegada pelo Android |

## Antes da primeira compilação assinada

1. Crie a aplicação `com.edukangola.app` na Google Play Console e active **Play App Signing**.
2. Copie a impressão SHA-256 do certificado de assinatura da aplicação em **Integridade da aplicação**.
3. Substitua o texto de exemplo em `assetlinks.json.template` pela impressão SHA-256 e publique o resultado em `frontend/public/.well-known/assetlinks.json`.
4. Confirme que `https://www.edukangola.com/.well-known/assetlinks.json` devolve JSON, não a página React.
5. Crie e guarde o ficheiro `android.keystore` fora do Git. A chave e as palavras-passe não devem ser guardadas neste repositório.

## Gerar a aplicação

Depois de a chave estar disponível, execute no directório `android-twa`:

```bash
bubblewrap update --manifest=./twa-manifest.json
bubblewrap build --manifest=./twa-manifest.json
```

O resultado esperado é `app-release-bundle.aab`, a versão a enviar primeiro para o canal de testes internos da Play Console.

> A configuração actual não activa Play Billing. Antes de uma publicação pública que venda subscrições de cursos em vídeo dentro da aplicação Android, reveja a política de pagamentos aplicável da Google Play e decida a integração de cobrança Android adequada.
