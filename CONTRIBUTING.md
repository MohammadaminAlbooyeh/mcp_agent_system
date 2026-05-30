# Contributing

## Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
cp .env.example .env
pip install -r requirements.txt
docker-compose up -d db
python scripts/init_db.py
```

## Code Style

- Python: Black + isort + flake8
- JavaScript: Prettier + ESLint
- Docstrings: Google style

## Testing

```bash
pytest tests/
pytest tests/unit/
pytest tests/integration/
```

## Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No new warnings
