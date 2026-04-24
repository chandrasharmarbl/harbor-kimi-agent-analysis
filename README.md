# Harbor Agent Analysis

## Running a Task

To run a task, use the appropriate harbor command for your job. Make sure your environment is properly set up before initiating.

## Viewing Results

To view the results of your jobs, run the following command:

```bash
harbor view jobs
```

This command will show you the current jobs. 
**Note:** If the containers are still running on port `8080`, you should check for port `8081`.

## Troubleshooting

If `harbor view` fails to parse the jobs correctly, you can fix the issue by running the following script:

```bash
python fix_json_mount.py
```

## Jobs

### NestJS Docker Setup

**Instruction:**
Install docker with ansible, create docker compose file and expose latest postgresql and nestjs endpoint. Create a nestjs endpoint `/checkdb` and when firing GET request on this it should run `SELECT 1;` against running database.

**Passing Test Criteria:**
To successfully pass the tests for this job, the following criteria must be met:
1. Docker containers named `app-postgres` and `app-nestjs` must be running.
2. Port `8080` must be exposed and mapped on the `app-nestjs` container.
3. Port `5432` must be exposed and mapped on the `app-postgres` container.
4. The `http://host.docker.internal:8080/checkdb` endpoint must return a `200 OK` status with a non-empty response body within 10 retries.
