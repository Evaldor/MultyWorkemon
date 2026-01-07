# MultyWorkemon

## Promt

Напиши на python решение состоящее из совокупности statless микросервисов упакованных в docker контейнеры. каждый из микросервисов реализует лоирование в kibana и healthcheck в графану.

API keys and endpoints are in environment variables or config files; 

Provide specific examples: Yandex IMAP server, Telegram bot token, REST API endpoint, LLM API keys, Jira base URL; saved prompt is configurable

No specific credentials yet, use placeholders; saved prompt is hard-coded in code

## Список сервисов


![Схема взаимодействия](https://github.com/Evaldor/MultyWorkemon/raw/main/microservice.jpg)

### AI-communicator

Отвечает за коммуникацию с пользователями. Сервис проверяет новые письма почтовом ящике yandex, сообщения полученные через месенджер telegarm и отпраляет их в качестве запроса в метод analyze-request API AI-Secretary. 

### AI-Secretary

Отвечает за оркестрацию происходящего и основну бизнес логику процесса.
сервис реализован как API. Сохраняет историю запросов и ответов в бд PostgeSQL

получив запрос на метод analyze-request сервис перенаправляет его на метод get-context API AI-Guesser
если в ответе от AI-Guesser конекст определен, то запрос обогащенный контекстом отправляется в метод prepare-analititcs API AI-SystemAnalitic а полученный ответ отдвет в качестве ответа тому кто обратился к analyze-request.


openapi: 3.0.0
info:
  title: Support Context Analyzer API
  description: API для анализа контекста обращений и определения необходимых действий
  version: 1.0.0

paths:
  /analyze-request:
    get:
      summary: Анализ входящего обращения и определение необходимых действий
      description: |
        Анализирует входящее обращение и определяет, достаточно ли информации для ответа,
        какое действие требуется выполнить, и формирует ответ или уточняющий вопрос.
      parameters:
        - name: channel
          in: query
          description: Канал поступления обращения
          required: true
          schema:
            type: string
            enum: [email, tg, direct]
          example: email
        - name: username
          in: query
          description: Имя пользователя, от которого пришло обращение
          required: true
          schema:
            type: string
          example: "smirnovanton"
        - name: request
          in: query
          description: Текст обращения пользователя
          required: true
          schema:
            type: string
          example: "Я хочу получать аналитику о операциях наших кошельков"
      responses:
        '200':
          description: Успешный анализ обращения
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AnalysisResponse'
        '400':
          description: Неверные параметры запроса
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Внутренняя ошибка сервера
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  schemas:
    AnalysisResponse:
      type: object
      required:
        - is_enough
        - request
        - action
        - question
        - response
      properties:
        is_enough:
          type: boolean
          description: Достаточно ли информации для определения контекста
          example: false
        request:
          type: string
          description: Полный текст изначального запроса
          example: "Я хочу получать аналитику о операциях наших кошельков"
        action:
          type: string
          description: Требуемое действие
          enum:
            - уточнить
            - ответить сообщением
            - создать jira-task
            - написать в telegram сотруднику
            - ответить на письмо
            - написать в рассылку департамента
          example: уточнить
        question:
          type: string
          description: Уточняющий вопрос, если он есть
          example: "Уточните аналатику каких операций?"
        context-response:
          type: string
          description: Сформированный ответ
          example: "Для получения такой аналитики вам необходимо обратиться к аналитическому кубу."
      example:
        is_enough: false
        request: "Я хочу получать аналитику о операциях наших кошельков"
        action: "уточнить"
        question: "Уточните аналатику каких операций?"
        response: "Для получения такой аналитики вам необходимо обратиться к аналитическому кубу."

    ErrorResponse:
      type: object
      properties:
        error:
          type: string
          description: Описание ошибки
        message:
          type: string
          description: Детальное сообщение об ошибке
        statusCode:
          type: integer
          description: HTTP код статуса
      example:
        error: "Bad Request"
        message: "Parameter 'channel' must be one of: email, tg, direct"
        statusCode: 400


### AI-Guesser

 сервис реализован как API. получает входящий запрос через метод API. к информации из тела запроса добавляет фиксированный промт и отправляет в нейросеть LLM yandex-gpt, deepseek, grock или любую другую. возвращает полученный ответ.

 saved prompt is a fixed string like 'Ты системный аналитик в финтехе, определи запрос пользователя достаточне для того чтобы понять в какой предметной области находится то что ему интересно?'

 paths:
  /get-context:
    get:
      summary: Определение контекста обращения
      description: |
        Определение контекста обращения на основе текста обращения и атрибутов обратившегося пользователя
      parameters:
        - name: username
          in: query
          description: Имя пользователя, от которого пришло обращение
          required: true
          schema:
            type: string
          example: "smirnovanton"
        - department: department
          in: query
          description: организационная единица к которой пренадлежит пользователь
          required: true
          schema:
            type: string
          example: "Департамент клиентского сервиса"
        - position: position
          in: query
          description: должность пользователя
          required: true
          schema:
            type: string
          example: "младший аналитик"
        - name: request
          in: query
          description: Текст обращения пользователя
          required: true
          schema:
            type: string
          example: "Я хочу получать аналитику о операциях наших кошельков"
      responses:
        '200':
          description: Успешный анализ обращения
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ContextResponse'
        '400':
          description: Неверные параметры запроса
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Внутренняя ошибка сервера
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  schemas:
    ContextResponse:
      type: object
      required:
        - is_enough
        - response
      properties:
        is_enough:
          type: boolean
          description: Достаточно ли информации для определения контекста
          example: false
        response:
          type: string
          description: Сформированный ответ
          example: "Контекста не достаточно, вас интетесуют движения средств или все операции типа авторизаций и прочего?"
      example:
        is_enough: false
        response: "Контекста не достаточно, вас интетесуют движения средств или все операции типа авторизаций и прочего?"

    ErrorResponse:
      type: object
      properties:
        error:
          type: string
          description: Описание ошибки
        message:
          type: string
          description: Детальное сообщение об ошибке
        statusCode:
          type: integer
          description: HTTP код статуса
      example:
        error: "Bad Request"
        message: "Requiered paremeter is missing"
        statusCode: 400

### AI-SystemAnalitic

 сервис реализован как API. получает входящий запрос через метод API. к информации из тела запроса добавляет фиксированный промт и отправляет в нейросеть LLM yandex-gpt, deepseek, grock или любую другую. возвращает полученный ответ.

saved prompt is a fixed string like 'Ты инденер данных в финтехе, посоветуй в каких компонентах истемы надо сделать операции и какие, для того чтобы дать польователю то что он хочет?'

paths:
  /prepare-analititcs:
    get:
      summary: Определение совокупности действий или компонентов
      description: |
        Определение совокупности действий или компонентов которые нудно проанализировать для того чтобы ответить пользователю
      parameters:
        - context: preparedcontext
          in: query
          description: описание контекста обращения
          required: true
          schema:
            type: string
            example: "Младший системный аналитик из клиентского департамента хочет сформировать срезы по авторизационным операциям кошельков, это домен b2c."
        - name: request
          in: query
          description: Текст обращения пользователя
          required: true
          schema:
            type: string
          example: "Я хочу получать аналитику о операциях наших кошельков. Контекста не достаточно, вас интетесуют движения средств или все операции типа авторизаций и прочего? Меня интересуют операции авторизации "
      responses:
        '200':
          description: Успешный анализ обращения
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ContextResponse'
        '400':
          description: Неверные параметры запроса
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Внутренняя ошибка сервера
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  schemas:
    ContextResponse:
      type: object
      required:
        - is_enough
        - response
      properties:
        is_enough:
          type: boolean
          description: Достаточно ли информации для формирования преданалитики
          example: true
        response:
          type: string
          description: Сформированный ответ
          example: "Для подобной построения такого среза можно совершить доработку аналитического куба авторизаций, добавив туда статус авторизации и выполнить следующий запрос к кубу"
      example:
        is_enough: true
        response: "Для подобной построения такого среза можно совершить доработку аналитического куба авторизаций, добавив туда статус авторизации и выполнить следующий запрос к кубу"

    ErrorResponse:
      type: object
      properties:
        error:
          type: string
          description: Описание ошибки
        message:
          type: string
          description: Детальное сообщение об ошибке
        statusCode:
          type: integer
          description: HTTP код статуса
      example:
        error: "Bad Request"
        message: "Requiered paremeter is missing"
        statusCode: 400
  

## Setup Instructions

1. Ensure Docker and Docker Compose are installed.

2. Clone or navigate to the project directory.

3. For each service, update the `.env` files with actual credentials:
   - `services/ai-secretary/.env`: Set DATABASE_URL to your PostgreSQL connection string.
   - `services/ai-guesser/.env`: Set LLM_API_KEY and other LLM settings.
   - `services/ai-systemanalitic/.env`: Same as ai-guesser.
   - `services/ai-communicator/.env`: Set EMAIL, PASSWORD, TELEGRAM_BOT_TOKEN.

4. Build and run the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

5. Services will be available on:
   - AI-Secretary: http://localhost:8000
   - AI-Guesser: http://localhost:8001
   - AI-SystemAnalitic: http://localhost:8002
   - AI-Communicator: http://localhost:8003

6. For logging to Kibana, ensure logs are forwarded to Elasticsearch (e.g., via Filebeat).

7. For healthchecks in Grafana, configure Prometheus to scrape the /health endpoints and Grafana to visualize.

See `examples.md` for API usage examples.

## Local Development Setup

For running each service locally without Docker, follow these instructions for each service. Ensure Python 3.9+ is installed, and set up virtual environments for each service to avoid dependency conflicts.

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- For AI-Secretary: PostgreSQL database (or SQLite for local testing)

### AI-Secretary (Port 8000)

1. Navigate to the service directory:
   ```bash
   cd services/ai-secretary
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Update `.env` file with your configuration (database URL, etc.).

5. Run the service:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

6. Health check: `curl http://localhost:8000/health`

### AI-Guesser (Port 8001)

1. Navigate to the service directory:
   ```bash
   cd services/ai-guesser
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Update `.env` file with LLM API key and endpoint.

5. Run the service:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8001 --reload
   ```

6. Health check: `curl http://localhost:8001/health`

### AI-SystemAnalitic (Port 8002)

1. Navigate to the service directory:
   ```bash
   cd services/ai-systemanalitic
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Update `.env` file with LLM API key and endpoint.

5. Run the service:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8002 --reload
   ```

6. Health check: `curl http://localhost:8002/health`

### AI-Communicator (Port 8003)

1. Navigate to the service directory:
   ```bash
   cd services/ai-communicator
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Update `.env` file with Yandex IMAP credentials, Telegram bot token, and AI-Secretary URL.

5. Run the service:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8003 --reload
   ```

6. Health check: `curl http://localhost:8003/health`

### Notes
- Use `--reload` for development to automatically restart on code changes.
- Ensure all services are running and accessible by others (e.g., AI-Communicator needs AI-Secretary).
- For AI-Secretary, if using SQLite for local development, set `DATABASE_URL=sqlite:///./test.db` in `.env`.
- Deactivate virtual environments with `deactivate` when done.