-- =========================================================
-- 01 - Supabase Setup - Projeto Imersão
-- =========================================================
-- Script principal de estrutura do banco Supabase.
-- Contém tabelas, colunas, constraints, RLS, policies,
-- função administrativa, índices e Storage.
--
-- ATENÇÃO:
-- Este script deve ser usado como referência ou migração controlada.
-- Não execute em produção sem revisar antes.
-- =========================================================


-- Supabase setup - Projeto Análise de Comunicação
-- Este arquivo documenta a estrutura principal do banco, policies RLS, admins e Storage.
-- Não execute novamente em produção sem revisar o estado atual do banco.


-- =========================
-- Tabela: profiles
-- =========================

CREATE TABLE IF NOT EXISTS public.profiles (
    id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name text NOT NULL,
    birth_date date NOT NULL,
    cpf text NOT NULL,
    phone text NOT NULL,
    cep text NOT NULL,
    street text,
    number text,
    neighborhood text,
    city text,
    state text,
    created_at timestamptz DEFAULT now(),
    avatar_url text
);

ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS full_name text,
ADD COLUMN IF NOT EXISTS birth_date date,
ADD COLUMN IF NOT EXISTS avatar_url text;

-- Migração defensiva para bancos antigos que ainda possuíam first_name e last_name.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'profiles'
        AND column_name = 'first_name'
    )
    AND EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'profiles'
        AND column_name = 'last_name'
    ) THEN
        EXECUTE '
            UPDATE public.profiles
            SET full_name = trim(concat_ws('' '', first_name, last_name))
            WHERE full_name IS NULL
               OR trim(full_name) = ''''
        ';
    END IF;
END $$;

ALTER TABLE public.profiles
DROP COLUMN IF EXISTS first_name,
DROP COLUMN IF EXISTS last_name;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'profiles_birth_date_not_future_check'
    ) THEN
        ALTER TABLE public.profiles
        ADD CONSTRAINT profiles_birth_date_not_future_check
        CHECK (
            birth_date <= CURRENT_DATE
        );
    END IF;
END $$;

ALTER TABLE public.profiles
ALTER COLUMN full_name SET NOT NULL;

ALTER TABLE public.profiles
ALTER COLUMN birth_date SET NOT NULL;

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own profile"
ON public.profiles;

CREATE POLICY "Users can view their own profile"
ON public.profiles
FOR SELECT
USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert their own profile"
ON public.profiles;

CREATE POLICY "Users can insert their own profile"
ON public.profiles
FOR INSERT
WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update their own profile"
ON public.profiles;

CREATE POLICY "Users can update their own profile"
ON public.profiles
FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);


-- =========================
-- Tabela: analyses
-- =========================

-- input_type pode ser:
-- audio = áudio gravado pelo navegador
-- video = vídeo enviado na versão local
-- text = texto digitado pelo usuário

CREATE TABLE IF NOT EXISTS public.analyses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title text,
    video_name text,
    input_type text DEFAULT 'video',
    score integer,
    transcription text,
    report_json jsonb,
    ai_available boolean,
    created_at timestamptz DEFAULT now(),
    expires_at timestamptz,
    status text DEFAULT 'active'
);

ALTER TABLE public.analyses
ADD COLUMN IF NOT EXISTS expires_at timestamptz,
ADD COLUMN IF NOT EXISTS status text DEFAULT 'active',
ADD COLUMN IF NOT EXISTS input_type text DEFAULT 'video';

UPDATE public.analyses
SET expires_at = created_at + interval '15 days'
WHERE expires_at IS NULL;

UPDATE public.analyses
SET input_type = 'video'
WHERE input_type IS NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'analyses_input_type_check'
    ) THEN
        ALTER TABLE public.analyses
        ADD CONSTRAINT analyses_input_type_check
        CHECK (input_type IN ('audio', 'video', 'text'));
    END IF;
END $$;

ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own analyses"
ON public.analyses;

CREATE POLICY "Users can view their own analyses"
ON public.analyses
FOR SELECT
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own analyses"
ON public.analyses;

CREATE POLICY "Users can insert their own analyses"
ON public.analyses
FOR INSERT
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own analyses"
ON public.analyses;

CREATE POLICY "Users can update their own analyses"
ON public.analyses
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own analyses"
ON public.analyses;

CREATE POLICY "Users can delete their own analyses"
ON public.analyses
FOR DELETE
USING (auth.uid() = user_id);


-- =========================
-- Tabela: admin_users
-- =========================

-- Esta tabela define quais usuários possuem acesso administrativo.
-- O cadastro de administradores deve ser feito manualmente pelo Supabase.
-- O app não deve permitir que usuários comuns se tornem administradores.

CREATE TABLE IF NOT EXISTS public.admin_users (
    id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at timestamptz DEFAULT now(),
    notes text
);

ALTER TABLE public.admin_users ENABLE ROW LEVEL SECURITY;


-- =========================
-- Função: is_admin
-- =========================

-- Função usada pelas policies e pelo app para verificar se o usuário autenticado é admin.

CREATE OR REPLACE FUNCTION public.is_admin(user_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.admin_users
        WHERE id = user_id
    );
$$;

GRANT EXECUTE ON FUNCTION public.is_admin(uuid) TO authenticated;


-- =========================
-- Policies: admin_users
-- =========================

DROP POLICY IF EXISTS "Users can view own admin status"
ON public.admin_users;

CREATE POLICY "Users can view own admin status"
ON public.admin_users
FOR SELECT
TO authenticated
USING (
    auth.uid() = id
);

DROP POLICY IF EXISTS "Admins can view admin users"
ON public.admin_users;

CREATE POLICY "Admins can view admin users"
ON public.admin_users
FOR SELECT
TO authenticated
USING (
    public.is_admin(auth.uid())
);


-- =========================
-- Policies administrativas somente leitura
-- =========================

-- Admins podem visualizar todos os perfis.
-- Não há policies administrativas para INSERT, UPDATE ou DELETE.

DROP POLICY IF EXISTS "Admins can view all profiles"
ON public.profiles;

CREATE POLICY "Admins can view all profiles"
ON public.profiles
FOR SELECT
TO authenticated
USING (
    public.is_admin(auth.uid())
);

-- Admins podem visualizar todas as análises.
-- Não há policies administrativas para INSERT, UPDATE ou DELETE.

DROP POLICY IF EXISTS "Admins can view all analyses"
ON public.analyses;

CREATE POLICY "Admins can view all analyses"
ON public.analyses
FOR SELECT
TO authenticated
USING (
    public.is_admin(auth.uid())
);


-- =========================
-- Índices recomendados
-- =========================

CREATE INDEX IF NOT EXISTS idx_analyses_user_created
ON public.analyses(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_analyses_user_status_expiration
ON public.analyses(user_id, status, expires_at);

CREATE INDEX IF NOT EXISTS idx_analyses_user_input_type
ON public.analyses(user_id, input_type);

CREATE INDEX IF NOT EXISTS idx_profiles_full_name
ON public.profiles(full_name);


-- =========================
-- Supabase Storage: profile-images
-- =========================

-- Bucket utilizado para fotos de perfil.
-- O bucket deve ser criado manualmente no Supabase Storage com o nome:
-- profile-images
--
-- Configuração recomendada:
-- Public bucket: ON
-- Allowed MIME types: image/png, image/jpeg, image/webp
-- File size limit recomendado: 5 MB

-- Remove policy pública ampla de listagem, caso exista.
-- O bucket pode ser público para exibir imagens via URL pública,
-- mas a listagem de objetos deve ficar restrita.

DROP POLICY IF EXISTS "Public can view profile images"
ON storage.objects;

DROP POLICY IF EXISTS "Users can view their own profile image objects"
ON storage.objects;

CREATE POLICY "Users can view their own profile image objects"
ON storage.objects
FOR SELECT
TO authenticated
USING (
    bucket_id = 'profile-images'
    AND auth.uid()::text = (storage.foldername(name))[1]
);

DROP POLICY IF EXISTS "Users can upload their own profile image"
ON storage.objects;

CREATE POLICY "Users can upload their own profile image"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'profile-images'
    AND auth.uid()::text = (storage.foldername(name))[1]
);

DROP POLICY IF EXISTS "Users can update their own profile image"
ON storage.objects;

CREATE POLICY "Users can update their own profile image"
ON storage.objects
FOR UPDATE
TO authenticated
USING (
    bucket_id = 'profile-images'
    AND auth.uid()::text = (storage.foldername(name))[1]
)
WITH CHECK (
    bucket_id = 'profile-images'
    AND auth.uid()::text = (storage.foldername(name))[1]
);

DROP POLICY IF EXISTS "Users can delete their own profile image"
ON storage.objects;

CREATE POLICY "Users can delete their own profile image"
ON storage.objects
FOR DELETE
TO authenticated
USING (
    bucket_id = 'profile-images'
    AND auth.uid()::text = (storage.foldername(name))[1]
);