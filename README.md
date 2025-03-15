# Inicialização do Projeto

## 🚀 Como Iniciar o Projeto

### 1️⃣ Construindo e Subindo os Containers
Caso ainda não tenha a imagem Docker construída, execute o seguinte comando no mesmo diretório do arquivo `docker-compose.yml`:
```sh
docker compose up --build
```
Se a imagem já foi construída anteriormente, basta rodar:
```sh
docker compose up
```

---

Após iniciar o projeto, acesse a documentação via Swagger pelo seguinte link:
```sh
http://localhost:5005/apidocs/
```

---

## 🗄️ Acessando o Banco de Dados no Container
Para acessar o banco de dados dentro do container, siga os passos abaixo:

### 1️⃣ Certifique-se de que o container do banco está rodando
Liste os containers em execução:
```sh
docker ps
```

### 2️⃣ Descubra o ID do container do banco de dados
O comando acima exibirá uma lista de containers. Encontre o container do banco de dados e copie seu ID.

### 3️⃣ Acesse o banco de dados
Substitua `ID-DO-CONTAINER` pelo ID real do container:
```sh
docker exec -it ID-DO-CONTAINER psql -U postgres -d database
```

---

## 🔧 Comandos Úteis no PostgreSQL

- Listar todos os bancos de dados:
  ```sh
  \l
  ```
- Conectar a um banco de dados específico:
  ```sh
  \c <nome_do_banco>
  ```
- Listar todas as tabelas do banco de dados atual:
  ```sh
  \dt
  ```
- Exibir a estrutura de uma tabela:
  ```sh
  \d <nome_da_tabela>
  ```

---

📌 **Dica:** Para sair do PostgreSQL, use o comando `\q`.

---

⚡ **Agora você está pronto para rodar e acessar o projeto!**