# Integração Cartesia na Biblioteca

## Decisão de arquitectura

A Biblioteca solicitará áudio apenas ao backend Django, que autentica a pessoa com sessão válida, verifica que o livro está publicado, tem direitos confirmados e possui leitura digital autorizada. A chave da Cartesia ficará exclusivamente em `CARTESIA_API_KEY` no ambiente do Render; não será enviada ao navegador, registada em logs nem incluída no Git.

Para a leitura de uma página ou capítulo completo, será usado `POST https://api.cartesia.ai/tts/bytes`. O serviço aceita um transcript completo e devolve bytes de áudio, o que se adequa à reprodução de um trecho por vez. A implementação enviará `Authorization: Bearer <chave>` e `Cartesia-Version: 2026-08-14` apenas a partir do servidor.

## Configuração inicial

| Configuração | Valor inicial |
|---|---|
| Modelo | `sonic-3.5` |
| Idioma | `pt` |
| Saída | MP3, 44 100 Hz, 128 kbps |
| Ritmo | Ajustável entre 0,8× e 1,3× pelo leitor |
| Voz | Definida por `CARTESIA_VOICE_ID` depois de avaliação na biblioteca de vozes Cartesia |

> A voz só será activada em produção depois de escolher e validar uma voz portuguesa adequada no painel Cartesia. Não será usada voz clonada sem autorização documentada.

## Referências

- [Cartesia — Text-to-Speech (Bytes)](https://docs.cartesia.ai/api-reference/tts/bytes.md)
- [Cartesia — Autenticação de aplicações cliente](https://docs.cartesia.ai/get-started/authenticate-your-client-applications.md)
- [Cartesia — Comparação de endpoints TTS](https://docs.cartesia.ai/use-the-api/compare-tts-endpoints.md)
