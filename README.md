# MISIS FAQ Bot with Embeddings

Telegram bot for MISIS university freshmen with semantic FAQ search using sentence-transformers.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```
BOT_TOKEN=your_telegram_bot_token
```

3. Build embeddings index (first time only):
```bash
python build_index.py
```

4. Run the bot:
```bash
python bot.py
```

## Files

| File | Description |
|------|-------------|
| `bot.py` | Main bot with FAQ and dialog modes |
| `faq_embeddings_db.py` | Embeddings database (sentence-transformers + FAISS) |
| `build_index.py` | Script to pre-build embeddings index |
| `config.py` | Configuration |
| `data/faq.json` | FAQ data (45 questions) |

## How it works

1. **FAQ mode**: Browse categories → select question → get answer
2. **Search**: Type query → semantic search finds relevant answers
3. **Dialog mode**: Ask anything → bot finds similar FAQ entries

The bot uses `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` model for Russian language semantic search.

## FAQ Data Format

```json
{
  "dataset": [
    {
      "id": "faq_0001",
      "block": "Учебные вопросы",
      "subblock": "СТО + заказ справок", 
      "question": "Часы работы СтО?",
      "answer": "Студенческий офис работает...",
      "tags": ["учебные", "СТО", "справки"]
    }
  ]
}
```
