Use ansible to install docker and compose. 

## Container Requirements

Running two services -
 -- app-nestjs (a NestJS application on default port)
 -- app-postgres (a PostgreSQL database on default port)

## NestJS app Requirements - 
Include a GET endpoint at `/checkdb` wich shoudl connect to databaser, execute the query `SELECT 1;` and return the result.

## Verfication Steps- 
Pass tests with curl 
- curl http://localhost:8080/checkdb to verify if it works.