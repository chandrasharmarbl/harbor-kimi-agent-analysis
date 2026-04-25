Use ansible to install docker and compose. 

Then, start two services using docker compose, a PostgreSQL database on default port named app-postgres and a NestJS application named app-nestjs. 

The NestJS application must include a GET endpoint at `/checkdb`. When this endpoint is accessed, the application should connect to the database, execute the query `SELECT 1;`, and return the result.

Test with a curl to the endpoint http://localhost:8080/checkdb to verify if it works.