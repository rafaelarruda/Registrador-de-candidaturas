# Rastreador de Candidaturas

API REST para registrar vagas, acompanhar o andamento das candidaturas e consultar o resumo do funil. O projeto usa Python, FastAPI, PostgreSQL e Docker Compose.

## Requisitos no Windows

- Docker Desktop instalado e aberto (com o backend WSL 2 habilitado).
- Git instalado.

Não é necessário instalar Python nem PostgreSQL no Windows para executar esta primeira versão: ambos rodam nos containers.

## Executar

Abra o PowerShell nesta pasta e rode:

```powershell
docker compose up --build
```

As credenciais locais já têm valores padrão no Compose. Se quiser personalizá-las, copie `.env.example` para `.env` e ajuste os valores antes de iniciar os containers.

Na primeira execução, o Docker baixa as imagens, aplica as migrações do banco e constrói a API. Quando os serviços estiverem prontos:

- Painel visual: <http://localhost:8000/>
- Documentação interativa: <http://localhost:8000/docs>
- Verificação da API: <http://localhost:8000/health>
- PostgreSQL: `localhost:5432`

Para encerrar, pressione `Ctrl+C`. Para iniciar novamente em segundo plano:

```powershell
docker compose up --build -d
```

Para parar os containers sem apagar os dados:

```powershell
docker compose down
```

Os dados ficam no volume Docker `postgres_data`. Para apagar os containers **e os dados salvos**, use `docker compose down -v`.

As migrações são aplicadas automaticamente quando o serviço da API inicia. Para gerar uma migração após alterar os modelos, com a API em execução, use:

```powershell
docker compose exec api alembic revision --autogenerate -m "descrever alteracao"
```

Revise o arquivo gerado em `migrations/versions/` antes de reiniciar a API.

## Endpoints

| Método | Caminho | O que faz |
|---|---|---|
| `POST` | `/api/candidaturas` | Cria uma candidatura |
| `GET` | `/api/candidaturas` | Lista candidaturas; aceita `status`, `empresa`, `limit` e `offset`; retorna a contagem filtrada em `X-Total-Count` |
| `GET` | `/api/candidaturas/{id}` | Consulta uma candidatura |
| `PATCH` | `/api/candidaturas/{id}` | Atualiza os campos enviados |
| `DELETE` | `/api/candidaturas/{id}` | Remove uma candidatura |
| `GET` | `/api/resumo` | Conta candidaturas por status |

Status aceitos: `enviado`, `entrevista`, `oferta` e `recusado`.

Exemplo de corpo para criar uma candidatura:

```json
{
  "empresa": "Empresa Exemplo",
  "cargo": "Desenvolvedor Python",
  "link": "https://example.com/vaga",
  "salario": "R$ 8.000–10.000 por mês",
  "requisitos": "Python, FastAPI e PostgreSQL",
  "status": "enviado",
  "anotacoes": "Vaga híbrida; candidatura enviada pelo site."
}
```

## Testes

Com Python instalado, instale as dependências de desenvolvimento e execute a suíte:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

Os testes usam um banco SQLite temporário e não precisam do Docker nem de um PostgreSQL em execução.

## Git

Se esta pasta ainda não for um repositório, inicialize o histórico:

```powershell
git init
git add .
git commit -m "Criar MVP do rastreador de candidaturas"
```

## Próximas etapas

A API, o painel visual, os testes automatizados e as migrações de banco estão configurados.
