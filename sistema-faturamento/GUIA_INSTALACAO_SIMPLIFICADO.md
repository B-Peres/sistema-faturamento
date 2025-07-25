# 🚀 Sistema de Faturamento - Guia de Instalação Simplificado

## O que é este sistema?

Este é um **sistema web completo** para gestão de faturamento que roda no seu navegador. Você pode:

- ✅ Cadastrar clientes
- ✅ Criar cobranças (única, recorrente ou parcelada)
- ✅ Acompanhar pagamentos
- ✅ Ver dashboard financeiro
- ✅ Exportar dados

**Funciona 100% no navegador** - não precisa instalar nada além do Python!

## Pré-requisitos

Você precisa ter apenas:
- **Python 3.8 ou superior** (recomendado: Python 3.11+)
- **Conexão com internet** (apenas para instalação)

## Instalação em 3 Passos

### 1️⃣ Extrair e Entrar na Pasta
```bash
# Extrair o arquivo ZIP
unzip sistema-faturamento-final.zip
cd sistema-faturamento-final
```

### 2️⃣ Instalar Dependências
```bash
# Instalar as bibliotecas necessárias
pip3 install -r requirements.txt
```

### 3️⃣ Executar o Sistema
```bash
# Iniciar o servidor
python3 src/main.py
```

**Pronto!** Abra seu navegador e acesse: **http://localhost:5000**

## Problemas Comuns e Soluções

### ❌ "python3: command not found"
**Solução:** Instale o Python 3 ou use `python` ao invés de `python3`

### ❌ "pip3: command not found" 
**Solução:** Use `pip` ao invés de `pip3` ou instale o pip

### ❌ "ModuleNotFoundError"
**Solução:** Execute novamente: `pip3 install -r requirements.txt`

### ❌ "Port 5000 already in use"
**Solução:** Feche outros programas usando a porta 5000 ou altere a porta no arquivo `src/main.py`

### ❌ Página em branco no navegador
**Solução:** Aguarde alguns segundos e recarregue a página

## Testando se Funcionou

1. Abra **http://localhost:5000** no navegador
2. Você deve ver a interface do sistema
3. Teste cadastrar um cliente
4. Teste criar uma cobrança

## Para Usar em Produção

Se quiser disponibilizar online para outras pessoas:

```bash
# Instalar servidor de produção
pip3 install gunicorn

# Executar em produção
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## Dados de Teste

O sistema já vem com dados de exemplo:
- 5 clientes cadastrados
- 22 cobranças de exemplo
- Diferentes tipos de cobrança e status

## Suporte

- **Versão:** 2.0
- **Python:** 3.8+ (testado com 3.11)
- **Navegadores:** Chrome, Firefox, Safari, Edge
- **Sistema:** Windows, Mac, Linux

---

**Desenvolvido com Flask + React + SQLite**

