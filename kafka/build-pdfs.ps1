$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$output = Join-Path $workspace 'output/pdf'
New-Item -ItemType Directory -Force -Path $output | Out-Null
$compiler = (Get-Command pdflatex -ErrorAction Stop).Source
$jobs = @(
    @{ Project = 'architecture'; Name = 'kafka-architecture'; Passes = 3 },
    @{ Project = 'architecture-quiz'; Name = 'kafka-architecture-quiz'; Passes = 2 },
    @{ Project = 'architecture-solution'; Name = 'kafka-architecture-solution'; Passes = 2 }
)
foreach ($job in $jobs) {
    $projectPath = Join-Path $PSScriptRoot $job.Project
    $buildPath = Join-Path $workspace ('tmp/pdfs/' + $job.Name + '-build')
    New-Item -ItemType Directory -Force -Path $buildPath | Out-Null
    Push-Location -LiteralPath $projectPath
    try {
        foreach ($pass in 1..$job.Passes) {
            $logPath = Join-Path $buildPath ("compile-pass{0}.txt" -f $pass)
            # pdflatex/MiKTeX writes warnings to stderr; rely on $LASTEXITCODE instead of treating stderr as fatal.
            $prevPref = $ErrorActionPreference
            $ErrorActionPreference = 'Continue'
            & $compiler '-interaction=nonstopmode' '-halt-on-error' '-file-line-error' "-output-directory=$buildPath" "-jobname=$($job.Name)" 'main.tex' *> $logPath
            $ErrorActionPreference = $prevPref
            if ($LASTEXITCODE -ne 0) {
                Get-Content -LiteralPath $logPath -Tail 35
                throw "Compilation failed for $($job.Name), pass $pass."
            }
        }
        $builtPdf = Join-Path $buildPath ($job.Name + '.pdf')
        Copy-Item -LiteralPath $builtPdf -Destination (Join-Path $output ($job.Name + '.pdf'))
        Write-Output ("Built {0}" -f $job.Name)
    }
    finally {
        Pop-Location
    }
}
$bundlePath = Join-Path $workspace 'output/kafka-architecture-latex.zip'
$bundleFiles = @(
    'architecture', 'architecture-quiz', 'architecture-solution', 'assets',
    'kafka-architecture.md', 'kafka-architecture-hands-on.md',
    'kafka-architecture-quiz.md', 'kafka-architecture-solution.md',
    'README.md', 'build-pdfs.ps1'
) | ForEach-Object { Join-Path $PSScriptRoot $_ }
Compress-Archive -LiteralPath $bundleFiles -DestinationPath $bundlePath -Force
Write-Output 'Packaged output/kafka-architecture-latex.zip'
