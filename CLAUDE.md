# MinDat Scraper - crawl4ai Migration Project

## Project Overview
This project involves migrating the existing MinDat mineral scraper from requests/BeautifulSoup to crawl4ai for enhanced web scraping capabilities, better image extraction, and improved performance.

## Current Architecture
- **Language**: Python 3.12+
- **Current Dependencies**: requests, beautifulsoup4
- **Target Architecture**: crawl4ai-based scraper with concurrent processing
- **Data Sources**: mindat.org mineral database

## Project Structure
```
MinDatScraper/
├── main.py                 # Current scraper implementation
├── pyproject.toml          # Project dependencies
├── data/                   # JSON data storage
├── images/                 # Downloaded mineral images
├── logs/                   # Scraping reports and logs
└── CLAUDE.md              # This file - project instructions
```

## Learning Objectives
By completing this project, you will learn:
1. How to migrate from traditional scraping to modern crawl4ai
2. Implementing concurrent web scraping safely
3. Advanced image extraction and filtering techniques
4. Error handling and retry mechanisms in web scraping
5. Performance optimization for large-scale scraping

## Implementation Phases

### Phase 1: Research & Setup
**Goal**: Understand crawl4ai and prepare the environment

**Tasks**:
1. Research crawl4ai capabilities and installation
2. Update project dependencies
3. Understand crawl4ai vs requests/BeautifulSoup differences

**Key Learning Points**:
- crawl4ai async capabilities
- Built-in browser automation
- Enhanced content extraction

### Phase 2: Core Migration
**Goal**: Replace the core scraping engine

**Tasks**:
1. Refactor MindatScraper class initialization
2. Replace HTTP requests with crawl4ai calls
3. Update HTML parsing logic
4. Fix existing bugs (sanitize_filename typo)

**Key Learning Points**:
- Async/await patterns in Python
- Browser automation vs HTTP requests
- Modern web scraping best practices

### Phase 3: Enhanced Features
**Goal**: Leverage crawl4ai advanced capabilities

**Tasks**:
1. Implement enhanced image extraction
2. Add image quality filtering
3. Implement concurrent processing
4. Add advanced error handling

**Key Learning Points**:
- Image processing and filtering
- Concurrent programming patterns
- Robust error handling strategies

### Phase 4: Testing & Optimization
**Goal**: Ensure reliability and performance

**Tasks**:
1. Test with existing mineral list
2. Add comprehensive logging
3. Performance monitoring and optimization
4. Documentation updates

**Key Learning Points**:
- Testing scraping applications
- Performance profiling
- Production-ready error handling

## Technical Specifications

### Current Dependencies
```toml
dependencies = [
    "beautifulsoup4>=4.13.4",
    "requests>=2.32.4",
]
```

### Target Dependencies
```toml
dependencies = [
    "crawl4ai>=0.2.77",
    "aiofiles>=23.0.0",
    "pillow>=10.0.0",  # For image processing
]
```

### Key Classes to Implement
1. **AsyncMindatScraper**: Main scraper class using crawl4ai
2. **ImageProcessor**: Handle image filtering and quality assessment
3. **ConcurrentManager**: Manage concurrent scraping operations
4. **EnhancedLogger**: Improved logging and progress tracking

## Development Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints throughout
- Implement proper async/await patterns
- Add comprehensive docstrings

### Error Handling
- Implement exponential backoff for retries
- Handle network timeouts gracefully
- Log all errors with context
- Maintain robots.txt compliance

### Performance Targets
- Process 100+ minerals concurrently (respecting rate limits)
- 90%+ success rate for image extraction
- < 2 minutes total processing time for test dataset
- Memory usage < 500MB during operation

## Testing Strategy
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Full pipeline testing
3. **Performance Tests**: Concurrent load testing
4. **Compliance Tests**: robots.txt and rate limiting validation

## Mentor Guidance Protocol
- I will guide you through each implementation step
- You must explicitly request code changes
- I will provide examples and explanations for each concept
- Ask questions at any point for clarification
- We'll test each phase before proceeding to the next

## Success Criteria
✅ Successfully migrate to crawl4ai
✅ Implement concurrent processing
✅ Achieve 90%+ scraping success rate
✅ Extract high-quality mineral images
✅ Maintain ethical scraping practices
✅ Complete comprehensive testing

## Getting Started
Run the following command to begin Phase 1:
```bash
# Let's start by researching crawl4ai together
python -c "print('Ready to begin crawl4ai migration!')"
```

## Resources
- crawl4ai Documentation: https://crawl4ai.com/mkdocs/
- Python Async Programming: https://docs.python.org/3/library/asyncio.html
- Web Scraping Ethics: https://blog.apify.com/web-scraping-ethics/

---
**Note**: This is a learning-focused implementation. Each step will be explained and demonstrated before implementation.