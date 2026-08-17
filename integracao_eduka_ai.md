# Activação da Eduka AI

## Diagnóstico

O botão **Perguntar à Eduka AI** chama o endpoint autenticado da sala de aprendizagem. Esse endpoint utiliza a API Groq para gerar uma resposta baseada no curso, na aula, na descrição e no resumo disponível.

Para que a resposta funcione fora do ambiente local, a aplicação Django precisa de receber a chave no ambiente do provedor. A chave não deve ser incluída no repositório nem em ficheiros versionados.

## Variáveis obrigatórias

| Variável | Valor esperado | Finalidade |
|---|---|---|
| `GROQ_API_KEY` | Chave privada emitida pela Groq | Autoriza os pedidos da Eduka AI |
| `GROQ_MODEL` | Opcional; predefinição `llama-3.1-8b-instant` | Permite escolher o modelo de resposta |

## Activação no ambiente actual

No painel do mesmo provedor onde o Django está alojado, abrir as variáveis de ambiente do serviço web Django, criar `GROQ_API_KEY` e guardar a chave privada. Em seguida, efectuar um novo deploy ou reiniciar o serviço. A variável `GROQ_MODEL` só deve ser criada se for necessário substituir o modelo predefinido.

## Comportamento depois da activação

Um aluno inscrito num curso em vídeo escreve uma pergunta na secção **Dúvidas** e selecciona **Perguntar à Eduka AI**. A resposta é devolvida no mesmo ecrã. Se a chave estiver ausente, inválida ou o fornecedor estiver indisponível, a interface mostra uma mensagem clara e mantém a dúvida escrita para o aluno poder tentar novamente ou enviá-la ao formador.
