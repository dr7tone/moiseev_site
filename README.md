# moiseev_site

Личный сайт-портфолио Александра Моисеева. Статический сайт на HTML/CSS, который публикуется на GitHub Pages.

[![Deploy static site](https://github.com/dr7tone/moiseev_site/actions/workflows/deploy.yml/badge.svg?branch=master)](https://github.com/dr7tone/moiseev_site/actions/workflows/deploy.yml)

## CI/CD

При каждом push в ветку `master` GitHub Actions:

1. выполняет линтинг HTML (htmlhint) в job `lint`;
2. публикует сайт на GitHub Pages в job `deploy` (actions/deploy-pages).

Workflow: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

Сайт: https://dr7tone.github.io/moiseev_site/
