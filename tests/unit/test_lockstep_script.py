import subprocess


def test_lockstep_passes_against_pinned_shas() -> None:
    r = subprocess.run(
        ["uv", "run", "python", "scripts/check_lockstep.py"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"lockstep drift:\n{r.stdout}\n{r.stderr}"
