# typos-gitlab-code-quality

Generate [GitLab Code Quality report](https://docs.gitlab.com/ci/testing/code_quality/)
from [typos](https://github.com/crate-ci/typos)
output.

## Usage

Read from **stdin**:

```console
$ typos --format json | typos-gitlab-code-quality
```

Read from **file**:

```console
$ typos --format json > typos-report.json
$ typos-gitlab-code-quality typos-report.json
```

## Example `.gitlab-ci.yml`

With pip:

```yaml
typos:
  image: python:alpine
  script:
    - pip install typos typos-gitlab-code-quality
    # "|| true" is used for preventing job fail when typos find errors
    - typos --format json > typos-report.json || true
    - typos-gitlab-code-quality < typos-report.json > codequality.json
  artifacts:
    when: always
    reports:
      codequality: codequality.json
```

With [uv](https://docs.astral.sh/uv/guides/integration/gitlab/):

```yaml
typos:
  image: ghcr.io/astral-sh/uv:python3.14-alpine
  script:
    # "|| true" is used for preventing job fail when typos find errors
    - uvx typos --format json > typos-report.json || true
    - uvx typos-gitlab-code-quality < typos-report.json > codequality.json
  artifacts:
    when: always
    reports:
      codequality: codequality.json
```

<!-- ## Contributing -->

## Acknowledgements

This project is inspired by
[mypy-gitlab-code-quality](https://pypi.org/project/mypy-gitlab-code-quality/).
