<#
.SYNOPSIS
    Windows entrypoint for scripts/lib/benchmark.py. See that file for
    what it measures.

.PARAMETER Runs
    Number of requests to average over. Default 3.

.PARAMETER MaxTokens
    max_tokens per request. Default 200.

.EXAMPLE
    ./scripts/benchmark.ps1
.EXAMPLE
    ./scripts/benchmark.ps1 -Runs 5 -MaxTokens 400
#>

param(
    [int]$Runs = 3,
    [int]$MaxTokens = 200
)

$ErrorActionPreference = "Stop"
python "$PSScriptRoot\lib\benchmark.py" --runs $Runs --max-tokens $MaxTokens
exit $LASTEXITCODE
