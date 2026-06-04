

# Backend
mkdir backend
mkdir backend\app
mkdir backend\app\agents
mkdir backend\app\tools
mkdir backend\app\integrations
mkdir backend\app\memory
mkdir backend\app\llm
mkdir backend\app\api
mkdir backend\app\db
mkdir backend\app\tasks
mkdir backend\app\prompts
mkdir backend\tests
mkdir backend\tests\mocks

# Frontend
mkdir frontend
mkdir frontend\src
mkdir frontend\src\app
mkdir frontend\src\app\settings
mkdir frontend\src\components
mkdir frontend\src\hooks
mkdir frontend\src\lib

# Infrastructure
mkdir infra
mkdir infra\github-actions
mkdir infra\nginx

# Backend Files
ni backend\app\agents\orchestrator.py -ItemType File
ni backend\app\agents\planner.py -ItemType File
ni backend\app\agents\tool_router.py -ItemType File
ni backend\app\agents\hitl_gate.py -ItemType File

ni backend\app\tools\email_tool.py -ItemType File
ni backend\app\tools\calendar_tool.py -ItemType File
ni backend\app\tools\task_tool.py -ItemType File
ni backend\app\tools\search_tool.py -ItemType File
ni backend\app\tools\file_tool.py -ItemType File
ni backend\app\tools\base_tool.py -ItemType File

ni backend\app\integrations\gmail.py -ItemType File
ni backend\app\integrations\google_calendar.py -ItemType File
ni backend\app\integrations\slack.py -ItemType File
ni backend\app\integrations\jira.py -ItemType File
ni backend\app\integrations\github.py -ItemType File
ni backend\app\integrations\notion.py -ItemType File
ni backend\app\integrations\base_integration.py -ItemType File

ni backend\app\memory\short_term.py -ItemType File
ni backend\app\memory\long_term.py -ItemType File
ni backend\app\memory\memory_manager.py -ItemType File

ni backend\app\llm\base_llm.py -ItemType File
ni backend\app\llm\gemini.py -ItemType File
ni backend\app\llm\claude.py -ItemType File

ni backend\app\api\chat.py -ItemType File
ni backend\app\api\auth.py -ItemType File
ni backend\app\api\integrations.py -ItemType File
ni backend\app\api\health.py -ItemType File

ni backend\app\db\models.py -ItemType File
ni backend\app\db\schemas.py -ItemType File
ni backend\app\db\session.py -ItemType File

ni backend\app\tasks\email_watcher.py -ItemType File
ni backend\app\tasks\reminders.py -ItemType File
ni backend\app\tasks\briefing.py -ItemType File

ni backend\app\prompts\system_prompt.txt -ItemType File
ni backend\app\prompts\email_drafter.txt -ItemType File
ni backend\app\prompts\daily_briefing.txt -ItemType File

ni backend\app\main.py -ItemType File

ni backend\tests\test_agents.py -ItemType File
ni backend\tests\test_tools.py -ItemType File
ni backend\tests\test_integrations.py -ItemType File

ni backend\requirements.txt -ItemType File
ni backend\requirements-dev.txt -ItemType File
ni backend\Dockerfile -ItemType File
ni backend\.env.example -ItemType File

# Frontend Files
ni frontend\src\app\page.tsx -ItemType File
ni frontend\src\app\layout.tsx -ItemType File

ni frontend\src\components\ChatWindow.tsx -ItemType File
ni frontend\src\components\MessageBubble.tsx -ItemType File
ni frontend\src\components\ConfirmAction.tsx -ItemType File
ni frontend\src\components\IntegrationCard.tsx -ItemType File

ni frontend\src\hooks\useWebSocket.ts -ItemType File
ni frontend\src\hooks\useChat.ts -ItemType File

ni frontend\src\lib\api.ts -ItemType File

ni frontend\package.json -ItemType File
ni frontend\Dockerfile -ItemType File

# Infrastructure Files
ni infra\github-actions\ci.yml -ItemType File
ni infra\github-actions\deploy.yml -ItemType File
ni infra\nginx\nginx.conf -ItemType File

# Root Files
ni docker-compose.yml -ItemType File
ni docker-compose.prod.yml -ItemType File
ni .env.example -ItemType File
ni .gitignore -ItemType File
ni README.md -ItemType File

Write-Host "AI Secretary project structure created successfully!"