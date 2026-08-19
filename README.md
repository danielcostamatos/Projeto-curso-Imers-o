# Projeto Imersão - Análise de Comunicação

Sistema web em Python para análise de comunicação a partir de áudio, vídeo e texto, com foco em transcrição, correção textual, avaliação de clareza, fluidez, organização da mensagem, pausas, repetições, qualidade comunicativa e geração de relatórios em DOCX.

O projeto foi desenvolvido como MVP para apoiar avaliações pedagógicas de comunicação, permitindo que usuários gravem áudio, enviem vídeos na versão local ou escrevam textos para receber feedback estruturado com apoio de inteligência artificial.

---

## Funcionalidades principais

* Cadastro e login de usuários com Supabase Auth.
* Cadastro e edição de perfil do usuário.
* Upload de foto de perfil com Supabase Storage.
* Análise por áudio gravado diretamente no navegador.
* Análise por vídeo na versão local.
* Análise por texto digitado.
* Extração automática de áudio com FFmpeg.
* Transcrição automática com Whisper.
* Análise de pausas e tempo de silêncio.
* Identificação de repetições sequenciais e termos recorrentes.
* Avaliação global da comunicação com Gemini.
* Correção textual com IA.
* Avaliação textual com critérios próprios.
* Cálculo de score de comunicação oral.
* Cálculo de score textual.
* Histórico de análises por usuário.
* Limite mensal de análises.
* Expiração automática das análises após 15 dias.
* Descarte de análise com confirmação.
* Geração de relatório profissional em DOCX.
* Painel administrativo somente leitura.
* Interface web com Streamlit.
* Deploy web com Streamlit Cloud.

---

## Tipos de análise

O sistema possui três formas de análise:

### Áudio

Na versão web, o usuário pode gravar um áudio diretamente pelo navegador. O sistema processa a fala, gera a transcrição e avalia a comunicação oral.

### Vídeo

Na versão local, o usuário pode enviar um vídeo. O sistema extrai o áudio do arquivo, realiza a transcrição e avalia a apresentação oral.

### Texto

O usuário pode digitar um texto para análise. O sistema avalia aspectos de escrita, corrige o conteúdo e gera recomendações específicas.

A análise textual considera critérios como:

* Ortografia e gramática.
* Pontuação.
* Coerência.
* Coesão.
* Clareza e objetividade.
* Estrutura.
* Desenvolvimento da ideia.

---

## Critérios de avaliação oral

Nas análises por áudio e vídeo, o sistema avalia a comunicação considerando:

* Controle de linguagem.
* Clareza.
* Formalidade.
* Fluidez.
* Qualidade geral da comunicação.
* Pausas longas.
* Repetições.
* Termos recorrentes.
* Organização e objetividade da fala.

Observação: vícios de linguagem e muletas de fala podem impactar o score internamente, mas não são exibidos como seção específica nos detalhes da análise ou no relatório DOCX.

---

## Tecnologias utilizadas

* Python
* Streamlit
* Supabase Auth
* Supabase Database
* Supabase Storage
* OpenAI Whisper
* Google Gemini API
* FFmpeg
* python-docx
* Matplotlib
* Git/GitHub
* Streamlit Cloud

---

## Requisitos

* Python 3.10 ou superior.
* FFmpeg instalado e configurado no PATH.
* Conta/projeto no Supabase.
* Chave da Gemini API.
* Ambiente virtual Python.
* Navegador com suporte à gravação de áudio para uso da versão web.

---

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as variáveis necessárias.

Exemplo:

```env
# Modo da aplicação
# local = análise por vídeo, áudio e texto
# web = análise por áudio e texto
APP_MODE=local

# Supabase
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_anon_do_supabase

# Gemini
GEMINI_API_KEY=sua_chave_gemini
GEMINI_MODEL=gemini-2.5-flash
```

A chave do Supabase usada no app deve ser a chave pública `anon`. O projeto não deve utilizar `service_role` no frontend ou no Streamlit.

A análise depende da conexão com a internet, do Supabase e da Gemini API.

---

## Modos da aplicação

O projeto possui dois modos principais de execução.

### Modo local

Usado para desenvolvimento e para a versão com análise por vídeo.

```env
APP_MODE=local
```

No modo local, o sistema permite:

* Enviar vídeo.
* Gravar áudio.
* Digitar texto.

### Modo web

Usado no deploy do Streamlit Cloud.

```env
APP_MODE=web
```

No modo web, o sistema permite:

* Gravar áudio.
* Digitar texto.

A opção de vídeo não aparece na versão web, pois o processamento de vídeo é mais pesado e foi reservado para a execução local.

---

## Estrutura atual do projeto

```text
app/
├── database/
│   ├── __init__.py
│   ├── admin_db.py
│   ├── profile_db.py
│   └── supabase_db.py
│
├── services/
│   ├── __init__.py
│   ├── analysis_pipeline.py
│   ├── attention_points_analyzer.py
│   ├── audio_extractor.py
│   ├── audio_file_manager.py
│   ├── avatar_storage.py
│   ├── docx_exporter.py
│   ├── gemini_full_context_analyzer.py
│   ├── network_checker.py
│   ├── pause_analyzer.py
│   ├── repetition_analyzer.py
│   ├── report_builder.py
│   ├── score_analyzer.py
│   ├── supabase_client.py
│   ├── temp_file_cleaner.py
│   ├── text_analysis_analyzer.py
│   ├── text_report_builder.py
│   ├── text_score_analyzer.py
│   └── transcriber.py
│
├── ui/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── avatar.py
│   │   ├── navigation.py
│   │   ├── report_view.py
│   │   ├── score.py
│   │   └── sidebar.py
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── admin_detail.py
│   │   ├── analysis.py
│   │   ├── auth.py
│   │   ├── detail.py
│   │   ├── history.py
│   │   ├── home.py
│   │   └── profile.py
│   │
│   ├── dashboard.py
│   ├── session_state.py
│   └── styles.py
│
├── utils/
│   ├── __init__.py
│   ├── app_mode.py
│   ├── file_manager.py
│   └── validators.py
│
└── main.py

data/
├── input/
├── temp/
├── output/
└── profile_images/

docs/
└── database/
    ├── README.md
    ├── supabase_checks.sql
    └── supabase_setup.sql

requirements.txt
requirements-lock.txt
packages.txt
.env.example
```

---

## Entrada principal da aplicação

O arquivo principal do projeto é:

```text
app/main.py
```

Ele chama o roteador principal da interface:

```text
app/ui/dashboard.py
```

O `dashboard.py` centraliza a navegação entre páginas, aplicação de estilos, autenticação de sessão, verificação de perfil e controle de acesso ao painel administrativo.

---

## Como rodar o projeto localmente

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### 2. Ativar ambiente virtual no Git Bash

```bash
source .venv/Scripts/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie o arquivo `.env` na raiz do projeto e preencha as variáveis necessárias:

```env
APP_MODE=local

SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_anon_do_supabase

GEMINI_API_KEY=sua_chave_gemini
GEMINI_MODEL=gemini-2.5-flash
```

### 5. Rodar a aplicação

```bash
python -m streamlit run app/main.py
```

### 6. Parar o Streamlit

```bash
Ctrl + C
```

---

## Deploy web

O projeto pode ser publicado no Streamlit Cloud.

Configuração usada no deploy:

```text
Main file path: app/main.py
Branch: main
Python: 3.12
```

No Streamlit Cloud, as variáveis devem ser configuradas em `Secrets`.

Exemplo:

```toml
APP_MODE = "web"

SUPABASE_URL = "sua_url_do_supabase"
SUPABASE_KEY = "sua_chave_anon_do_supabase"

GEMINI_API_KEY = "sua_chave_gemini"
GEMINI_MODEL = "gemini-2.5-flash"
```

Para o Streamlit Cloud instalar o FFmpeg, o projeto utiliza o arquivo:

```text
packages.txt
```

Com o conteúdo:

```text
ffmpeg
```

---

## Fluxo de uso

1. O usuário acessa a aplicação.
2. Faz login ou cria uma conta.
3. Completa o cadastro de perfil, caso ainda não tenha feito.
4. Acessa a página inicial.
5. Escolhe o tipo de análise.
6. Grava áudio, envia vídeo na versão local ou digita um texto.
7. Inicia a análise.
8. O sistema processa o conteúdo.
9. A IA gera avaliação, score e recomendações.
10. O relatório é salvo no histórico do usuário.
11. O usuário visualiza o resultado na tela.
12. O usuário pode baixar o relatório em DOCX.
13. O usuário pode acompanhar análises anteriores no histórico.

---

## Regras de armazenamento e privacidade

* Vídeos enviados não são armazenados no banco de dados.
* Vídeos são usados apenas temporariamente durante o processamento local.
* Áudios gravados na versão web não são armazenados no banco de dados.
* Áudios são usados apenas temporariamente durante o processamento.
* Textos digitados são salvos no banco como parte do relatório da análise textual.
* O banco salva relatórios, transcrições ou textos originais, scores e metadados.
* Fotos de perfil são armazenadas no Supabase Storage.
* A pasta `data/profile_images/` permanece como fallback local e compatibilidade.
* Arquivos temporários ficam em `data/input/` e `data/temp/`.
* O sistema limpa arquivos temporários em momentos importantes do fluxo, como login, logout, nova análise e troca de análise.
* As pastas de dados são preservadas no Git com arquivos `.gitkeep`.

---

## Limite mensal e expiração

* Cada usuário possui limite mensal de análises.
* O limite atual é de 30 análises por mês.
* As análises ficam disponíveis no histórico por 15 dias.
* Após o prazo, deixam de aparecer para o usuário.
* Ao descartar uma análise, ela sai do histórico do usuário, mas o limite mensal utilizado não é restaurado.
* O descarte é feito por soft delete, preservando o registro no banco para fins de controle e acompanhamento.

---

## Banco de dados

O projeto utiliza Supabase para autenticação, persistência de dados e controle de acesso.

Principais tabelas:

```text
profiles
analyses
admin_users
```

A tabela `profiles` armazena os dados cadastrais do usuário.

A tabela `analyses` armazena os dados estruturados das análises.

A tabela `admin_users` define quais usuários possuem acesso administrativo.

Campos principais da tabela `analyses`:

```text
id
user_id
title
video_name
input_type
score
transcription
report_json
ai_available
created_at
expires_at
status
```

O campo `input_type` identifica a origem da análise:

```text
audio
video
text
```

Em análises por áudio, o valor de referência salvo em `video_name` é:

```text
audio_recording
```

Em análises por texto, o valor de referência salvo em `video_name` é:

```text
text_input
```

As políticas de RLS garantem que cada usuário acesse apenas seus próprios dados.

Administradores podem visualizar perfis e análises de todos os usuários em modo somente leitura.

---

## Supabase Storage

O projeto utiliza Supabase Storage para armazenar fotos de perfil.

Bucket utilizado:

```text
profile-images
```

Cada usuário só pode inserir, atualizar, visualizar e remover arquivos dentro da própria pasta no bucket.

Os arquivos de áudio e vídeo não são enviados para o Supabase Storage.

---

## Painel administrativo

O sistema possui um painel administrativo somente leitura.

O administrador pode:

* Visualizar usuários cadastrados.
* Visualizar perfis.
* Visualizar análises.
* Filtrar análises por usuário.
* Filtrar análises por tipo.
* Abrir detalhes de uma análise.
* Baixar relatório DOCX.

O administrador não pode:

* Editar dados de usuários comuns.
* Excluir usuários.
* Excluir análises.
* Alterar relatórios.
* Tornar outros usuários administradores pelo app.

O cadastro de administradores deve ser feito manualmente no Supabase, por meio da tabela:

```text
admin_users
```

---

## Relatório DOCX

O sistema gera relatórios editáveis em DOCX.

### Relatório de áudio e vídeo

Contém:

* Score geral.
* Classificação.
* Resumo da análise.
* Recomendações.
* Pontos de atenção.
* Pausas e ritmo.
* Repetições e termos recorrentes.
* Transcrição.
* Espaço para observações de revisão humana.

### Relatório de texto

Contém:

* Score textual.
* Classificação.
* Correção textual.
* Principais correções.
* Avaliação textual.
* Análise geral.
* Recomendações.
* Texto original enviado.
* Espaço para observações de revisão humana.

---

## Documentação do banco

A documentação específica do Supabase fica em:

```text
docs/database/
```

Arquivos principais:

```text
docs/database/supabase_setup.sql
docs/database/supabase_checks.sql
docs/database/README.md
```

O arquivo `supabase_setup.sql` documenta a estrutura principal do banco, tabelas, colunas, policies, função administrativa, índices e Storage.

O arquivo `supabase_checks.sql` contém consultas de auditoria para validar tabelas, policies, perfis, análises, tipos de entrada, expiração, administradores e Storage.

---

## Comandos úteis

Rodar aplicação:

```bash
python -m streamlit run app/main.py
```

Rodar aplicação simulando o comando do Streamlit Cloud:

```bash
streamlit run app/main.py
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

Atualizar lock de dependências:

```bash
pip freeze > requirements-lock.txt
```

Limpar arquivos temporários manualmente:

```bash
find data/input data/temp -type f ! -name ".gitkeep" -delete
```

Remover caches Python:

```bash
find app -type d -name "__pycache__" -prune -exec rm -rf {} +
```

Verificar erros de compilação:

```bash
python -m compileall app
```

Ver status do Git:

```bash
git status
```

Commit padrão:

```bash
git add .
git commit -m "Mensagem do commit"
git push origin main
```

---

## Status do projeto

Projeto em fase de MVP funcional.

Funcionalidades já implementadas:

* Autenticação de usuários.
* Cadastro de perfil.
* Upload de foto de perfil.
* Análise por áudio.
* Análise por vídeo na versão local.
* Análise por texto.
* Score oral.
* Score textual.
* Histórico de análises.
* Relatórios DOCX.
* Controle mensal de análises.
* Expiração automática.
* Descarte por soft delete.
* Painel administrativo somente leitura.
* Deploy web no Streamlit Cloud.

---

## Próximas etapas

* Criar aviso simples de privacidade na interface.
* Preparar checklist final de testes do MVP.
* Otimizar custos e uso de tokens da IA.
* Melhorar monitoramento e logs.
* Revisar responsividade em dispositivos móveis.
* Criar tag de versão do MVP.