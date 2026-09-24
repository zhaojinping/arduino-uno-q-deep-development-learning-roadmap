# IoT 设备身份与安全通信实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 完成第八篇第 6 章及其离线策略检查实验，讲清设备身份、TLS 服务身份、MQTT 最小权限和凭据生命周期，同时不把本机教学检查器描述成真实安全验证。

**Architecture:** 使用 Python 标准库实现严格 JSON 解析、纯函数策略评估和无网络 CLI；合成配置只含虚构身份、非秘密凭据引用和声明式 TLS/ACL 元数据。正文、代码说明、Fig-56 Mermaid 与篇章/资源导航按现有 IoT 章节模式共同交付。

**Tech Stack:** Markdown、Mermaid、Python 3.10+、标准库 json/datetime/argparse/unittest；无需第三方依赖、Broker、Arduino UNO Q 或网络。

**Spec:** docs/superpowers/specs/2026-09-24-iot-device-identity-and-secure-communications-design.md

## Global Constraints

- 输入仅采用虚构设备、域名、主题和不可用的凭据引用，不包含私钥、密码、有效 Token、可用证书或用户真实配置。
- 检查器只验证本章规定的 JSON 结构和固定教学策略；PASS 不代表实际设备、凭据、TLS 握手、Broker ACL、身份映射或生产安全成立。
- 代码仅使用 Python 标准库；不得建立 Socket、调用网络、读写密钥材料、访问环境秘密或静默下载依赖。
- CLI 仅读取与脚本同目录的合成 profiles.json，不接受任意输入文件路径，不读取系统当前时间或其他文件。
- 解析前筛查约定的敏感字段名和显著 PEM 私钥标记；解析阶段只报稳定问题码，不回显原始值；策略报告也不得携带输入值。
- 策略拒绝身份/通道/授权不合格的配置；无明文回退、共享设备主体或扩大权限的成功路径。
- Mermaid 正文源块与 diagrams/uno-q-iot-device-identity-secure-communication.mmd 必须一致；SVG 状态如实标注。
- 第八篇章节编号从 1 开始，本章固定为第 6 章；不得改写前五章或其行为契约。
- 章节首次出现产品名时写 Arduino UNO Q，之后才可简称 UNO Q；代码字段和文件名使用反引号。
- 提交与推送只涵盖已审阅通过的本章工作，不声称做过 Broker、TLS、PKI、网络、App Lab、Linux/MCU、Bridge/RPC 或硬件验收。

## Review Focus

1. JSON 含重复成员、非法 UTF-8 或 NaN/Infinity 时，不覆盖、不接受；Task 1 分别测试这些输入。
2. Python 中 bool 是 int 的子类；schema_version、TLS 布尔开关和时间值必须作精确类型检查；Task 1/2 测试错误类型。
3. 多 profile 可能复用 device_id、profile_id、principal_id、client_id 或 credential_ref；Task 2 测试冲突且诊断不得输出凭据值。
4. MQTT publish 与 subscribe 的主题规则方向不同，且 +/# 扩大过滤范围；Task 3 测试跨设备路径、通配符和错误动作。
5. 时间恰好等于 not_before/not_after/rotation_due_at，或秘密字段出现在坏记录中；Task 4/5 测边界、稳定问题码和不回显。非法时间戳必须精确符合零填充秒精度 UTC 格式。

---

## 文件结构

- Create: code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py — 严格解析、纯策略判定和 CLI。
- Create: code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py — 解析、策略、生命周期、CLI 与章节资源测试。
- Create: code/第8篇_IoT/第6章_IoT设备身份与安全通信/profiles.json — 固定合成通过/拒绝案例。
- Create: code/第8篇_IoT/第6章_IoT设备身份与安全通信/README.md — 演示、输出契约和限制。
- Create: diagrams/uno-q-iot-device-identity-secure-communication.mmd — Fig-56 唯一图源。
- Create: book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md — 正文与 Mermaid 源块。
- Modify: book/第8篇_IoT/README.md、SUMMARY.md、README.md — 篇入口、阅读目录和章节总数/状态。
- Modify: resources/references.md — NIST、IETF、OASIS 来源及本章验证边界。
- Modify: images/第8篇_IoT/README.md — Fig-56 登记。

## 稳定接口与配置契约

### policy_linter.py

- MAX_PROFILE_BYTES=32768、MAX_PROFILES=32、MAX_RULES_PER_PROFILE=16；都是固定教学上限。
- parse_document(raw: bytes) -> dict[str, object]：严格 UTF-8；拒绝重复 JSON 键、NaN/Infinity、非对象根、未知字段及错误 schema_version。
- parse_utc_timestamp(value: object) -> datetime.datetime：只接受秒精度 UTC 格式 YYYY-MM-DDTHH:MM:SSZ，返回 UTC-aware 值。
- evaluate_document(document, *, reference_time) -> list[dict[str, object]]：按输入顺序产生报告；纯逻辑，不读时钟、文件或网络。
- run_cli(argv=None, *, stdout=None, stderr=None) -> int：仅读取脚本同目录 profiles.json，并接受显式 --now；全 PASS 返回 0，有策略 DENY 返回 1，CLI/读文件/解析错误返回 2。
- 报告字段固定为 profile_id、decision、findings；finding 固定为 code、path，不携带原始输入值。

### profiles.json

根对象精确包含 schema_version、profiles。每个 profile 精确包含 profile_id、device_id、client_id、principal_id、credential_ref、credential_type、credential_state、not_before、not_after、rotation_due_at、tls、authorization。tls 精确字段为 enabled、verify_server、server_name、trust_ref、client_auth；authorization 精确字段为 default、rules；每条 rule 精确字段为 effect、operation、topic。schema_version 必须为整数 1，bool 不可冒充；profiles 为 1～32 项，rules 每份最多 16 项。

教学映射要求 client_id 等于 device_id、principal_id 等于 device:<device_id>；这只检查字符串约定，不证明密钥持有或证书身份。样例仅用 broker.example.invalid 与 synthetic:// 引用。

### 固定教学策略与问题码

- TLS 要求 enabled=true、verify_server=true、非通配 server_name、非空 trust_ref、client_auth=mutual_tls。此为本章教学策略，不是普遍配置建议。
- device_id、profile_id、client_id、principal_id、credential_ref 在 profiles 集合中均唯一；credential_type 为 x509_client_certificate。
- authorization.default=deny；设备仅可 publish 自身 telemetry/state 和 subscribe 自身 commands；拒绝 +/#、跨设备路径、未知动作和重复规则。
- credential_state 必须为 active，且 not_before < not_after、not_before <= reference_time < not_after、rotation_due_at > reference_time。
- 仅筛查约定的敏感字段名和显著 PEM 私钥标记；这不是任意秘密发现器。诊断不回显字段值。
- 稳定问题码至少包括 TLS_DISABLED、TLS_SERVER_VERIFY_DISABLED、DEVICE_ID_REUSED、PROFILE_ID_REUSED、DEVICE_PRINCIPAL_REUSED、CLIENT_ID_REUSED、CREDENTIAL_REF_REUSED、ACL_DEFAULT_NOT_DENY、ACL_CROSS_DEVICE_TOPIC、ACL_WILDCARD_TOO_BROAD、CREDENTIAL_REVOKED、CREDENTIAL_NOT_YET_VALID、CREDENTIAL_EXPIRED、CREDENTIAL_ROTATION_OVERDUE、SECRET_LITERAL_REJECTED、INPUT_SIZE_INVALID、DUPLICATE_JSON_KEY。

---

### Task 1: 严格 JSON 与 UTC 输入边界

**Files:**
- Create: code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py
- Create: code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py

**Interfaces:**
- Produces: parse_document(raw: bytes) -> dict[str, object]；parse_utc_timestamp(value: object) -> datetime.datetime。
- 根对象只接受 schema_version 与 profiles；schema_version 必须是 type(value) is int 且值为 1。

- [ ] **Step 1: Write parser/time tests first**

Add these tests before implementation:

```python
import unittest
import policy_linter

class ParserTests(unittest.TestCase):
    def test_duplicate_member_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
            policy_linter.parse_document(
                b'{"schema_version":1,"profiles":[],"profiles":[]}'
            )

    def test_nonfinite_and_invalid_utf8_are_rejected(self):
        for raw in (b'{"schema_version":1,"profiles":[],"x":NaN}', bytes((255,))):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                policy_linter.parse_document(raw)

    def test_bool_is_not_schema_version_one(self):
        with self.assertRaisesRegex(ValueError, "SCHEMA_VERSION_INVALID"):
            policy_linter.parse_document(b'{"schema_version":true,"profiles":[]}')

    def test_timestamp_requires_zulu_seconds(self):
        self.assertEqual(
            policy_linter.parse_utc_timestamp("2026-09-24T12:00:00Z").utcoffset().total_seconds(),
            0,
        )
        for value in ("2026-09-24", "2026-09-24T12:00:00+08:00", 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                policy_linter.parse_utc_timestamp(value)

    def test_timestamp_requires_zero_padded_fields(self):
        with self.assertRaises(ValueError):
            policy_linter.parse_utc_timestamp("2026-9-24T12:00:00Z")
```

- [ ] **Step 2: Run tests and confirm failure**

Run: python -B -m unittest discover -s "code/第8篇_IoT/第6章_IoT设备身份与安全通信" -p "test_*.py" -v<br>
Expected: failure because policy_linter.py and its functions do not exist.

- [ ] **Step 3: Implement bounded strict parsing**

Define byte/profile/rule limits; use json.loads with object_pairs_hook to reject duplicates and parse_constant to reject NaN/Infinity; strictly decode UTF-8; enforce exact root fields, root object type, schema_version exact int, and 1–32 profile count. Parse UTC with datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ"), require strftime round-trip equality to reject non-zero-padded variants, then attach timezone.utc. Before schema errors, screen for the agreed sensitive key names and conspicuous PEM private-key markers; raise only the stable code SECRET_LITERAL_REJECTED and never include raw values. Stable ValueError messages must not contain raw input.

```python
def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result
```

- [ ] **Step 4: Re-run parser tests**

Run the chapter unittest command. Expected: valid JSON parses; duplicate keys, invalid UTF-8, non-finite numbers, wrong roots/types, unknown root keys, empty/oversized input and invalid timestamps reject deterministically.

- [ ] **Step 5: Commit parser**

Run: git add "code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py" "code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py"<br>
Run: git commit -m "feat: add strict IoT profile parser"

### Task 2: 设备身份映射与 TLS 声明检查

**Files:**
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py

**Interfaces:**
- Produces: evaluate_document(document, *, reference_time) -> list[dict[str, object]]。
- Report shape: {profile_id, decision, findings}; finding shape: {code, path}; profile 顺序与输入相同。

- [ ] **Step 1: Add a profile builder and failing tests**

Test a complete valid profile, duplicate profile_id/device_id/principal_id/client_id/credential_ref, disabled TLS, disabled server verification, wildcard hostname, missing trust_ref, bool/type confusion, missing fields and unknown nested fields.

```python
def valid_profile(device_id="uno-q-demo-01"):
    return {
        "profile_id": "profile-" + device_id,
        "device_id": device_id,
        "client_id": device_id,
        "principal_id": "device:" + device_id,
        "credential_ref": "synthetic://credential/" + device_id,
        "credential_type": "x509_client_certificate",
        "credential_state": "active",
        "not_before": "2026-01-01T00:00:00Z",
        "not_after": "2027-01-01T00:00:00Z",
        "rotation_due_at": "2026-10-01T00:00:00Z",
        "tls": {
            "enabled": True, "verify_server": True,
            "server_name": "broker.example.invalid",
            "trust_ref": "synthetic://trust/demo-root",
            "client_auth": "mutual_tls",
        },
        "authorization": {"default": "deny", "rules": []},
    }
```

- [ ] **Step 2: Run tests and confirm failure**

Run the chapter unittest command. Expected: evaluation tests fail because evaluate_document and identity/TLS findings have not been implemented.

- [ ] **Step 3: Implement identity uniqueness and TLS policy**

Require client_id == device_id and principal_id == "device:" + device_id. Reject reused profile_id/device_id/client_id/principal_id/credential_ref across profiles. Use exact bool checks. Require the TLS tutorial baseline and non-wildcard service name; report TLS_SERVER_VERIFY_DISABLED when verify_server is false. Findings include only code/path.

- [ ] **Step 4: Re-run identity/TLS tests**

Run the chapter unittest command. Expected: complete profiles have no identity/TLS findings; every invalid mapping/settings profile is DENY with the expected stable code.

- [ ] **Step 5: Commit identity/TLS checks**

Run: git add "code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py" "code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py"<br>
Run: git commit -m "feat: validate IoT identity and TLS profile policy"

### Task 3: MQTT 默认拒绝与逐设备 ACL

**Files:**
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py

**Interfaces:**
- Consumes evaluate_document from Task 2.
- Permitted pairs: allow/publish own telemetry or state; allow/subscribe own commands.
- Produces ACL_DEFAULT_NOT_DENY, ACL_OPERATION_INVALID, ACL_WILDCARD_TOO_BROAD, ACL_CROSS_DEVICE_TOPIC, ACL_DUPLICATE_RULE and ACL_RULE_NOT_ALLOWED.

- [ ] **Step 1: Add ACL tests**

Test both permitted directions and deny default allow, +/# in any rule, other-device topics, subscribe telemetry, publish commands, unknown operation, duplicate rule and malformed fields.

```python
def test_cross_device_command_subscription_is_denied(self):
    profile = valid_profile()
    profile["authorization"] = {
        "default": "deny",
        "rules": [{
            "effect": "allow",
            "operation": "subscribe",
            "topic": "demo/v1/devices/uno-q-demo-02/commands",
        }],
    }
    report = evaluate_one(profile)
    self.assertEqual(report["decision"], "DENY")
    self.assertIn("ACL_CROSS_DEVICE_TOPIC", finding_codes(report))
```

- [ ] **Step 2: Run ACL tests and confirm failure**

Run the chapter unittest command. Expected: tests for broad filters and cross-device access fail before the ACL evaluator is implemented.

- [ ] **Step 3: Implement exact action/topic pairing**

Build allowed literal topic paths from the validated device_id. Require default=deny, exact rule fields and effect=allow. Reject +/# before exact topic comparison; accept only the operation-topic pairs in Interfaces and reject duplicates. Never infer a real Broker policy from this local result.

- [ ] **Step 4: Re-run ACL tests**

Run the chapter unittest command. Expected: own-device pairs pass; wildcard, cross-device, duplicate, malformed and wrong-direction rules are DENY.

- [ ] **Step 5: Commit ACL checks**

Run: git add "code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py" "code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py"<br>
Run: git commit -m "feat: enforce default-deny IoT topic policy"

### Task 4: 凭据生命周期与秘密值不回显

**Files:**
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py

**Interfaces:**
- Consumes UTC parsing and profile evaluation from Tasks 1–3.
- Requires active state and not_before <= reference_time < not_after and rotation_due_at > reference_time.
- Findings include revoked, not-yet-valid, expired, overdue rotation and SECRET_LITERAL_REJECTED codes.

- [ ] **Step 1: Add temporal-boundary and redaction tests**

At reference_time 2026-09-24T12:00:00Z, test not_before equality (allowed), not_after equality (expired), rotation_due_at equality (overdue), not_before >= not_after (invalid interval), revoked state, and a forbidden sensitive field containing a fake private-key marker. Parser/CLI tests assert only SECRET_LITERAL_REJECTED is emitted for malformed secret-bearing input; direct evaluator tests assert a SECRET_LITERAL_REJECTED finding for a synthetic profile and that the marker never appears in serialized report or stderr.

```python
def test_expiry_is_exclusive_and_secret_value_is_not_echoed(self):
    profile = valid_profile()
    profile["not_after"] = "2026-09-24T12:00:00Z"
    report = evaluate_one(profile)
    output = json.dumps(report, sort_keys=True)
    self.assertIn("CREDENTIAL_EXPIRED", output)
    self.assertNotIn("synthetic-private-key-marker", output)
```

- [ ] **Step 2: Run tests and confirm failure**

Run the chapter unittest command. Expected: lifecycle and redaction tests fail until those rules are present.

- [ ] **Step 3: Implement lifecycle checks and narrow secret screening**

Use the UTC parser for all three timestamps. Reject invalid date order, non-active state, not-yet-valid, expired and due/overdue rotation according to the strict comparisons above. Reuse a bounded recursive secret-screening helper before schema validation and in direct policy evaluation; malformed file input exits 2 with only SECRET_LITERAL_REJECTED on stderr, while a direct synthetic-profile evaluation records a finding. Never put values in errors, findings or logs. Do not claim heuristic scanning detects arbitrary secrets.

- [ ] **Step 4: Re-run lifecycle/redaction tests**

Run the chapter unittest command. Expected: exact temporal boundaries produce stable findings and serialized reports contain no fake marker.

- [ ] **Step 5: Commit lifecycle rules**

Run: git add "code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py" "code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py"<br>
Run: git commit -m "feat: validate IoT credential lifecycle metadata"

### Task 5: 合成样例、CLI 与代码说明

**Files:**
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py
- Create: code/第8篇_IoT/第6章_IoT设备身份与安全通信/profiles.json
- Create: code/第8篇_IoT/第6章_IoT设备身份与安全通信/README.md

**Interfaces:**
- CLI: policy_linter.py --now YYYY-MM-DDTHH:MM:SSZ；仅读取脚本旁 profiles.json。
- Exit 0 means all PASS; 1 means at least one policy DENY; 2 means CLI/file/parse error.
- stdout is deterministic JSONL in profile order; stderr reports stable codes only.

- [ ] **Step 1: Add CLI tests against temporary synthetic fixtures**

Patch PROFILE_FILE to a TemporaryDirectory fixture. Test all-PASS exit 0, deliberate DENY exit 1, malformed/missing file and invalid --now exit 2, JSONL order, and no secret marker in stdout/stderr.

```python
def test_all_pass_profiles_return_zero(self):
    profile_file = write_profiles([valid_profile()])
    stdout, stderr = io.StringIO(), io.StringIO()
    with mock.patch.object(policy_linter, "PROFILE_FILE", profile_file):
        code = policy_linter.run_cli(
            ["--now", "2026-09-24T12:00:00Z"],
            stdout=stdout,
            stderr=stderr,
        )
    self.assertEqual(code, 0)
    self.assertEqual(stderr.getvalue(), "")
    self.assertIn('"decision":"PASS"', stdout.getvalue())
```

- [ ] **Step 2: Run CLI tests and confirm failure**

Run the chapter unittest command. Expected: tests fail because argparse, bundled fixture loading and return-code behavior are absent.

- [ ] **Step 3: Implement the no-arbitrary-path CLI**

Set PROFILE_FILE=Path(__file__).resolve().with_name("profiles.json"); parse only --now; read those bytes and call parse_document/evaluate_document. Emit deterministic JSON lines. Return 0/1/2 as defined. On OSError report INPUT_READ_FAILED without path or exception text. Do not read environment, current time, other files or sockets.

- [ ] **Step 4: Add fixture and code README**

profiles.json contains one passing profile plus discrete bad profiles for TLS verification disabled, shared principal, wildcard/cross-device ACL and expired/revoked credential. Use only example.invalid, synthetic:// references and fake dates. README gives exact commands, expected states and the linter's cryptographic/production limitations.

- [ ] **Step 5: Run CLI tests and demonstration**

Run: python -B "code/第8篇_IoT/第6章_IoT设备身份与安全通信/policy_linter.py" --now "2026-09-24T12:00:00Z"<br>
Expected: deterministic JSONL with PASS and DENY profiles, exit 1 because the fixture deliberately contains denials. Run chapter unittest discovery; all tests pass.

- [ ] **Step 6: Commit tool and fixtures**

Run: git add "code/第8篇_IoT/第6章_IoT设备身份与安全通信"<br>
Run: git commit -m "feat: add offline IoT security policy linter"

### Task 6: Fig-56 与出版级章节正文

**Files:**
- Create: diagrams/uno-q-iot-device-identity-secure-communication.mmd
- Create: book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/README.md
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py

**Interfaces:**
- Front matter: title 与 H1 相同；part=8；chapter=6；status=draft；last_verified=2026-09-24。
- 第一处正文写全 Arduino UNO Q；代码说明字段顺序遵循 docs/writing-guidelines.md。
- Mermaid 正文源与独立 Fig-56 文件一致；章节包含实验结果、常见问题、边界、延伸阅读。

- [ ] **Step 1: Add failing chapter/figure contract tests**

Test metadata, CLI command, figure existence, success/reject branches, local link targets and exact Mermaid source equality.

```python
def test_mermaid_source_is_identical_to_chapter_block(self):
    root = Path(__file__).resolve().parents[3]
    diagram = (root / "diagrams/uno-q-iot-device-identity-secure-communication.mmd").read_text(
        encoding="utf-8"
    ).strip()
    chapter = (root / "book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md").read_text(
        encoding="utf-8"
    )
    marker = chr(96) * 3 + "mermaid"
    body = chapter.split(marker, 1)[1].split(chr(96) * 3, 1)[0].strip()
    self.assertEqual(body, diagram)
```

- [ ] **Step 2: Run tests and confirm missing chapter assets fail**

Run chapter unittest discovery. Expected: tests fail because chapter and Fig-56 do not exist yet.

- [ ] **Step 3: Author the diagram**

Create enrollment → unique device identity → TLS service-name validation → Broker authentication and principal binding → default-deny ACL → permitted MQTT flow. TLS/authentication/authorization failures reach reject/audit with no plaintext fallback. Show rotation/revocation returning to identity management.

- [ ] **Step 4: Write the chapter**

Cover identity-field distinctions; TLS channel vs service identity vs MQTT authorization; publish/subscribe ACL matrix; credential lifecycle; offline experiment; exact code explanation fields; fixed output; actual test status; limitations; FAQ; summary; and references. Label tutorial policy separately from standards and recommendations.

- [ ] **Step 5: Run the contract tests**

Run chapter unittest discovery. Expected: metadata and documented command match the files; the exact Mermaid source matches; both success and rejection routes appear; local targets resolve.

- [ ] **Step 6: Commit the chapter and figure**

Run: git add "diagrams/uno-q-iot-device-identity-secure-communication.mmd" "book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md" "code/第8篇_IoT/第6章_IoT设备身份与安全通信/README.md" "code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py"<br>
Run: git commit -m "docs: write IoT identity and secure communications chapter"

### Task 7: 来源、目录和图示登记

**Files:**
- Modify: SUMMARY.md
- Modify: README.md
- Modify: book/第8篇_IoT/README.md
- Modify: resources/references.md
- Modify: images/第8篇_IoT/README.md
- Modify: code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py

**Interfaces:**
- Chapter 6 follows Chapter 5 in all navigation; total chapter count changes 54 → 55.
- Add “第八篇第6章补充核验” for NISTIR 8259A/8259 Rev. 1, NIST capability catalog, RFC 9846, RFC 9525, OASIS MQTT 5.0, each with use/version/boundary.
- Fig anchor: fig-56-uno-q-iot-device-identity-secure-communication; SVG pending until actually generated and visually reviewed.

- [ ] **Step 1: Add failing navigation/reference tests**

Test exact Chapter 6 path in SUMMARY and Part 8 README, root count 55, all registered official-source groups, Fig-56 anchor/source/chapter links, and relative link target existence.

```python
def test_summary_registers_chapter_six(self):
    root = Path(__file__).resolve().parents[3]
    target = "book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md"
    self.assertIn(target, (root / "SUMMARY.md").read_text(encoding="utf-8"))
    self.assertIn("第6章", (root / "book/第8篇_IoT/README.md").read_text(encoding="utf-8"))
    self.assertIn("共 55 章", (root / "README.md").read_text(encoding="utf-8"))
```

- [ ] **Step 2: Run registry tests and confirm they fail**

Run chapter unittest discovery. Expected: checks fail because current navigation ends at Chapter 5/Fig-55.

- [ ] **Step 3: Update registries without reordering prior chapters**

Append Chapter 6 after Chapter 5; update root total/status; register Fig-56; add official source rows with current versions/dates and non-endorsement notes. Preserve all existing entries. Do not claim SVG rendered without rendering and visual review.

- [ ] **Step 4: Run registry and local-link tests**

Run chapter unittest discovery. Expected: all new targets exist, all links resolve, prior chapter links remain unchanged.

- [ ] **Step 5: Commit navigation and references**

Run: git add SUMMARY.md README.md "book/第8篇_IoT/README.md" resources/references.md "images/第8篇_IoT/README.md" "code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py"<br>
Run: git commit -m "docs: register IoT identity chapter and sources"

### Task 8: 全篇验证与交接

**Files:** Verify all Task 1–7 deliverables and changed indexes.

- [ ] **Step 1: Run every IoT chapter test**

Run: python -B -m unittest discover -s "code/第8篇_IoT" -p "test_*.py" -v<br>
Expected: all existing five-chapter tests and new Chapter 6 tests pass.

- [ ] **Step 2: Verify CLI outcomes and non-disclosure**

Run the Task 5 command; expect stable JSONL and exit 1 only for deliberate fixture denials. Task 5 tests separately assert all-PASS exit 0 and invalid-input exit 2. Confirm no output contains the synthetic secret marker.

- [ ] **Step 3: Verify chapter, links, references and Mermaid**

Check front matter, headings, code explanation fields, exact CLI invocation, internal targets/anchors, all source rows, unique Fig-56 anchor, exact Mermaid equality and accurate SVG/hardware verification status.

- [ ] **Step 4: Check the complete implementation diff**

Run: git diff --check origin/main..HEAD<br>
Run: git status --short<br>
Expected: no whitespace errors and only intended chapter deliverables; do not amend or force-push.

- [ ] **Step 5: Commit a verified correction only if needed**

If Step 4 finds an issue, fix only that issue, rerun its owning test and the whole IoT suite, then commit a specific correction. Handoff reports counts and explicitly states live TLS/Broker/UNO Q security was not tested.

## Plan Self-Review

- Coverage: Tasks 1–2 cover identity and TLS; Task 3 ACL; Task 4 lifecycle/redaction; Task 5 fixtures/CLI; Task 6正文/Fig-56; Task 7 navigation/sources; Task 8 integration evidence.
- All five Review Focus classes have explicit tests in Tasks 1–5.
- Interfaces and report fields remain consistent across the tasks; the CLI has no arbitrary path or secret input.
- No live service, key/certificate generation, product-specific compatibility claim or SVG rendering promise was added.
- No TBD/TODO or unassigned implementation step remains.
