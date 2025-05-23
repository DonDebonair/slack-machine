import nox

nox.options.default_venv_backend = "uv"


def _install_deps(session: nox.Session):
    session.run_install(
        "uv",
        "sync",
        f"--python={session.python}",
        "--group=dev",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )


@nox.session(python=["3.9", "3.10", "3.11", "3.12", "3.13"])
def test(session: nox.Session):
    _install_deps(session)
    session.run("pytest")


@nox.session(python="3.13")
def lint(session: nox.Session):
    session.install("ruff")
    session.run("ruff", "check")


@nox.session(python="3.13")
def check_format(session: nox.Session):
    session.install("ruff")
    session.run("ruff", "format", "--check")


@nox.session(python="3.13")
def mypy(session: nox.Session):
    _install_deps(session)
    session.run("mypy", "src/machine")
