# Banco de dados - Supabase

Esta pasta documenta a estrutura do banco Supabase usado no projeto Análise de Comunicação.

## Arquivos

### `supabase_setup.sql`

Contém a estrutura principal das tabelas, colunas, policies RLS, função administrativa, índices recomendados e configuração documentada do Supabase Storage.

Inclui:

* Tabela `profiles`
* Tabela `analyses`
* Tabela `admin_users`
* Função `public.is_admin`
* Colunas de expiração, status e tipo de entrada da análise
* Policies de acesso por usuário
* Policies administrativas somente leitura
* Índices úteis para histórico, consultas por usuário e perfis
* Policies do Supabase Storage para fotos de perfil

### `supabase_checks.sql`

Contém consultas de auditoria para verificar:

* Estrutura das tabelas
* Remoção dos campos antigos `first_name` e `last_name`
* Campos atuais de perfil, como `full_name` e `birth_date`
* Perfis com dados obrigatórios ausentes
* Policies RLS
* Função administrativa `public.is_admin`
* Administradores cadastrados
* Quantidade de análises por status
* Quantidade de análises por tipo de entrada
* Análises sem expiração
* Últimas análises registradas
* Policies do Supabase Storage

## Regras atuais do produto

* Cada usuário acessa apenas seus próprios dados.
* Administradores podem visualizar perfis e análises de todos os usuários em modo somente leitura.
* Administradores não possuem permissões administrativas de criação, edição ou exclusão de dados de usuários comuns pelo app.
* Vídeos não são salvos no banco de dados.
* Áudios gravados na versão web não são salvos no banco de dados.
* O banco salva apenas relatórios, transcrições, scores e metadados.
* Análises possuem `status`.
* `active`: análise disponível.
* `deleted`: análise descartada pelo usuário.
* O descarte é feito por soft delete.
* Análises descartadas não aparecem no histórico do usuário comum.
* O limite mensal não é restaurado ao descartar uma análise.
* As análises expiram após 15 dias.
* Cada análise possui um `input_type`, indicando se foi feita por áudio ou vídeo.

## Tabelas principais

### `profiles`

Armazena os dados cadastrais do usuário.

Campos principais:

* `id`
* `full_name`
* `birth_date`
* `cpf`
* `phone`
* `cep`
* `street`
* `number`
* `neighborhood`
* `city`
* `state`
* `avatar_url`
* `created_at`

O campo `full_name` armazena o nome completo do usuário.

O campo `birth_date` armazena a data de nascimento do usuário no formato de data do banco.

Os campos antigos `first_name` e `last_name` foram removidos do modelo atual. O cadastro e a edição de perfil usam apenas `full_name`.

O campo `avatar_url` armazena a URL pública da foto de perfil salva no Supabase Storage.

### `analyses`

Armazena os dados estruturados das análises realizadas.

Campos principais:

* `id`
* `user_id`
* `title`
* `video_name`
* `input_type`
* `score`
* `transcription`
* `report_json`
* `ai_available`
* `created_at`
* `expires_at`
* `status`

A coluna `video_name` guarda apenas uma referência textual ao insumo usado na análise. Em análises por vídeo, pode indicar o nome/caminho temporário do arquivo utilizado. Em análises por áudio gravado na versão web, o valor salvo deve ser `audio_recording`.

O conteúdo bruto original, seja áudio ou vídeo, não é salvo no banco de dados.

O campo `input_type` identifica a origem da análise:

* `audio`: análise feita a partir de áudio gravado na versão web.
* `video`: análise feita a partir de vídeo enviado na versão local.

### `admin_users`

Define quais usuários possuem acesso administrativo.

Campos principais:

* `id`
* `created_at`
* `notes`

O campo `id` referencia diretamente o usuário em `auth.users`.

O cadastro de administradores deve ser feito manualmente no Supabase. O app não deve permitir que usuários comuns se tornem administradores.

### `public.is_admin`

Função usada pelas policies e pelo app para verificar se um usuário autenticado possui acesso administrativo.

A função consulta a tabela `admin_users` e retorna verdadeiro quando o usuário informado está cadastrado como administrador.

## Supabase Storage

O projeto utiliza Supabase Storage para armazenar fotos de perfil.

Bucket utilizado:

```text
profile-images