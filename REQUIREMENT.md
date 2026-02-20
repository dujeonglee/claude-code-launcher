## Claude Code 런처 개발
# 요구사항
1. 파이선 앱 으로 개발 할것.
2. 윈도우, WSL, 리눅스, 맥 OS 를 지원 할것
3. Typer 파이선 라이브러리를 사용할 것.
4. 앱이 실행 되면 다음을 순서대로 수행 할것.
    - Step1: claude 가 설치 되어 있는지 확인. 설치 되어 있지 않다면 Step2로 설치 되어 있다면 Step3으로 진행.
    - Step2: OS에 따라 설치 스크립트를 shell에서 실행. 윈도우를 제외한 환경에 대해서는 install.sh를 실행하고, 윈도우에 대해서는 install.ps1 을 파워쉘에서 수행 하고 실패 할 경우 Windows CMD에서 install.cmd 를 수행. Step3 으로 진행.
    - Step3: claude(.exe) update 를 쉘에서 실행해서 업데이트. Step4로 진행.
    - Step4: 현재 디렉토리 기준에서 .claude/settings.local.json, .claude\settings.local.json, .claude\settings.local.json 을 찾아보고 없으면 해당 위치에 빈 파일을 생성. Step5로 진행.
    - Step5: settings.local.json 파일을 읽고 "env" 항목을 불러 온다. "env"가 없으면 Step6으로 진행. "env"가 있으면 Step7으로 진행
    - Step6: "env"에 환경 변수 값을 설정 한다.
             - "LLM_RUNTIME_SERVER": {ollama, vllm, mlx} 값을 설정 할 수 있다. Radio 버튼과 같이 화살표키를 이용해서 3개 중 하나를 고를 수 있도록 하자. (추후에 다른 LLM Runtime지원이 추가 될 수 있으니 이부분 유념하여 확장성 있도록 작성 할 것.)
             - "ANTHROPIC_BASE_URL": "http://localhost:{port}" {port}는 위 LLM Runtime의 기본 포트로 설정을 하고, 사용자가 url / 포트 번호를 수정할 수 있도록 하자.
             - "ANTHROPIC_AUTH_TOKEN": LLM_RUNTIME_SERVER 타입에 따라서 필요한 경우에 대해서만 설정 할 수 있도록 하자.
             - "ANTHROPIC_API_KEY": LLM_RUNTIME_SERVER 타입에 따라서 필요한 경우에 대해서만 설정 할 수 있도록 하자.
             - "ANTHROPIC_DEFAULT_OPUS_MODEL": LLM_RUNTIME_SERVER 으로부터 가용한 모델을 불러와서 화살표 키를 이용해서 선택 할 수 있도록 하자. ollama, vllm, mlx 마다 API가 다르니 유의 하자.
             - "ANTHROPIC_DEFAULT_SONNET_MODEL": LLM_RUNTIME_SERVER 으로부터 가용한 모델을 불러와서 화살표 키를 이용해서 선택 할 수 있도록 하자. ollama, vllm, mlx 마다 API가 다르니 유의 하자.
             - "ANTHROPIC_DEFAULT_HAIKU_MODEL": LLM_RUNTIME_SERVER 으로부터 가용한 모델을 불러와서 화살표 키를 이용해서 선택 할 수 있도록 하자. ollama, vllm, mlx 마다 API가 다르니 유의 하자.
             - "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1" 로 하자.
             - 이 외에 환경변수가 나중에 추가 될 수 있으니 유연성 있도록 작성 할 것.
             설정이 다 되면 Step8로 진행.
    - Step7: "env"에 환경 변수 값을 로드하고, 수정할지 물어 본다. (y/n). y면 Step6으로 진행. n면 Step8로 진행.
    - Step8: 새창을 열어서 현재 디랙토리와 동일 위치에서 claude(.exe)를 실행하고 본 프로그램을 종료 한다. 사용자는 새창에서 claude code를 이용해서 작업을 수행 하게 된다.
5. 명확하지 않은 부분이 있다면 반드시 나에게 문의 할것.