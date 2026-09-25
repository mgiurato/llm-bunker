<#
.SYNOPSIS
    Windows entrypoint for scripts/lib/verify.py. See that file for the
    full checklist (container health, model loaded, inference, network
    isolation, non-root execution).

.EXAMPLE
    ./scripts/verify.ps1
#>

$ErrorActionPreference = "Stop"
python "$PSScriptRoot\lib\verify.py" @args
exit $LASTEXITCODE
