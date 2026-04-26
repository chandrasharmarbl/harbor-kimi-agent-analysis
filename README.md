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

## Job Analysis

### Observations

| Job Name | Status | Cost (USD) | Tokens | Steps |
| --- | --- | --- | --- | --- |
| [2026-04-26__23-29-36](./analysis/2026-04-26__23-29-36.md) | Success | $0.0379 | 1,125,518 | 55 |
| [2026-04-27__01-25-17](./analysis/2026-04-27__01-25-17.md) | Failure | $0.0368 | 797,744 | 45 |
| [2026-04-26__22-37-30](./analysis/2026-04-26__22-37-30.md) | Failure | $0.0377 | 1,293,467 | 67 |
| [2026-04-26__23-46-38](./analysis/2026-04-26__23-46-38.md) | Success | $0.0396 | 1,368,672 | 58 |
| [2026-04-27__02-35-43](./analysis/2026-04-27__02-35-43.md) | Success | $0.0624 | 2,214,214 | 61 |
| [2026-04-27__02-30-38](./analysis/2026-04-27__02-30-38.md) | Failure | $0.0000 | 0 | 0 |
| [2026-04-27__03-10-12](./analysis/2026-04-27__03-10-12.md) | Success | $0.0427 | 1,533,959 | 51 |
| [2026-04-27__01-10-30](./analysis/2026-04-27__01-10-30.md) | Success | $0.0314 | 992,775 | 52 |
| [2026-04-27__02-57-34](./analysis/2026-04-27__02-57-34.md) | Success | $0.0367 | 1,211,372 | 53 |
| [2026-04-27__01-43-26](./analysis/2026-04-27__01-43-26.md) | Success | $0.0236 | 787,196 | 51 |
| [2026-04-26__23-06-32](./analysis/2026-04-26__23-06-32.md) | Success | $0.0590 | 3,337,791 | 112 |

### Key Findings

- **Success Rate**: The agent successfully completed the task in 8 out of 11 runs (72.7% success rate).
- **Cost & Tokens**: On average, successful runs cost around $0.04 USD and use about 1-1.5M tokens, typically completing in 50-60 steps.
- **Why it Fails Sometimes**:
  1. **Network Configuration in Docker-in-Docker**: The agent sometimes struggles with mapping ports (`localhost` vs container IPs), failing verification because the endpoint isn't accessible correctly from the host environment.
  2. **Database Authentication & Connectivity**: The NestJS application occasionally fails to start because it attempts to connect to `localhost:5432` instead of the `app-postgres` service name in the Docker Compose network.
  3. **Agent Crashes/Timeouts**: One run failed with 0 tokens and $0 cost, indicating a system failure, timeout, or crash before the agent could take any steps.
