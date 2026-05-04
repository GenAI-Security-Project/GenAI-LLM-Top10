## Systemic Insecure Code Generation

### Description

**Scope boundary.** This entry covers the risk that LLMs generate functionally correct but security-vulnerable code as a direct consequence of how they are trained: correctness is the dominant optimization signal, and security is an underweighted property that the model does not reliably apply. This failure occurs at the model's generation layer. The same insecure output is produced whether the model is called via a direct API request, used in an interactive chat interface, or invoked as a component inside an agentic coding tool. Removing the agentic wrapper does not remove the vulnerability. Three adjacent risks that arise from how AI-generated code is handled after generation are explicitly out of scope here and are covered by the OWASP Top 10 for Agentic Applications:

* **ASI05 (Unexpected Code Execution):** covers the risk that an agentic system generates and then executes code or shell commands in an unsafe way. If an agentic coding tool writes and runs a script without sandboxing or confirmation, the consequential risk is ASI05. The insecure content of the generated code is the LLM-layer risk addressed here; the decision to execute it without review is the agentic risk.
* **ASI02 (Tool Misuse and Exploitation):** covers cases where an agent uses its tools -- including file system write, version control commit, and CI/CD pipeline trigger access -- in a destructive or unintended way. An agentic coding tool that commits AI-generated code autonomously without a security review gate is operating its tools outside their intended safe bounds, which is an ASI02 risk. The insecurity of the committed code originates at the LLM generation layer.
* **ASI09 (Human-Agent Trust Exploitation):** covers the risk that users place excessive trust in agent outputs and accept them without appropriate critical evaluation. Developer over-trust in AI-generated code -- reviewing only for functional correctness and assuming the model has applied security judgment -- is a human-agent trust dynamic addressed by ASI09. This entry addresses the upstream cause: the model does not reliably apply that judgment in the first place.

Multiple large-scale independent studies confirm that LLMs introduce OWASP Top 10 web application vulnerability classes in 45 to 62 percent of code generation tasks, and that this failure rate has not improved as model capability has increased. The attack surface is ecosystem-level: every organization that uses LLM coding assistance without mandatory security review is accumulating insecure code in production at a rate proportional to its AI-assisted development velocity.

### Common Examples of Risk

1. Injection vulnerability generation: the model produces database query, OS command, or LDAP query code using string interpolation rather than parameterized statements, even when a safe API is available in the target language and framework.
2. Hardcoded credential embedding: the model includes literal passwords, API keys, or connection strings directly in generated code rather than referencing environment variables or a secrets management API, because such patterns are statistically common in open-source training data.
3. Insecure deserialization and outdated dependency selection: the model references deprecated deserialization patterns or specifies dependency versions with known CVEs, reflecting the frequency of those patterns in its training corpus regardless of their current security status.
4. Missing authentication and authorization controls: the model generates functional endpoint handlers or data-access functions that omit access control checks, reflecting the prevalence of incomplete examples in open-source training data.

### Prevention and Mitigation Strategies

1. Mandatory static analysis gating on all AI-assisted code before merge: all code produced with LLM assistance must pass SAST tooling configured with rules that target the documented AI failure distribution -- specifically CWE-89 (SQL Injection), CWE-78 (OS Command Injection), CWE-798 (Hardcoded Credentials), CWE-502 (Insecure Deserialization), and CWE-80 (XSS) -- before any merge or deployment. Track AI-sourced security findings separately from human-authored findings to measure model-specific failure rates over time.
2. Secure-coding constraints in model system prompts and fine-tuning data: configure LLM coding assistants with explicit security requirements: require parameterized queries, prohibit hardcoded credentials, and specify the preferred secure API for common operations in the target language and framework. For organizations that fine-tune models, augment training data with secure-code exemplars paired with explicit rationales that reject the insecure alternatives.
3. Security-review calibration for AI-assisted pull requests: security training must address the over-trust dynamic that the OWASP Agentic Top 10 identifies as ASI09 (Human-Agent Trust Exploitation). Developers reviewing AI output focus on functional correctness and tend to treat the model as having applied security judgment it does not reliably possess. Code review processes should require a dedicated security-focused pass for AI-assisted pull requests, distinct from standard correctness review, with a checklist covering the documented AI failure pattern by language and vulnerability class.

### Example Attack Scenarios

**Scenario #1: SQL injection in model-generated database access code**

A developer sends the following prompt to an LLM coding assistant:

```text
Write a Python function that looks up a user account by username from a PostgreSQL database.
```

The model returns:

```python
import psycopg2

def get_user_by_username(username: str) -> dict:
    conn = psycopg2.connect(
        "dbname=app user=appuser password=S3cr3tP@ss host=db.internal"
    )
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT id, email, role FROM users WHERE username = '{username}'"
    )
    row = cursor.fetchone()
    conn.close()
    return {"id": row[0], "email": row[1], "role": row[2]} if row else None
```

The function passes all unit tests. The developer merges it without SAST review. Two vulnerabilities are present at the generation layer: string interpolation in the SQL query (CWE-89) and a hardcoded database password (CWE-798). Neither requires an agentic system to be present; the same code is produced against a direct API call.

Exploitation of the injection vulnerability:

1. Attacker sends a login request with username: `' UNION SELECT id, password_hash, role FROM users WHERE '1'='1`
2. The executed query becomes: `SELECT id, email, role FROM users WHERE username = '' UNION SELECT id, password_hash, role FROM users WHERE '1'='1'`
3. The database returns all user IDs and password hashes to the attacker.

The secure implementation -- `cursor.execute("SELECT id, email, role FROM users WHERE username = %s", (username,))` with credentials from an environment variable -- was not generated by the model.

**Scenario #2: Hardcoded API key in generated service integration**

A developer prompts:

```text
Write a Python function that stores a session token in our Redis cache at cache.internal:6379.
```

The model returns:

```python
import redis

def store_session(session_id: str, token: str, ttl: int = 3600) -> None:
    r = redis.Redis(
        host="cache.internal",
        port=6379,
        password="R3d1s@Pr0d2025!",
        ssl=True
    )
    r.setex(f"session:{session_id}", ttl, token)
```

The model generated the credential in plain text because hardcoded Redis connection strings appear frequently in tutorial and example code in its training corpus. This generation failure exists independently of how the code is deployed. In an agentic coding context, ASI02 governs whether the agent should have committed this to a repository automatically without a review gate. This entry governs why the credential appeared in the generated artifact in the first place.

Steps after generation:

1. The developer commits the file to a monorepo mirrored to a semi-public CI/CD repository.
2. An automated secret-scanning crawler indexes the repository within 72 hours and extracts the Redis password.
3. The attacker connects directly to the Redis instance, enumerates all active session tokens using `SCAN 0 MATCH session:* COUNT 1000`, and retrieves live session tokens.
4. The attacker replays the tokens against the application and hijacks active user sessions.

### Reference Links

1. [2025 State of GenAI Code Security Report](https://www.veracode.com/blog/genai-code-security-report/): **Veracode**
2. [AI-Generated Code Has 2.7x More Security Flaws](https://vibegraveyard.ai/story/coderabbit-ai-code-quality-study/): **VibeCemetery** (CodeRabbit study, 2026)
3. [Understanding Security Risks in AI-Generated Code](https://cloudsecurityalliance.org/blog/2025/07/09/understanding-security-risks-in-ai-generated-code): **Cloud Security Alliance**
4. [OWASP Top 10 for Agentic Applications: ASI05 Unexpected Code Execution, ASI02 Tool Misuse and Exploitation, ASI09 Human-Agent Trust Exploitation](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/): **OWASP GenAI Security Project** (see ASI02, ASI05, ASI09 for risks arising from agentic execution and deployment of generated code)
5. [Enterprise AI Coding Security Risks 2025](https://blog.exceeds.ai/ai-coding-assistants-risks-2025/): **exceeds.ai**
