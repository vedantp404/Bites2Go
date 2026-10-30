-- Stage 9 development foundation. Apply only to a reviewed Supabase development project.
begin;
create table public.diary_records (
  owner_id uuid not null references auth.users(id) on delete cascade,
  record_id text not null check (record_id ~ '^[a-zA-Z0-9:-]{1,120}$'),
  revision integer not null check (revision > 0),
  payload jsonb,
  updated_at timestamptz not null default now(),
  primary key (owner_id, record_id),
  constraint diary_payload_shape check (payload is null or (
    jsonb_typeof(payload) = 'object' and payload ? 'id'
    and jsonb_typeof(payload->'id') = 'string' and payload->>'id' = record_id
    and octet_length(payload::text) <= 32768
  ))
);
comment on column public.diary_records.payload is 'Version-1 diary snapshot; SQL NULL is a retained deletion tombstone. Client validates full nutrition semantics before applying.';
alter table public.diary_records enable row level security;
alter table public.diary_records force row level security;
revoke all on public.diary_records from public, anon, authenticated;
grant select on public.diary_records to authenticated;
create policy diary_select_own on public.diary_records for select to authenticated
  using ((select auth.uid()) = owner_id);
-- No direct INSERT/UPDATE/DELETE policy or grant: all mutations use the scoped CAS RPC.
create function public.put_diary(p_id text, p_expected_revision integer, p_payload jsonb)
returns public.diary_records
language plpgsql security definer set search_path = '' as $$
declare
  actor uuid := auth.uid();
  current_row public.diary_records;
  saved public.diary_records;
begin
  if actor is null then raise exception 'Authentication required' using errcode = '28000'; end if;
  if p_id is null or p_id !~ '^[a-zA-Z0-9:-]{1,120}$' or p_expected_revision is null or p_expected_revision < 0 then
    raise exception 'Invalid sync request' using errcode = '22023';
  end if;
  -- Serialize first inserts as well as updates; lock is account + record scoped.
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(actor::text || ':' || p_id, 0));
  select * into current_row from public.diary_records where owner_id = actor and record_id = p_id for update;
  if found then
    if p_expected_revision > current_row.revision then raise exception 'Revision conflict' using errcode = '40001'; end if;
    if current_row.payload is not distinct from p_payload then return current_row; end if;
    if current_row.revision <> p_expected_revision then raise exception 'Revision conflict' using errcode = '40001'; end if;
    update public.diary_records set payload = p_payload, revision = revision + 1, updated_at = clock_timestamp()
      where owner_id = actor and record_id = p_id returning * into saved;
  else
    if p_expected_revision <> 0 then raise exception 'Revision conflict' using errcode = '40001'; end if;
    insert into public.diary_records(owner_id, record_id, revision, payload)
      values (actor, p_id, 1, p_payload) returning * into saved;
  end if;
  return saved;
end;
$$;
revoke all on function public.put_diary(text, integer, jsonb) from public, anon;
grant execute on function public.put_diary(text, integer, jsonb) to authenticated;
commit;
