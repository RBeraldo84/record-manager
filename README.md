# Record Manager

Databricks App para manutenção controlada de registros em uma Delta Table do Unity Catalog.

## Tabelas

- `raw_db.default.app_records`
- `raw_db.default.app_audit`

## Funcionalidades previstas

- Consulta e busca de registros
- INSERT
- UPDATE
- DELETE
- Identificação automática do usuário
- Auditoria de operações
- Identidade visual corporativa inspirada na B3

## Estrutura

```text
record-manager/
├── app.py
├── app.yaml
├── config.py
├── requirements.txt
├── repositories/
│   ├── audit_repository.py
│   └── records_repository.py
├── services/
│   ├── __init__.py
│   ├── database.py
│   └── records.py
├── ui/
│   ├── __init__.py
│   └── components.py
└── assets/
    └── style.css
```

## Configuração

O App espera a variável `DATABRICKS_WAREHOUSE_ID`, preferencialmente fornecida por um recurso de SQL Warehouse configurado no Databricks App.

As tabelas de destino são configuradas em `app.yaml`.

Para execução local, copie `.env.example` para `.env` e preencha:

- `DATABRICKS_CONFIG_PROFILE`
- `DATABRICKS_WAREHOUSE_ID`
- `TARGET_CATALOG`
- `TARGET_SCHEMA`
- `TARGET_TABLE`
- `AUDIT_TABLE`

Não versione `.env` nem arquivos gerados em `.databricks/`.

## Camadas

- `app.py`: orquestra a tela Streamlit.
- `ui/`: componentes e helpers de apresentação.
- `services/`: regras de negócio e coordenação de operações.
- `repositories/`: SQL e persistência.
- `config.py`: variáveis de ambiente e nomes qualificados do Unity Catalog.
