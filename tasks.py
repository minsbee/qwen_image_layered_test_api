import sys
from invoke import task

# 윈도우 환경에서는 가상 터미널 기능이 제공되지 않으므로 플랫폼 검사 후 윈도우인 경우 가상환경 설정 꺼줘야 됨
is_windows = True if sys.platform.startswith("win") else False


@task
def dev(c):
    c.run(
        "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --env-file .env.dev",
        pty=is_windows,
    )


@task
def start(c):
    c.run(
        "uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env",
        pty=False,
    )


@task
def lint(c):
    c.run("ruff check .", pty=is_windows)


@task
def format(c):
    c.run("ruff format .", pty=is_windows)


@task
def test(c):
    c.run("pytest", pty=is_windows)
