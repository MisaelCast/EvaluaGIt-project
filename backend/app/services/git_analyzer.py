import git


MAX_COMMITS = 100


def analyze_git_history(repo_path: str, requirements: dict | None = None) -> dict:
    """Analiza el historial de commits del repositorio clonado."""
    repo = git.Repo(repo_path)
    commits = list(repo.iter_commits(max_count=MAX_COMMITS))

    total_commits = len(commits)

    authors = _get_unique_authors(commits)

    last_commit = _get_last_commit_info(commits[0] if commits else None)

    minimum = _evaluate_minimum_commits(requirements, total_commits)

    warnings = _build_warnings(minimum)

    return {
        "total_commits": total_commits,
        "minimum_commits": minimum,
        "authors": authors,
        "last_commit": last_commit,
        "warnings": warnings,
    }


def _get_unique_authors(commits: list) -> list[str]:
    authors_set = {c.author.name for c in commits}
    return sorted(authors_set)


def _get_last_commit_info(commit) -> dict:
    if not commit:
        return {
            "hash": "",
            "message": "",
            "author": "",
            "date": "",
        }

    return {
        "hash": commit.hexsha,
        "message": commit.message.strip().split("\n")[0],
        "author": commit.author.name,
        "date": commit.authored_datetime.isoformat(),
    }


def _evaluate_minimum_commits(requirements: dict | None, total_commits: int) -> dict:
    minimum = 0
    if requirements:
        raw = requirements.get("minimumCommits")
        if isinstance(raw, (int, float)) and raw > 0:
            minimum = int(raw)

    return {
        "required": minimum,
        "passed": total_commits >= minimum if minimum > 0 else True,
        "missing": max(minimum - total_commits, 0),
    }


def _build_warnings(minimum: dict) -> list[str]:
    warnings = []
    if minimum["required"] > 0 and not minimum["passed"]:
        warnings.append("El repositorio no cumple con el minimo de commits requerido")
    return warnings