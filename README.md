# YouTube & Twitch Channel Scraper

An advanced web scraper that finds YouTube and Twitch channels for users based on their X (Twitter) profile data. Uses sophisticated matching algorithms and parallel processing for efficient channel discovery.

## 🚀 Features

- **Sophisticated Matching**: Uses enhanced matching logic extracted from banana scraper with title verification, abbreviation patterns, and word-based matching
- **Parallel Processing**: Configurable worker threads (1-10) for concurrent processing
- **Proxy Rotation**: Built-in proxy management with failure tracking
- **Resume Capability**: Can resume interrupted processing from where it left off
- **Multiple Search Strategies**: URL extraction fallback when profile names don't match channel names
- **Rate Limiting**: Smart delays to avoid getting blocked
- **Comprehensive Logging**: Detailed logging with configurable verbosity

## 📁 Project Structure

```
voice/
├── data/
│   └── 3_snapshot_s_mepo7m7c1bhrdvfkc6_external_links(without_YT_twitch).csv
├── proxy/
│   └── Free_Proxy_List.csv
├── v1/                          # Python virtual environment
├── youtube_twitch_scraper.py    # Main scraper
├── enhanced_matching.py         # Sophisticated matching logic  
├── config.py                    # Configuration settings
├── youtube_twitch_results_enhanced.csv  # Output results (generated)
└── README.md
```

## 🛠 Installation

1. **Clone/Download** the project to your local machine

2. **Set up Python virtual environment**:
   ```bash
   python -m venv v1
   v1\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install crawl4ai pandas beautifulsoup4 aiohttp aiofiles asyncio
   ```

## 📊 Input Data Format

The scraper expects a CSV file with the following columns:
- `username`: X/Twitter username
- `profile_name`: Display name on X/Twitter
- `url`: Profile URL
- `followers`: Follower count

Example:
```csv
username,profile_name,url,followers
kirstnicolexo,kirstie (taylor's version),http://brokenblame.tumblr.com/,350
aliceyinyang,melis |,https://instagram.com/lifeisaroadtrip_/,957
```

## 🚀 Usage

### Basic Usage
```bash
python youtube_twitch_scraper.py
```

### With Custom Worker Count
```bash
python youtube_twitch_scraper.py --workers 5
```

### Interactive Mode
The scraper will prompt you to select the number of parallel workers (1-10) for processing.

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Matching thresholds
MATCH_THRESHOLD = 50  # Minimum score for accepting matches

# Rate limiting
SEARCH_DELAY = (2, 4)  # Random delay between searches (min, max seconds)
BATCH_DELAY = (1, 3)   # Delay between batches

# Search limits
MAX_RESULTS_PER_QUERY = 5  # Top N results to analyze per search

# Proxy settings
PROXY_TIMEOUT = 15  # Proxy timeout in seconds
MAX_PROXY_RETRIES = 3  # Maximum retries per proxy
```

## 🔍 How It Works

### 1. Enhanced Matching System
- **Title Verification**: Fetches page titles to verify matches
- **Abbreviation Patterns**: Recognizes abbreviations (e.g., "ny" for "new york")
- **Word-based Matching**: Matches individual words within names
- **Containment Checks**: Flexible substring matching with thresholds
- **URL Analysis**: Extracts potential names from profile URLs

### 2. Search Strategy
1. **Primary Search**: Uses original username and profile name
2. **URL Fallback**: Extracts name from profile URL if no good matches
3. **Multiple Queries**: Tests different combinations of available names
4. **Early Exit**: Stops searching when good match found (score ≥ 50)

### 3. Parallel Processing
- **Worker Pools**: Configurable concurrent workers (1-10)
- **Load Balancing**: Distributes users across workers
- **Shared State**: Thread-safe result saving and progress tracking
- **Error Isolation**: Individual worker failures don't stop others

## 📈 Output Format

Results are saved to `results/youtube_twitch_results_enhanced.csv`:

```csv
username,profile_name,url,followers,youtube_url,youtube_score,twitch_url,twitch_score
kirstnicolexo,kirstie (taylor's version),http://brokenblame.tumblr.com/,350,https://www.youtube.com/@_kirstynicole_,70,,0
```

### Score Interpretation
- **0**: No match found
- **50-69**: Moderate confidence match
- **70-85**: High confidence match
- **85+**: Very high confidence match

## 🛡️ Proxy Management

The scraper includes robust proxy management:
- **Automatic Rotation**: Cycles through available proxies
- **Failure Tracking**: Removes non-working proxies
- **Format Support**: HTTP and HTTPS proxies
- **Timeout Handling**: Configurable timeouts per proxy

## 🔧 Advanced Features

### Resume Processing
If interrupted, the scraper automatically resumes from where it left off by checking existing results.

### URL Name Extraction
When profile names don't match channel names, the scraper extracts potential names from profile URLs:
- `https://x.com/username` → `username`
- `https://twitter.com/profile_name/status/123` → `profile_name`

### Smart Rate Limiting
- Random delays between searches (2-4 seconds)
- Longer delays between user batches
- Proxy rotation to distribute load

## 📊 Performance

### Success Rates
Success rates depend on:
- Quality of input data (username/profile name accuracy)
- Proxy reliability and speed
- Platform availability and structure
- Matching threshold settings (currently set to 50)

### Processing Speed
Processing speed varies based on:
- Number of parallel workers (1-10 configurable)
- Proxy response times
- Search result complexity
- Rate limiting delays

Run the scraper on your dataset to get actual performance metrics.

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install --upgrade crawl4ai pandas beautifulsoup4 aiohttp
   ```

2. **Proxy Issues**
   - Update `proxy/Free_Proxy_List.csv` with fresh proxies
   - Reduce worker count if proxies are failing

3. **Rate Limiting**
   - Increase delays in `config.py`
   - Use fewer workers
   - Get better proxy list

4. **Memory Issues**
   - Reduce worker count
   - Process smaller batches

### Logs
Check logs for detailed error information:
- Successful matches are logged at INFO level
- Errors and warnings provide troubleshooting details
- Debug level shows detailed matching process

## 📝 Notes

- **Ethical Usage**: Respects rate limits and uses delays
- **Proxy Dependent**: Quality of results depends on proxy reliability  
- **Platform Changes**: May need updates if YouTube/Twitch change their layouts
- **False Positives**: Review results with lower scores manually

## 🔄 Updates & Maintenance

### Regular Maintenance
1. Update proxy list monthly
2. Monitor success rates
3. Adjust thresholds based on results
4. Update dependencies

### Extending Functionality
- Add more platforms (TikTok, Instagram, etc.)
- Implement machine learning matching
- Add result validation features
- Create web interface

## 📞 Support

For issues or questions:
1. Check logs for error details
2. Verify input data format
3. Test with smaller datasets first
4. Update proxy list if needed

---

**Last Updated**: August 29, 2025  
**Version**: 2.0 (Parallel Processing Edition)
