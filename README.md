# API Orçamentos Cirurgia Já

API simples para buscar a URL da imagem de orçamento por nome do procedimento.

## Endpoints

### Health
GET `/`
Retorna status da API.

### Buscar orçamento por nome
GET `/orcamento?nome=Hemorroida`

Opcional:
- `&exato=1` para busca case-sensitive.

Resposta:
```json
{ "nome": "Hemorroida", "imagem_url": "https://..." }
```

### Verificar se existe
GET `/orcamento/existe?nome=Hemorroida`

### Listar todos (admin/teste)
GET `/orcamentos`

## Rodar com Docker Compose

1) Copie `.env.example` para `.env` e ajuste.
2) Suba:
```bash
docker compose up -d --build
```

A API ficará em:
- http://SEU_IP:5023
