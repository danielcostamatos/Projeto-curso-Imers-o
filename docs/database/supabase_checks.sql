-- Consultas úteis para auditoria do banco Supabase.


-- =========================
-- Estrutura das tabelas principais
-- =========================

SELECT
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN ('profiles', 'analyses', 'admin_users')
ORDER BY table_name, ordinal_position;


-- =========================
-- Conferir se campos antigos foram removidos
-- =========================

SELECT
    column_name
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'profiles'
AND column_name IN ('first_name', 'last_name');


-- Resultado esperado:
-- Nenhuma linha retornada.


-- =========================
-- Conferir campos atuais do perfil
-- =========================

SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'profiles'
AND column_name IN (
    'id',
    'full_name',
    'birth_date',
    'cpf',
    'phone',
    'cep',
    'street',
    'number',
    'neighborhood',
    'city',
    'state',
    'avatar_url',
    'created_at'
)
ORDER BY ordinal_position;


-- =========================
-- Perfis com dados obrigatórios ausentes
-- =========================

SELECT
    COUNT(*) AS profiles_with_missing_required_data
FROM public.profiles
WHERE full_name IS NULL
   OR trim(full_name) = ''
   OR birth_date IS NULL
   OR cpf IS NULL
   OR trim(cpf) = ''
   OR phone IS NULL
   OR trim(phone) = ''
   OR cep IS NULL
   OR trim(cep) = '';


-- =========================
-- Perfis com data de nascimento futura
-- =========================

SELECT
    id,
    full_name,
    birth_date
FROM public.profiles
WHERE birth_date > CURRENT_DATE;


-- =========================
-- Últimos perfis cadastrados
-- =========================

SELECT
    p.id,
    u.email,
    p.full_name,
    p.birth_date,
    p.city,
    p.state,
    p.avatar_url,
    p.created_at
FROM public.profiles p
JOIN auth.users u ON u.id = p.id
ORDER BY p.created_at DESC
LIMIT 10;


-- =========================
-- Policies RLS
-- =========================

SELECT
    schemaname,
    tablename,
    policyname,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
AND tablename IN ('profiles', 'analyses', 'admin_users')
ORDER BY tablename, policyname;


-- =========================
-- Função administrativa
-- =========================

SELECT
    routine_schema,
    routine_name,
    routine_type,
    data_type
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name = 'is_admin';


-- =========================
-- Administradores cadastrados
-- =========================

SELECT
    au.id,
    u.email,
    au.created_at,
    au.notes
FROM public.admin_users au
JOIN auth.users u ON u.id = au.id
ORDER BY au.created_at DESC;


-- =========================
-- Policies administrativas somente leitura
-- =========================

SELECT
    schemaname,
    tablename,
    policyname,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
AND policyname IN (
    'Admins can view all profiles',
    'Admins can view all analyses',
    'Admins can view admin users'
)
ORDER BY tablename, policyname;


-- =========================
-- Quantidade de análises por status
-- =========================

SELECT
    status,
    COUNT(*) AS total
FROM public.analyses
GROUP BY status
ORDER BY status;


-- =========================
-- Quantidade de análises por tipo de entrada
-- =========================

SELECT
    input_type,
    COUNT(*) AS total
FROM public.analyses
GROUP BY input_type
ORDER BY input_type;


-- =========================
-- Quantidade de análises por status e tipo
-- =========================

SELECT
    status,
    input_type,
    COUNT(*) AS total
FROM public.analyses
GROUP BY status, input_type
ORDER BY status, input_type;


-- =========================
-- Análises sem data de expiração
-- =========================

SELECT
    COUNT(*) AS analyses_without_expiration
FROM public.analyses
WHERE expires_at IS NULL;


-- =========================
-- Análises com tipo inválido
-- =========================

SELECT
    id,
    user_id,
    title,
    input_type,
    created_at
FROM public.analyses
WHERE input_type NOT IN ('audio', 'video')
   OR input_type IS NULL;


-- =========================
-- Verificação de possíveis caminhos temporários de áudio bruto salvos por engano
-- =========================

SELECT
    COUNT(*) AS analyses_with_raw_audio_temp_reference
FROM public.analyses
WHERE video_name ILIKE '%recorded_audio_%'
   OR video_name ILIKE '%data/temp%'
   OR video_name ILIKE '%data\\temp%';


-- =========================
-- Últimas análises registradas
-- =========================

SELECT
    id,
    user_id,
    title,
    video_name,
    input_type,
    score,
    ai_available,
    created_at,
    expires_at,
    status
FROM public.analyses
ORDER BY created_at DESC
LIMIT 10;


-- =========================
-- Policies do Storage para fotos de perfil
-- =========================

SELECT
    schemaname,
    tablename,
    policyname,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'storage'
AND tablename = 'objects'
AND policyname IN (
    'Users can view their own profile image objects',
    'Users can upload their own profile image',
    'Users can update their own profile image',
    'Users can delete their own profile image'
)
ORDER BY policyname;