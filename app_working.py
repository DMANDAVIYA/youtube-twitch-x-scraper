#!/usr/bin/env python3
"""
Streamlit App using the EXACT working scraper logic - SYNCHRONOUS VERSION
Same sophisticated matching, same query logic, same everything - just sync
"""

import streamlit as st
import pandas as pd
import os
import io
import time
import tempfile
import requests
import random
import re
import logging
from datetime import datetime
from urllib.parse import quote_plus, unquote
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fake_useragent import UserAgent

# Import the enhanced matching
from enhanced_matching import EnhancedMatcher
import config

# Configure Streamlit page
st.set_page_config(
    page_title="YouTube & Twitch Channel Finder",
    page_icon="🔍",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #F8D7DA;
        border: 1px solid #F5C6CB;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class SyncProxyManager:
    """Synchronous proxy manager"""
    
    def __init__(self, proxy_file: str):
        self.proxy_file = proxy_file
        self.proxies = []
        self.current_index = 0
        self.failed_proxies = set()
        self.load_proxies()
    
    def load_proxies(self):
        """Load and shuffle proxy list"""
        try:
            if os.path.exists(self.proxy_file):
                proxy_df = pd.read_csv(self.proxy_file)
                for _, row in proxy_df.iterrows():
                    proxy = {
                        'http': f"http://{row['ip']}:{row['port']}",
                        'https': f"http://{row['ip']}:{row['port']}"
                    }
                    self.proxies.append(proxy)
                
                random.shuffle(self.proxies)
                st.info(f"Loaded {len(self.proxies)} proxies")
        except Exception as e:
            st.warning(f"Error loading proxies: {e}")
            self.proxies = []
    
    def get_next_proxy(self):
        """Get next working proxy in rotation"""
        if not self.proxies:
            return None
        
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            proxy_key = f"{proxy['http']}"
            if proxy_key not in self.failed_proxies:
                return proxy
            
            attempts += 1
        
        return None
    
    def mark_proxy_failed(self, proxy):
        """Mark a proxy as failed"""
        if proxy:
            proxy_key = f"{proxy['http']}"
            self.failed_proxies.add(proxy_key)


class SyncSearchEngine:
    """Synchronous search engine using the EXACT same logic as the original"""
    
    def __init__(self, proxy_manager: SyncProxyManager):
        self.proxy_manager = proxy_manager
        self.session = self._create_session()
    
    def _create_session(self):
        """Create requests session with retry strategy and rotating user agents"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Use fake-useragent for proper user agent rotation
        ua = UserAgent()
        session.headers.update({
            'User-Agent': ua.random
        })
        return session
    
    def search_with_requests(self, query: str, platform: str, max_results: int = 5):
        """Search using requests - EXACT same logic as crawl4ai version"""
        max_proxy_attempts = 3
        
        for attempt in range(max_proxy_attempts):
            proxy = self.proxy_manager.get_next_proxy()
            
            try:
                # Create search URL - EXACT same as original
                if platform == "youtube":
                    search_url = f"https://www.google.com/search?q={quote_plus(query + ' youtube channel')}"
                else:  # twitch
                    search_url = f"https://www.google.com/search?q={quote_plus(query + ' twitch')}"
                
                st.info(f"🔍 Searching: {query} on {platform}")
                
                # Configure request with proxy
                request_kwargs = {'timeout': 15}
                if proxy:
                    request_kwargs['proxies'] = proxy
                
                # Add delay like original
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(search_url, **request_kwargs)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Check for bot detection
                    if "Our systems have detected unusual traffic" in response.text:
                        st.error("❌ Google detected unusual traffic")
                        if proxy:
                            self.proxy_manager.mark_proxy_failed(proxy)
                        continue
                    
                    results = []
                    
                    # Try multiple selectors for Google search results - EXACT same as original
                    search_result_selectors = [
                        'div.g',           # Standard Google result
                        'div[data-ved]',   # Alternative selector
                        '.yuRUbf',         # Another common selector
                        'div.tF2Cxc'      # Yet another selector
                    ]
                    
                    search_divs = []
                    for selector in search_result_selectors:
                        search_divs = soup.select(selector)
                        if search_divs:
                            st.info(f"Found {len(search_divs)} results with selector: {selector}")
                            break
                    
                    if not search_divs:
                        # DIRECT LINK EXTRACTION - EXACT same as original
                        st.info(f"Using direct link extraction for {platform}")
                        all_links = soup.find_all('a', href=True)
                        platform_links = []
                        
                        for link in all_links:
                            href = link.get('href', '')
                            text = link.get_text().strip()
                            
                            # Check if it's a platform URL - EXACT same logic
                            is_platform_url = False
                            if platform == 'youtube' and 'youtube.com' in href:
                                # Filter out non-channel URLs - EXACT same
                                if any(path in href for path in ['/watch?', '/shorts/', '/playlist?']):
                                    continue
                                is_platform_url = True
                            elif platform == 'twitch' and 'twitch.tv' in href:
                                is_platform_url = True
                            
                            if is_platform_url and text and len(text) > 3:
                                # Clean Google redirect URLs - EXACT same
                                clean_href = href
                                if href.startswith('/url?q='):
                                    try:
                                        clean_href = unquote(href.split('/url?q=')[1].split('&')[0])
                                    except Exception:
                                        clean_href = href.split('/url?q=')[1].split('&')[0]
                                
                                platform_links.append({
                                    'title': text[:100],  # Limit title length
                                    'url': clean_href,
                                    'snippet': ''
                                })
                        
                        st.info(f"Found {len(platform_links)} {platform} links via direct extraction")
                        results = platform_links[:max_results]
                    else:
                        # Parse structured results - EXACT same logic
                        st.info(f"Parsing {len(search_divs)} structured results")
                        
                        for i, div in enumerate(search_divs[:max_results * 2]):
                            # Try multiple combinations of selectors - EXACT same
                            title_selectors = ['h3', '.LC20lb', '[role="heading"]', 'h3 span', '.DKV0Md', '.BNeawe.vvjwJb.AP7Wnd']
                            link_selectors = ['a[href]', 'a', '[href]']
                            
                            title_elem = None
                            link_elem = None
                            
                            for title_sel in title_selectors:
                                title_elem = div.select_one(title_sel)
                                if title_elem and title_elem.get_text().strip():
                                    break
                            
                            for link_sel in link_selectors:
                                link_elem = div.select_one(link_sel)
                                if link_elem and link_elem.get('href'):
                                    break
                            
                            if title_elem and link_elem:
                                title = title_elem.get_text().strip()
                                url = link_elem['href']
                                
                                # Check if it's a platform URL - EXACT same logic
                                is_platform_url = False
                                if platform == 'youtube' and 'youtube.com' in url:
                                    is_platform_url = True
                                elif platform == 'twitch' and 'twitch.tv' in url:
                                    is_platform_url = True
                                
                                if is_platform_url:
                                    # Clean Google redirect URLs - EXACT same
                                    if url.startswith('/url?q='):
                                        try:
                                            url = unquote(url.split('/url?q=')[1].split('&')[0])
                                        except Exception:
                                            url = url.split('/url?q=')[1].split('&')[0]
                                    
                                    snippet_elem = div.select_one('.VwiC3b') or div.select_one('.s') or div.select_one('.st')
                                    snippet = snippet_elem.get_text().strip() if snippet_elem else ''
                                    
                                    st.success(f"✅ Found {platform} result: '{title}' -> '{url}'")
                                    
                                    results.append({
                                        'title': title,
                                        'url': url,
                                        'snippet': snippet
                                    })
                                    
                                    if len(results) >= max_results:
                                        break
                    
                    if results:
                        st.success(f"✅ Successfully extracted {len(results)} search results for {query}")
                        return results
                    else:
                        st.warning(f"No {platform} results found")
                        return []
                else:
                    st.error(f"Bad response: {response.status_code}")
                    if proxy:
                        self.proxy_manager.mark_proxy_failed(proxy)
                        
            except Exception as e:
                st.error(f"Search attempt {attempt + 1} failed: {e}")
                if proxy:
                    self.proxy_manager.mark_proxy_failed(proxy)
                time.sleep(2)
        
        st.error(f"All search attempts failed for query: {query}")
        return []


class SyncURLFilter:
    """URL filtering - EXACT same as original"""
    
    @staticmethod
    def filter_youtube_url(url: str) -> str:
        """Filter and clean YouTube URLs - EXACT same as original"""
        if not url:
            return None
        
        # Remove Google redirect
        if url.startswith('/url?q='):
            url = url.split('/url?q=')[1].split('&')[0]
        
        # Validate YouTube URLs
        if "youtube.com" in url:
            # Accept various YouTube URL formats
            valid_patterns = ['/channel/', '/c/', '/@', '/user/']
            if any(pattern in url for pattern in valid_patterns):
                return url
        
        return None
    
    @staticmethod
    def filter_twitch_url(url: str) -> str:
        """Filter and clean Twitch URLs - EXACT same as original"""
        if not url:
            return None
        
        # Remove Google redirect
        if url.startswith('/url?q='):
            url = url.split('/url?q=')[1].split('&')[0]
        
        # Validate Twitch URLs
        if "twitch.tv" in url and len(url.split('/')) >= 4:
            # Basic Twitch channel URL validation
            return url
        
        return None


class SyncChannelFinder:
    """Synchronous channel finder using EXACT same logic as original"""
    
    def __init__(self, proxy_manager: SyncProxyManager):
        self.search_engine = SyncSearchEngine(proxy_manager)
        self.enhanced_matcher = EnhancedMatcher()
    
    def extract_name_from_url(self, url: str) -> str:
        """Extract potential name from profile URL - EXACT same as original"""
        try:
            # Common patterns in X/Twitter URLs
            if 'x.com' in url or 'twitter.com' in url:
                # Split by / and find the username part
                parts = url.split('/')
                for i, part in enumerate(parts):
                    if part in ['x.com', 'twitter.com'] and i + 1 < len(parts):
                        username_part = parts[i + 1]
                        # Remove query parameters
                        if '?' in username_part:
                            username_part = username_part.split('?')[0]
                        # Remove @ symbol
                        username_part = username_part.replace('@', '')
                        # Skip common paths that aren't usernames
                        if username_part not in ['home', 'explore', 'notifications', 'messages', 'bookmarks', 'lists', 'profile', 'more', 'compose', 'search', 'settings', 'help']:
                            return username_part.strip()
            else:
                # For other URLs, use the last path segment
                path = url.split('/')[-1] if '/' in url else url
                
                # Remove query parameters
                if '?' in path:
                    path = path.split('?')[0]
                
                # Remove common suffixes
                path = path.replace('@', '')
                
                # Clean up the extracted name
                cleaned_name = path.strip()
                
                if cleaned_name and len(cleaned_name) > 0:
                    return cleaned_name
            
        except Exception as e:
            st.warning(f"Error extracting name from URL {url}: {e}")
        
        return ""
    
    def find_channels_for_user(self, username: str, profile_name: str, url: str = ""):
        """Find YouTube and Twitch channels for a user - EXACT same logic as original"""
        results = {
            'youtube_url': None,
            'youtube_score': 0,
            'twitch_url': None,
            'twitch_score': 0
        }
        
        # Create search queries - EXACT same as original
        queries = []
        if username:
            queries.append(f'"{username}"')
        if profile_name and profile_name != username:
            queries.append(f'"{profile_name}"')
        if username and profile_name:
            queries.append(f'{username} {profile_name}')
        
        # Extract name from URL as fallback if provided - EXACT same
        url_extracted_name = ""
        if url:
            url_extracted_name = self.extract_name_from_url(url)
            if url_extracted_name and url_extracted_name not in [username, profile_name]:
                queries.append(f'"{url_extracted_name}"')
        
        # Remove empty queries
        queries = [q for q in queries if q.strip() != '""' and q.strip()]
        queries = queries[:3]  # Limit queries to prevent overuse
        
        st.info(f"🔎 Search queries for {username}: {queries}")
        
        # Search each platform - EXACT same logic
        for platform in ['youtube', 'twitch']:
            best_match = {'score': 0, 'title': None, 'url': None}
            
            for query in queries:
                try:
                    search_results = self.search_engine.search_with_requests(query, platform)
                    
                    if search_results:
                        for result in search_results:
                            title = result.get('title', '')
                            url = result.get('url', '')
                            
                            # Filter valid URLs - EXACT same
                            if platform == 'youtube':
                                clean_url = SyncURLFilter.filter_youtube_url(url)
                            else:
                                clean_url = SyncURLFilter.filter_twitch_url(url)
                            
                            if not clean_url:
                                continue
                            
                            # Enhanced matching - EXACT same
                            if self.enhanced_matcher.enhanced_name_match(clean_url, username, profile_name):
                                # Use enhanced matching score
                                match_score = self.enhanced_matcher.calculate_match_score(username, profile_name, title, clean_url)
                                
                                # Set minimum score for enhanced matches
                                if match_score < 50:
                                    match_score = 50
                                
                                best_match = {
                                    'score': match_score,
                                    'title': title,
                                    'url': clean_url
                                }
                                
                                st.success(f"✅ Enhanced match found for {username} on {platform}: {clean_url} (score: {match_score})")
                                
                                # Found a good match, stop searching more results for this query
                                break
                        
                        # Found a good match for this query, stop searching more results
                        if best_match['score'] >= 50:
                            break
                            
                except Exception as e:
                    st.error(f"Search failed for {query} on {platform}: {e}")
                    continue
                
                # If we found a good match, stop searching other queries
                if best_match['score'] >= 50:
                    break
                
                # Rate limiting between queries
                time.sleep(random.uniform(2, 4))
            
            # Store best match
            if best_match['score'] >= 50:
                if platform == 'youtube':
                    results['youtube_url'] = best_match['url']
                    results['youtube_score'] = best_match['score']
                else:
                    results['twitch_url'] = best_match['url']
                    results['twitch_score'] = best_match['score']
        
        return results


def validate_csv(df: pd.DataFrame) -> tuple[bool, str]:
    """Validate CSV format"""
    required_columns = ['username', 'profile_name', 'url', 'followers']
    
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        return False, f"Missing columns: {', '.join(missing)}"
    
    if df.empty:
        return False, "CSV file is empty"
    
    if df['username'].isna().all():
        return False, "No valid usernames found"
        
    return True, "Valid CSV format"


def process_users_with_real_logic(df: pd.DataFrame, progress_bar, status_text, proxy_file_path: str) -> pd.DataFrame:
    """Process users with the REAL working logic"""
    
    # Initialize components using EXACT same logic
    proxy_manager = SyncProxyManager(proxy_file_path)
    channel_finder = SyncChannelFinder(proxy_manager)
    
    results = []
    total_users = len(df)
    
    for i, row in df.iterrows():
        username = row['username']
        profile_name = row['profile_name']
        url = row['url']
        
        # Update progress
        progress = (i + 1) / total_users
        progress_bar.progress(progress)
        status_text.text(f"Processing {username} ({i + 1}/{total_users})")
        
        st.info(f"🔎 Starting search for user: {username} (profile: {profile_name})")
        
        # Find channels using REAL logic
        try:
            channels = channel_finder.find_channels_for_user(username, profile_name, url)
            
            st.info(f"📊 Results for {username}: YouTube={channels['youtube_url']}, Twitch={channels['twitch_url']}")
            
            # Combine original data with results
            result_row = {
                'username': username,
                'profile_name': profile_name,
                'url': url,
                'followers': row['followers'],
                'youtube_url': channels['youtube_url'] or '',
                'youtube_score': channels['youtube_score'],
                'twitch_url': channels['twitch_url'] or '',
                'twitch_score': channels['twitch_score']
            }
            
            results.append(result_row)
            
        except Exception as e:
            st.error(f"Error processing {username}: {str(e)}")
            # Add empty result
            result_row = {
                'username': username,
                'profile_name': profile_name,
                'url': url,
                'followers': row['followers'],
                'youtube_url': '',
                'youtube_score': 0,
                'twitch_url': '',
                'twitch_score': 0
            }
            results.append(result_row)
        
        # Rate limiting between users
        time.sleep(random.uniform(3, 6))
    
    return pd.DataFrame(results)


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔍 YouTube & Twitch Channel Finder</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Using the REAL working sophisticated matching algorithms!</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'results_df' not in st.session_state:
        st.session_state.results_df = None
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        uploaded_file = st.file_uploader(
            "Upload CSV with user data",
            type=['csv'],
            help="CSV file with columns: username, profile_name, url, followers"
        )
        
        proxy_file = st.file_uploader(
            "Upload proxy list (optional)",
            type=['csv'],
            help="CSV file with proxy list. Leave empty to use default."
        )
    
    # Main content
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            is_valid, message = validate_csv(df)
            
            if is_valid:
                st.markdown('<div class="success-box">✅ Valid CSV file uploaded successfully!</div>', unsafe_allow_html=True)
                
                # Display sample data
                st.subheader("📊 Input Data Preview")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Users", len(df))
                with col2:
                    st.metric("Valid Usernames", df['username'].notna().sum())
                with col3:
                    avg_followers = df['followers'].mean() if 'followers' in df.columns else 0
                    st.metric("Avg Followers", f"{avg_followers:,.0f}")
                
                st.dataframe(df.head(10), use_container_width=True)
                
                # Handle proxy file
                proxy_file_path = config.PROXY_FILE  # Default
                if proxy_file is not None:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_proxy:
                        proxy_df = pd.read_csv(proxy_file)
                        proxy_df.to_csv(tmp_proxy.name, index=False)
                        proxy_file_path = tmp_proxy.name
                
                # Processing button
                if st.button("🚀 Start Processing with REAL Logic", disabled=st.session_state.processing):
                    st.session_state.processing = True
                    st.rerun()
                
                # Processing section
                if st.session_state.processing:
                    st.header("⚡ Processing Status")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Process with REAL logic
                        results_df = process_users_with_real_logic(df, progress_bar, status_text, proxy_file_path)
                        
                        # Store results
                        st.session_state.results_df = results_df
                        st.session_state.processing = False
                        
                        st.success("🎉 Processing completed with REAL sophisticated logic!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Processing failed: {str(e)}")
                        st.session_state.processing = False
                        st.rerun()
            
            else:
                st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Error reading CSV: {str(e)}</div>', unsafe_allow_html=True)
    
    else:
        # Instructions
        st.header("📋 Instructions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Required CSV Format:**
            - `username`: X/Twitter username
            - `profile_name`: Display name 
            - `url`: Profile URL
            - `followers`: Follower count
            """)
            
        with col2:
            st.markdown("""
            **This version uses:**
            - ✅ Enhanced matching algorithms
            - ✅ Sophisticated query construction
            - ✅ Multiple Google result selectors
            - ✅ Proper URL filtering
            - ✅ REAL working logic!
            """)
    
    # Results section
    if st.session_state.results_df is not None:
        st.header("📈 Results")
        
        results_df = st.session_state.results_df
        
        # Results metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_processed = len(results_df)
            st.metric("Total Processed", total_processed)
        
        with col2:
            youtube_found = results_df['youtube_url'].notna().sum()
            st.metric("YouTube Found", youtube_found)
        
        with col3:
            twitch_found = results_df['twitch_url'].notna().sum()
            st.metric("Twitch Found", twitch_found)
        
        with col4:
            success_rate = ((youtube_found + twitch_found) / (total_processed * 2)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Results table
        st.subheader("📊 Detailed Results")
        st.dataframe(results_df, use_container_width=True)
        
        # Download button
        csv_buffer = io.StringIO()
        results_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Results CSV",
            data=csv_data,
            file_name=f"youtube_twitch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )


if __name__ == "__main__":
    main()