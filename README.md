# TopSaudeHub Case técnico

A stack escolhida foi:
- Front-end:
    - Angular
    - Typescript
    - Tailwind
    - PrimeNG (componentes semi-prontos)
- Back-end:
  - Python - FastAPI
  - SQLAlchemy
  - Alembic (+ Faker para gerar dados)

Para executar o projeto, basta executar o comando:

```bash
docker compose up -d
```

Ao executar o projeto, é gerado o banco de dados, com dados para testes.

O front-end roda em http://localhost:4200/ e o backend em http://localhost:8000/


Para rodar os testes, basta executar o comando:


```bash
docker compose run --rm tests
```

# Regras

Produto:
  - SKU deve ser no formato AAA-000
  - SKU e nome devem ser unicos

Cliente:
  - Documento deve ter entre 11 e 14 digitos (CPF ou CNPJ)
  - Nome, e-mail e documento devem ser unicos

Pedidos:
  - Dentro de um pedido apenas 1 item de cada tipo pode ser preenchido
  - Um pedido não pode ser salvo 2 vezes durante a execução (idempotencia)

Durante o desenvolvimento foi utilizado IA para sanar algumas dúvidas e para sugestões de melhorias em estrutura. 