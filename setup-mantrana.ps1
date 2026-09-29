# setup-mantrana.ps1
# Creates the mantrana project file tree structure.
# Run from: D:\puneet\Projects\
# Usage: .\setup-mantrana.ps1

$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Base path — change if you want a different root
# ---------------------------------------------------------------------------
$Root = Join-Path (Get-Location) 'mantrana'

Write-Host "Creating project tree at: $Root" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# Files to create (relative paths). Directories are inferred from the paths.
# ---------------------------------------------------------------------------
$files = @(
    # .github
    '.github/workflows/ci.yml'
    '.github/workflows/security.yml'
    '.github/workflows/docs.yml'
    '.github/ISSUE_TEMPLATE/bug_report.yml'
    '.github/ISSUE_TEMPLATE/feature_request.yml'
    '.github/ISSUE_TEMPLATE/config.yml'
    '.github/PULL_REQUEST_TEMPLATE.md'
    '.github/CODEOWNERS'
    '.github/dependabot.yml'
    '.github/SECURITY.md'

    # config
    'config/council.yaml'
    'config/models.yaml'
    'config/sites/deepseek.yaml'

    # prompts
    'prompts/role_catalog.md'
    'prompts/moderator.md'
    'prompts/roles/sme.md'
    'prompts/roles/architect.md'
    'prompts/roles/critic.md'
    'prompts/roles/coder.md'

    # src/mantrana
    'src/mantrana/__init__.py'
    'src/mantrana/config.py'
    'src/mantrana/log.py'
    'src/mantrana/router.py'
    'src/mantrana/agents.py'
    'src/mantrana/orchestrator.py'
    'src/mantrana/clients/__init__.py'
    'src/mantrana/clients/base.py'
    'src/mantrana/clients/fake.py'

    # tests
    'tests/test_router.py'
    'tests/test_log.py'
    'tests/test_orchestrator.py'

    # docs
    'docs/index.md'
    'docs/architecture.md'
    'docs/phases.md'
    'docs/contributing.md'

    # root files
    '.pre-commit-config.yaml'
    '.gitignore'
    '.editorconfig'
    'pyproject.toml'
    'README.md'
    'CONTRIBUTING.md'
    'CODE_OF_CONDUCT.md'
    'LICENSE'
    'CHANGELOG.md'
    'mkdocs.yml'
)

# ---------------------------------------------------------------------------
# Create directory structure and empty files
# ---------------------------------------------------------------------------
foreach ($relative in $files) {
    $fullPath = Join-Path $Root $relative
    $dir      = Split-Path -Parent $fullPath

    if (-not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    if (-not (Test-Path -LiteralPath $fullPath)) {
        New-Item -ItemType File -Path $fullPath -Force | Out-Null
    }
}

# ---------------------------------------------------------------------------
# Optional: ensure Python packages have __init__.py markers (already listed)
# ---------------------------------------------------------------------------
Write-Host "`nDone. File tree:" -ForegroundColor Green
Get-ChildItem -Path $Root -Recurse -Force |
    Where-Object { $_.FullName -notmatch '\\\.git\\' } |
    ForEach-Object {
        $rel = $_.FullName.Substring($Root.Length).TrimStart('\')
        if ($_.PSIsContainer) {
            Write-Host "  [DIR ] $rel" -ForegroundColor Yellow
        } else {
            Write-Host "  [FILE] $rel"
        }
    }