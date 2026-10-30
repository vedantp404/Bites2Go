$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$pgBin = Split-Path (Get-Command psql -ErrorAction Stop).Source
$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('bites2go-pg-test-' + [guid]::NewGuid())
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
$listener.Start()
$testPort = $listener.LocalEndpoint.Port
$listener.Stop()
$started = $false
try {
  & (Join-Path $pgBin 'initdb.exe') -D $testRoot -U postgres -A trust --encoding=UTF8 --locale=C | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Disposable cluster initialization failed.' }
  & (Join-Path $pgBin 'pg_ctl.exe') -D $testRoot -l (Join-Path $testRoot 'server.log') -o "-h 127.0.0.1 -p $testPort" -w start
  if ($LASTEXITCODE -ne 0) { throw 'Disposable cluster startup failed.' }
  $started = $true
  foreach ($sql in @('supabase/tests/bootstrap-local.sql','supabase/migrations/202610300001_diary_sync.sql','supabase/tests/diary-access.sql')) {
    & (Join-Path $pgBin 'psql.exe') -X --host=127.0.0.1 --port=$testPort --username=postgres --dbname=postgres --set=ON_ERROR_STOP=1 -f (Join-Path $repoRoot $sql)
    if ($LASTEXITCODE -ne 0) { throw "SQL check failed: $sql" }
  }
} finally {
  if ($started) {
    & (Join-Path $pgBin 'pg_ctl.exe') -D $testRoot -m fast -w stop
    if ($LASTEXITCODE -ne 0) { throw "Test cluster stop failed; retained at $testRoot" }
  }
  $resolved = [System.IO.Path]::GetFullPath($testRoot)
  $temp = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
  if (-not $resolved.StartsWith($temp, [System.StringComparison]::OrdinalIgnoreCase) -or -not (Split-Path $resolved -Leaf).StartsWith('bites2go-pg-test-')) { throw 'Unsafe test cleanup path.' }
  if (Test-Path -LiteralPath $resolved) { Remove-Item -LiteralPath $resolved -Recurse -Force }
}
