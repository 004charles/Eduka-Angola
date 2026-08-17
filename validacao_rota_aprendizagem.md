# Validação — Continuação de aprendizagem

Data: 17 de agosto de 2026.

## Resultado

A rota React `/aprender/video/excel-para-o-dia-a-dia` foi aberta directamente no preview e deixou de apresentar a página genérica **Página não encontrada**. O router encaminhou-a para a página **Sala de aprendizagem**.

O ambiente de teste autenticado devolveu a mensagem **Não tem acesso a este vídeo-curso**, o que confirma que a verificação de autorização da API continua activa para esse curso específico. Este resultado é esperado quando a conta actual não está inscrita nesse curso e é distinto do erro de roteamento inicialmente reportado.

## Correcção aplicada

O botão **Continuar a aprender** agora privilegia o endereço `aprendizagem_url` fornecido pelo dashboard. Se a sessão ainda tiver dados antigos sem esse campo, o frontend extrai o slug do URL legado e reconstrói `/aprender/video/:slug`, evitando que o aluno seja enviado para uma rota inexistente.
