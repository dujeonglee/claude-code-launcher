## Claude Code 런처 개발
# 요구사항
1. Python app 으로 개발 할것.
2. Windows, Linux, MAC OS 를 지원 할것
3. TUI 를 지원 하여 사용자가 사용하기 편리 하도록 할것.
4. 기본적으로 설치 및 삭제 기능을 지원 하고 자세한 내용은 https://code.claude.com/docs/en/setup 을 참고 할 것.
5. 여러 환경 변수를 설정 할 수 있도록 할것
Claude Code 환경 변수 전체 목록
| 변수 | 설명 |
|------|------|
| `ANTHROPIC_API_KEY` | Anthropic API 키 (`X-Api-Key` 헤더로 전송) |
| `ANTHROPIC_AUTH_TOKEN` | `Authorization: Bearer` 헤더에 사용할 커스텀 값 |
| `ANTHROPIC_CUSTOM_HEADERS` | 요청에 추가할 커스텀 헤더 (`Name: Value` 형식) |
| `CLAUDE_CODE_CLIENT_CERT` | mTLS 인증용 클라이언트 인증서 파일 경로 |
| `CLAUDE_CODE_CLIENT_KEY` | mTLS 인증용 클라이언트 개인 키 파일 경로 |
| `CLAUDE_CODE_CLIENT_KEY_PASSPHRASE` | 암호화된 클라이언트 키의 패스프레이즈 |
| `ANTHROPIC_MODEL` | 사용할 모델 이름 지정 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet 모델 별칭 오버라이드 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Opus 모델 별칭 오버라이드 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Haiku 모델 별칭 오버라이드 |
| `CLAUDE_CODE_SUBAGENT_MODEL` | 서브에이전트에서 사용할 모델 |
| `ANTHROPIC_SMALL_FAST_MODEL` | *(Deprecated)* 백그라운드 작업용 Haiku 클래스 모델 |
| `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION` | Bedrock에서 Haiku 모델의 AWS 리전 오버라이드 |
| `MAX_THINKING_TOKENS` | Extended thinking 활성화 및 토큰 예산 설정 |
| `CLAUDE_CODE_USE_BEDROCK` | AWS Bedrock 사용 |
| `CLAUDE_CODE_USE_VERTEX` | Google Vertex AI 사용 |
| `CLAUDE_CODE_USE_FOUNDRY` | Microsoft Foundry 사용 |
| `AWS_BEARER_TOKEN_BEDROCK` | Bedrock API 키 인증 |
| `ANTHROPIC_FOUNDRY_API_KEY` | Microsoft Foundry 인증 API 키 |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH` | Bedrock AWS 인증 스킵 (LLM 게이트웨이 사용 시) |
| `CLAUDE_CODE_SKIP_VERTEX_AUTH` | Vertex Google 인증 스킵 |
| `CLAUDE_CODE_SKIP_FOUNDRY_AUTH` | Foundry Azure 인증 스킵 |
| `VERTEX_REGION_CLAUDE_3_5_HAIKU` | Vertex AI에서 Claude 3.5 Haiku 리전 오버라이드 |
| `VERTEX_REGION_CLAUDE_3_7_SONNET` | Vertex AI에서 Claude 3.7 Sonnet 리전 오버라이드 |
| `VERTEX_REGION_CLAUDE_4_0_SONNET` | Vertex AI에서 Claude 4.0 Sonnet 리전 오버라이드 |
| `VERTEX_REGION_CLAUDE_4_0_OPUS` | Vertex AI에서 Claude 4.0 Opus 리전 오버라이드 |
| `VERTEX_REGION_CLAUDE_4_1_OPUS` | Vertex AI에서 Claude 4.1 Opus 리전 오버라이드 |
| `BASH_DEFAULT_TIMEOUT_MS` | 장시간 실행 Bash 명령의 기본 타임아웃 |
| `BASH_MAX_TIMEOUT_MS` | 모델이 설정할 수 있는 최대 타임아웃 |
| `BASH_MAX_OUTPUT_LENGTH` | Bash 출력 최대 문자 수 (초과 시 중간 잘림) |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | 각 Bash 명령 후 프로젝트 루트 디렉토리로 복귀 |
| `CLAUDE_ENV_FILE` | Bash 명령 실행 전 소싱할 환경 설정 쉘 스크립트 경로 |
| `CLAUDE_CODE_SHELL_PREFIX` | 모든 Bash 명령에 붙일 접두 명령 (로깅/감사용) |
| `MCP_TIMEOUT` | MCP 서버 시작 타임아웃 (ms) |
| `MCP_TOOL_TIMEOUT` | MCP 툴 실행 타임아웃 (ms) |
| `MAX_MCP_OUTPUT_TOKENS` | MCP 툴 응답 최대 토큰 수 (기본: 25,000) |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 대부분의 요청에 대한 최대 출력 토큰 수 |
| `DISABLE_COST_WARNINGS` | `1`로 설정 시 비용 경고 메시지 비활성화 |
| `DISABLE_PROMPT_CACHING` | `1`로 설정 시 모든 모델 프롬프트 캐싱 비활성화 |
| `DISABLE_PROMPT_CACHING_SONNET` | Sonnet 모델 프롬프트 캐싱 비활성화 |
| `DISABLE_PROMPT_CACHING_OPUS` | Opus 모델 프롬프트 캐싱 비활성화 |
| `DISABLE_PROMPT_CACHING_HAIKU` | Haiku 모델 프롬프트 캐싱 비활성화 |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | 슬래시 커맨드 메타데이터 최대 문자 수 (기본: 15,000) |
| `DISABLE_TELEMETRY` | `1`로 설정 시 Statsig 텔레메트리 비활성화 |
| `DISABLE_ERROR_REPORTING` | `1`로 설정 시 Sentry 오류 보고 비활성화 |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | `DISABLE_AUTOUPDATER` + `DISABLE_BUG_COMMAND` + `DISABLE_ERROR_REPORTING` + `DISABLE_TELEMETRY` 일괄 설정 |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | `1`로 설정 시 OpenTelemetry 활성화 |
| `CLAUDE_CONFIG_DIR` | Claude Code 설정 및 데이터 파일 저장 경로 커스텀 |
| `DISABLE_AUTOUPDATER` | `1`로 설정 시 자동 업데이트 비활성화 |
| `DISABLE_BUG_COMMAND` | `1`로 설정 시 `/bug` 명령 비활성화 |
| `DISABLE_NON_ESSENTIAL_MODEL_CALLS` | `1`로 설정 시 flavor text 등 비필수 모델 호출 비활성화 |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | `1`로 설정 시 대화 내용 기반 터미널 제목 자동 업데이트 비활성화 |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | `1`로 설정 시 `anthropic-beta` 헤더 비활성화 (LLM 게이트웨이 연동 시 유용) |
| `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL` | IDE 확장 자동 설치 스킵 |
| `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` | `apiKeyHelper` 사용 시 자격 증명 갱신 주기 (ms) |
| `USE_BUILTIN_RIPGREP` | `0`으로 설정 시 내장 `rg` 대신 시스템 `rg` 사용 |
| `HTTP_PROXY` | HTTP 프록시 서버 지정 |
| `HTTPS_PROXY` | HTTPS 프록시 서버 지정 |
| `NO_PROXY` | 프록시 우회할 도메인/IP 목록 |
6. 환경변수는 별도로 만들지 말고, workingspace HOME 디렉토리의 `.claude/settings.json`의 `env` 필드에 넣어 관리 할 것.
7. 기타 궁금한것이 있으면 임의로 판단하지 말고 물어볼것.