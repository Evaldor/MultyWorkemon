# API Request Examples

## AI-Secretary

### Analyze Request
```bash
curl "http://localhost:8000/analyze-request?channel=email&username=smirnovanton&request=Я хочу получать аналитику о операциях наших кошельков&department=Департамент клиентского сервиса&position=младший аналитик"
```

### Health Check
```bash
curl http://localhost:8000/health
```

## AI-Guesser

### Get Context
```bash
curl "http://localhost:8001/get-context?username=smirnovanton&department=Департамент клиентского сервиса&position=младший аналитик&request=Я хочу получать аналитику о операциях наших кошельков"
```

### Health Check
```bash
curl http://localhost:8001/health
```

## AI-SystemAnalitic

### Prepare Analytics
```bash
curl "http://localhost:8002/prepare-analititcs?preparedcontext=Младший системный аналитик из клиентского департамента хочет сформировать срезы по авторизационным операциям кошельков, это домен b2c.&request=Я хочу получать аналитику о операциях наших кошельков. Контекста не достаточно, вас интетесуют движения средств или все операции типа авторизаций и прочего? Меня интересуют операции авторизации"
```

### Health Check
```bash
curl http://localhost:8002/health
```

## AI-Communicator

### Health Check
```bash
curl http://localhost:8003/health