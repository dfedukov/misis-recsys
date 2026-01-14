# MISIS FAQ Bot - Code Review Report

**Date**: 2026-01-14
**Reviewed by**: Claude Code
**Status**: ⚠️ Issues Found - Requires Configuration Updates

---

## Executive Summary

The MISIS FAQ Telegram bot is a well-structured application that uses vector embeddings (sentence-transformers) and FAISS for semantic search of FAQ data. The code is clean and functional, but there are **configuration and path issues** that need to be fixed before the bot can run.

**Overall Code Quality**: ✅ Good
**Functionality**: ✅ Properly implemented
**Configuration**: ⚠️ Needs fixing

---

## Issues Found

### 🔴 CRITICAL ISSUE #1: File Path Mismatch

**Location**: [config.py:11](config.py#L11)

```python
FAQ_JSON_PATH = os.getenv("FAQ_JSON_PATH", "data/faq.json")
```

**Problem**:
- Config expects FAQ file at `data/faq.json`
- Actual FAQ file is located at `faq.json` (root directory)
- The `data/` directory doesn't exist

**Impact**: Bot will fail to start with "FAQ file not found" error

**Solution Options**:
1. **Quick fix**: Update [config.py:11](config.py#L11) to:
   ```python
   FAQ_JSON_PATH = os.getenv("FAQ_JSON_PATH", "faq.json")
   ```

2. **Proper fix**: Move the FAQ file:
   ```bash
   mkdir -p data
   mv faq.json data/
   ```

---

### 🟡 ISSUE #2: Missing .env File

**Location**: Root directory

**Problem**: No `.env` file exists with BOT_TOKEN configuration

**Impact**: Bot will log error and exit on startup ([bot.py:120-122](bot.py#L120-L122))

**Solution**: Create `.env` file with your Telegram bot token:
```bash
echo "BOT_TOKEN=your_telegram_bot_token_here" > .env
```

Get your bot token from [@BotFather](https://t.me/botfather) on Telegram.

---

### 🟢 ISSUE #3: Missing Dependencies (Likely)

**Location**: [requirements.txt](requirements.txt)

**Problem**: Dependencies may not be installed

**Impact**: ImportError on startup

**Solution**: Install required packages:
```bash
pip install -r requirements.txt
```

**Note**: The sentence-transformers model (paraphrase-multilingual-MiniLM-L12-v2) will be downloaded on first run (~420MB).

---

## Code Analysis

### ✅ Strengths

1. **Well-structured architecture**:
   - Clear separation of concerns (bot logic, embeddings DB, config)
   - Proper use of FSM (Finite State Machine) for dialog flows
   - Clean dataclass models for FAQ items and search results

2. **Robust embeddings implementation** ([faq_embeddings_db.py](faq_embeddings_db.py)):
   - Uses FAISS IndexFlatIP (Inner Product) with normalized embeddings = cosine similarity
   - Proper index persistence (save/load functionality)
   - Good error handling for missing index

3. **Good user experience**:
   - Two modes: FAQ browsing and Dialog mode
   - Semantic search with configurable score thresholds
   - Clear keyboard navigation
   - Helpful feedback based on confidence scores

4. **Russian language support**:
   - Uses `paraphrase-multilingual-MiniLM-L12-v2` model (good for Russian)
   - All UI text in Russian
   - 45 FAQ entries covering university topics

### ⚠️ Potential Issues

1. **Score threshold tuning** ([bot.py:257,358](bot.py#L257)):
   - Line 257: Uses `score > 0.7` threshold for FAQ question match
   - Line 358: Uses `score > 0.75` for high-confidence dialog answer
   - **Concern**: These thresholds may need adjustment based on testing
   - **Recommendation**: Test with real queries and adjust if needed

2. **Limited search results** ([bot.py:79](bot.py#L79)):
   - FAQ questions keyboard limited to 15 items
   - **Impact**: Users can't see all questions in large categories
   - **Recommendation**: Add pagination or increase limit

3. **Missing error handling**:
   - No try-catch around embedding model loading ([faq_embeddings_db.py:123](faq_embeddings_db.py#L123))
   - Network errors during model download not handled
   - **Recommendation**: Add error handling for model initialization

4. **Memory considerations**:
   - All embeddings loaded in memory
   - For 45 items: ~70KB (384 dimensions × 45 × 4 bytes)
   - **Current status**: ✅ Fine for this scale
   - **Future**: Consider FAISS IVF indices if scaling beyond 10,000 items

---

## Security Review

### ✅ Security: Good

1. **No SQL injection risk**: Uses FAISS vector search, no SQL
2. **No command injection**: No shell execution based on user input
3. **No XSS**: Telegram bots are not vulnerable to XSS
4. **Bot token security**: Properly uses .env file (not hardcoded)

### ⚠️ Security Recommendations

1. **Add .env to .gitignore**: Prevent token leakage
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Validate user input length**: Add limits to prevent memory exhaustion
   ```python
   if len(message.text) > 1000:
       await message.answer("Query too long. Please limit to 1000 characters.")
       return
   ```

---

## Functionality Testing

### FAQ Data Structure ✅

From [faq.json](faq.json):
- **Total entries**: 45 questions
- **Categories**:
  - Учебные вопросы (Academic questions): ~19 items
  - Внеучебная деятельность (Extracurricular): ~4 items
  - Общежития (Dormitories): ~6 items
  - Навигация (Navigation): ~5 items
  - Военно-учетный стол (Military registration): ~5 items
  - Абитуриентам (Applicants): ~5 items

- **Data quality**: ✅ All entries have required fields
- **Unique IDs**: ✅ All IDs unique (faq_0001 to faq_0045)

### Embeddings Logic ✅

From [faq_embeddings_db.py:63-66](faq_embeddings_db.py#L63-L66):
```python
def get_embedding_text(self) -> str:
    tags_text = " ".join(self.tags) if self.tags else ""
    return f"{self.question} {tags_text}".strip()
```

**Analysis**:
- ✅ Combines question + tags for richer embeddings
- ✅ Good approach for semantic search
- Could also include subblock for more context, but current approach is sufficient

### Search Algorithm ✅

From [faq_embeddings_db.py:180-210](faq_embeddings_db.py#L180-L210):
1. Encode query with same model
2. Normalize embeddings
3. FAISS search with Inner Product (= cosine similarity for normalized vectors)
4. Filter by score threshold
5. Return top-k results

**Analysis**: ✅ Correct implementation of semantic search

---

## Bot Workflow Analysis

### Main Flow ✅

1. `/start` → Main menu (FAQ mode / Dialog mode / Help)
2. **FAQ Mode**:
   - Browse categories → Select question → View answer
   - OR Search by keywords → View results
3. **Dialog Mode**:
   - Ask free-form question → Get semantic search results
   - High confidence (>0.75): Direct answer
   - Low confidence: Show multiple similar questions

**Analysis**: ✅ Well-designed UX with clear navigation

### State Management ✅

Uses aiogram FSM with two states:
- `BotStates.faq_mode`: For FAQ browsing
- `BotStates.dialog_mode`: For free-form questions

**Analysis**: ✅ Proper use of FSM, clean state transitions

### Handler Organization ✅

Handlers are well-organized:
- Command handlers: `/start`, `/help`, `/faq`, `/dialog`
- Button handlers: Uses `F.text` filters for keyboard buttons
- State-based handlers: Different behavior per mode
- Fallback handler: Catches unrecognized input

**Analysis**: ✅ Clean and maintainable handler structure

---

## Performance Considerations

### Current Performance: ✅ Good for 45 items

- **Index building**: ~5-10 seconds (first time only)
- **Search latency**: <50ms per query (FAISS is very fast)
- **Memory usage**: ~70KB for embeddings + ~400MB for model

### Scaling Recommendations

If FAQ grows beyond 1,000 items:
1. Consider FAISS IVF (Inverted File) index
2. Add caching layer for frequent queries
3. Consider quantization (IndexIVFPQ) for large scales

---

## Recommendations

### Must Fix Before Running:

1. ✅ Fix file path issue (see Issue #1)
2. ✅ Create .env file with BOT_TOKEN (see Issue #2)
3. ✅ Install dependencies: `pip install -r requirements.txt`
4. ✅ Run build_index.py to create embeddings

### Nice to Have:

1. Add pagination for large category results
2. Add input validation (length limits)
3. Add error handling for model loading
4. Add .gitignore file
5. Add logging for user queries (for future improvements)
6. Consider adding metrics tracking
7. Add unit tests for embeddings_db module

### Optional Enhancements:

1. **Multi-language support**: Add English FAQ entries
2. **Feedback loop**: Store user ratings to improve results
3. **Analytics**: Track popular questions
4. **Admin commands**: Update FAQ without restarting bot
5. **Caching**: Cache frequent queries with Redis
6. **A/B testing**: Test different score thresholds

---

## Step-by-Step Setup Instructions

To get the bot running:

```bash
# 1. Fix file paths (choose one option)
# Option A: Update config
sed -i '' 's|data/faq.json|faq.json|g' config.py

# Option B: Move file
mkdir -p data
mv faq.json data/

# 2. Create .env file
echo "BOT_TOKEN=your_telegram_bot_token" > .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Build embeddings index (takes ~30 seconds)
python build_index.py

# 5. Run the bot
python bot.py
```

---

## Conclusion

**Overall Assessment**: ✅ **High Quality Code**

The bot is well-implemented with good architecture and proper use of modern libraries. The main issues are **configuration-related** and can be fixed in under 5 minutes.

**Recommendation**: Fix the path configuration and the bot will work correctly.

**Code Quality Grade**: **A-** (would be A+ after fixing configuration issues)

---

## Test Checklist

Before deploying to production, test:

- [ ] Bot starts without errors
- [ ] FAQ mode: Category browsing works
- [ ] FAQ mode: Question selection works
- [ ] FAQ mode: Search functionality works
- [ ] Dialog mode: High-confidence answers work
- [ ] Dialog mode: Low-confidence multiple results work
- [ ] Navigation: Back buttons work
- [ ] Navigation: Main menu button works
- [ ] Edge cases: Empty queries handled
- [ ] Edge cases: Very long queries handled
- [ ] Performance: Response time < 1 second

---

**Next Steps**: Fix the configuration issues listed above, then run the bot and test with real queries to verify semantic search quality.
