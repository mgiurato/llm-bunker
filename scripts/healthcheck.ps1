<#
.SYNOPSIS
    Windows entrypoint for scripts/lib/healthcheck.py. See that file for
    what it actually checks.

.EXAMPLE
    ./scripts/healthcheck.ps1
#>

$ErrorActionPreference = "Stop"
python "$PSScriptRoot\lib\healthcheck.py" @args
exit $LASTEXITCODE
