-- Real PostgreSQL authorization/CAS checks with synthetic principals. Entire test rolls back.
begin;
set local role authenticated;
select set_config('request.jwt.claim.sub', '11111111-1111-1111-1111-111111111111', true);
do $$ declare r public.diary_records; begin
  r := public.put_diary('entry-a', 0, '{"id":"entry-a","test":"snapshot"}');
  if r.owner_id <> auth.uid() or r.revision <> 1 then raise exception 'owner/insert failed'; end if;
  r := public.put_diary('entry-a', 0, '{"test":"snapshot","id":"entry-a"}');
  if r.revision <> 1 then raise exception 'retry duplicated'; end if;
  r := public.put_diary('entry-a', 1, '{"id":"entry-a","test":"updated"}');
  if r.revision <> 2 then raise exception 'update failed'; end if;
  begin perform public.put_diary('entry-a', 0, '{"id":"entry-a","test":"stale"}'); raise exception 'stale write allowed'; exception when serialization_failure then null; end;
  begin perform public.put_diary('entry-a', 99, '{"id":"entry-a","test":"updated"}'); raise exception 'future revision allowed'; exception when serialization_failure then null; end;
  begin perform public.put_diary('entry-b', 0, '{"id":"wrong"}'); raise exception 'identity mismatch allowed'; exception when check_violation then null; end;
  begin perform public.put_diary('entry-b', 0, jsonb_build_object('id','entry-b','value',repeat('a',33000))); raise exception 'oversized payload allowed'; exception when check_violation then null; end;
end $$;
-- Owner B cannot read or mutate A, even with the same stable record ID.
select set_config('request.jwt.claim.sub', '22222222-2222-2222-2222-222222222222', true);
do $$ declare r public.diary_records; begin
  if exists(select 1 from public.diary_records) then raise exception 'cross-account read'; end if;
  r := public.put_diary('entry-a', 0, '{"id":"entry-a","test":"owner-b"}');
  if r.owner_id <> auth.uid() or r.revision <> 1 then raise exception 'cross-account overwrite'; end if;
  begin insert into public.diary_records values (auth.uid(), 'direct', 1, null, now()); raise exception 'direct insert allowed'; exception when insufficient_privilege then null; end;
  begin update public.diary_records set owner_id='11111111-1111-1111-1111-111111111111'; raise exception 'direct reassignment allowed'; exception when insufficient_privilege then null; end;
  begin delete from public.diary_records; raise exception 'hard deletion allowed'; exception when insufficient_privilege then null; end;
end $$;
select set_config('request.jwt.claim.sub', '11111111-1111-1111-1111-111111111111', true);
do $$ declare r public.diary_records; begin
  if (select count(*) from public.diary_records) <> 1 then raise exception 'owner visibility failed'; end if;
  if (select payload->>'test' from public.diary_records) <> 'updated' then raise exception 'owner A changed'; end if;
  r := public.put_diary('entry-a', 2, null);
  if r.revision <> 3 or r.payload is not null then raise exception 'tombstone failed'; end if;
  r := public.put_diary('entry-a', 2, null);
  if r.revision <> 3 then raise exception 'delete retry failed'; end if;
  begin perform public.put_diary('entry-a', 2, '{"id":"entry-a"}'); raise exception 'stale resurrection allowed'; exception when serialization_failure then null; end;
end $$;
select set_config('request.jwt.claim.sub', '', true);
do $$ begin
  if exists(select 1 from public.diary_records) then raise exception 'expired session read'; end if;
  begin perform public.put_diary('entry-c', 0, null); raise exception 'missing session write'; exception when invalid_authorization_specification then null; end;
end $$;
set local role anon;
do $$ begin
  begin perform * from public.diary_records; raise exception 'anonymous read'; exception when insufficient_privilege then null; end;
  begin perform public.put_diary('anon', 0, null); raise exception 'anonymous rpc'; exception when insufficient_privilege then null; end;
end $$;
reset role;
delete from auth.users where id='11111111-1111-1111-1111-111111111111';
do $$ begin
  if exists(select 1 from public.diary_records where owner_id='11111111-1111-1111-1111-111111111111') then raise exception 'account cascade failed'; end if;
  if (select count(*) from public.diary_records) <> 1 then raise exception 'other owner removed'; end if;
end $$;
rollback;
select 'PASS: ownership, anonymous denial, direct-write denial, CAS/retries, tombstones and account deletion' as result;
