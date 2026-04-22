# 🎓 EdukAngola — Plataforma Integrada de Educação e Gestão

O **EdukAngola** é uma plataforma educacional e sistema de gestão completo que conecta:

- Instituições de ensino (escolas, universidades, centros de formação)
- Estudantes em busca de formação e qualificação
- Empresas e parceiros que valorizam certificados reconhecidos e aprendizagem prática

Nosso objetivo é criar um ecossistema educacional escalável, que simplifica processos, profissionaliza instituições e oferece qualidade acadêmica de padrão internacional.

---

## 🚀 Missão

Promover o acesso ao conhecimento, a modernização da educação em Angola e a valorização de instituições de ensino por meio da tecnologia.

## 🎯 Visão

Ser a maior plataforma de gestão educacional e cursos online em Angola — com expansão para outros países lusófonos.

---

## 🌍 Público-Alvo

- Universidades públicas e privadas  
- Centros de formação profissional  
- Escolas de ensino básico e secundário  
- Alunos em busca de cursos de qualidade  
- Empresas que valorizam formação contínua  

---

## 🏆 Diferenciais Competitivos

- ✅ Gestão multi-filial e multi-permissão  
- ✅ Certificados com QR Code e validação pública  
- ✅ Trilhas de aprendizagem e gamificação  
- ✅ Preparado para provas práticas avançadas (ambientes virtuais)  
- ✅ Página pública profissional para cada instituição  
- ✅ Modular: pode ser usado como marketplace ou apenas como sistema interno (GestorEduka)  

---

## 💼 Objetivos Estratégicos

- Digitalizar a gestão educacional e reduzir burocracias  
- Tornar cursos acessíveis em todo o território nacional  
- Elevar a credibilidade de instituições com certificados validados  
- Criar novas receitas por meio de comissões e pacotes premium  

---

## 🏗️ Stack Técnica

| Camada              | Tecnologias                                     |
|---------------------|--------------------------------------------------|
| Backend             | Django / Django Rest Framework                  |
| Frontend Web        | HTML CSS JAVASCRIPT                             |
| Banco de Dados      | PostgreSQL                                      |
| Autenticação        | Django Auth + JWT                               |
| Armazenamento       | S3-compatible (AWS, MinIO)                      |
| Ambientes de Prova  | Docker / Kubernetes                             |
| Player de Vídeo     | Plyr + DRM                                      |

---

## 🟢 Estrutura do Sistema

O EdukAngola é composto por duas grandes áreas principais:

### 1. Plataforma EdukAngola (Ambiente Público + Área do Aluno)

- Interface de descoberta de cursos
- Inscrição online com envio de documentos
- Área do aluno com provas, progresso e certificados
- Painel básico do professor
- Página pública de certificados com QR Code

### 2. GestorEduka (Painel Administrativo da Instituição)

- Gestão de instituições e suas filiais
- Matrículas, financeiro e controle de bolsas
- Provas, tarefas e correções
- Emissão de certificados em lote
- Relatórios avançados e personalização visual

---

## 📦 Funcionalidades

### 🎓 Plataforma EdukAngola (Marketplace + Aluno)

| Nº | Módulo                         | Descrição                                                                 |
|----|--------------------------------|---------------------------------------------------------------------------|
| 1  | Catálogo de Cursos             | Pesquisa com filtros (categoria, duração, preço, bolsas)                  |
| 2  | Página da Instituição          | Perfil personalizado com logo, cores e cursos                             |
| 3  | Inscrição Online               | Formulários completos com upload de documentos                            |
| 4  | Conta do Aluno                 | Dashboard com inscrições, progresso e certificados                        |
| 5  | Provas e Tarefas               | Questões objetivas, dissertativas e envio de arquivos                     |
| 6  | Avaliação e Feedback           | Visualização de notas e comentários dos professores                       |
| 7  | Certificados e Validação       | Emissão de PDFs com QR Code e validação pública                           |
| 8  | Notificações                   | Emails e alertas personalizados                                           |
| 9  | Painel do Professor (básico)   | Visualização de turmas e correção de provas                               |
| 10 | Histórico de Pagamentos        | Visualização dos pagamentos processados offline                           |
| 11 | Sistema de Mensagens (futuro) | Comunicação entre alunos e professores                                    |
| 12 | Trilhas de Aprendizagem       | Sistema de progressão com pré-requisitos e badges (futuro)                |

### 🛠️ GestorEduka (Administração)

| Nº | Módulo                        | Descrição                                                                 |
|----|-------------------------------|---------------------------------------------------------------------------|
| 1  | Cadastro da Instituição       | Dados gerais, logotipo e perfil público                                   |
| 2  | Gestão de Filiais             | Criação de filiais com permissões específicas                             |
| 3  | Perfis e Permissões           | Controle de acessos (admin, gestor, secretaria, professor)                |
| 4  | Cadastro de Cursos            | Nome, descrição, valor, bolsas e filiais vinculadas                       |
| 5  | Cadastro de Turmas            | Horários, capacidade e professores atribuídos                             |
| 6  | Matrículas e Inscrições       | Aprovação manual ou automática                                            |
| 7  | Gestão Financeira             | Mensalidades, bolsas, descontos e relatórios                              |
| 8  | Gestão de Provas              | Criação de questões, tarefas e pontuações                                 |
| 9  | Correção e Avaliação          | Lançamento de notas e feedback                                            |
| 10 | Emissão de Certificados       | Geração individual e em lote                                              |
| 11 | Materiais Didáticos           | Upload de PDFs, vídeos e conteúdos interativos                            |
| 12 | Calendário Acadêmico          | Planejamento visual de atividades                                         |
| 13 | Relatórios e Dashboards       | Indicadores financeiros e acadêmicos                                      |
| 14 | Notificações Personalizadas   | Templates de email e eventos automáticos                                  |
| 15 | Customização Visual           | Identidade visual do painel e da página pública                           |
| 16 | Trilhas e Progressão (futuro) | Sistema de badges e caminhos de aprendizagem                              |
| 17 | Avaliação por Pares (futuro) | Peer review entre estudantes, inspirado na metodologia da Escola 42       |
| 18 | Provas Práticas (futuro)      | Execução de exercícios em ambientes virtuais com Docker/VMs               |

---

## 🔌 Integrações Futuras

- Pagamentos via Multicaixa e Visa  
- Gateways de pagamento internacionais  
- Integração com ERPs educacionais via API  
- Aplicativo player com DRM integrado  
- Marketplace de cursos de terceiros  

---

## 💡 Diagrama da Arquitetura

```plaintext
+-------------------+           +---------------------+
|   Visitantes      |           |     Professores     |
+-------------------+           +---------------------+
          \                             /
           \                           /
            V                         V
+--------------------------------------------+
|         Plataforma EdukAngola              |
|--------------------------------------------|
| - Catálogo de Cursos                       |
| - Inscrição e Pagamentos Offline           |
| - Conta do Aluno                           |
| - Provas e Tarefas                         |
| - Certificados                             |
+--------------------------------------------+
                 |
+----------------+-----------------+
                 |
                 V
+--------------------------------------------+
|              GestorEduka                   |
|--------------------------------------------|
| - Gestão de Cursos e Turmas                |
| - Matrículas e Financeiro                  |
| - Provas e Avaliações                      |
| - Materiais Didáticos                      |
| - Relatórios e Estatísticas                |
+--------------------------------------------+

🏅 Por que escolher o EdukAngola?
✅ Modular e escalável

✅ Certificados com QR Code e verificação pública

✅ Preparado para múltiplas instituições e filiais

✅ Foco no sucesso do aluno e na credibilidade das instituições

✅ Suporte a provas práticas e peer review

📢 Contato
Para parcerias, dúvidas ou suporte:

📧 Email: emelsonmuquissi@gmail.com

📞 Telefones: +244 936 327 119 / +244 923 908 353

Atualizado em: Julho de 2025

