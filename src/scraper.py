import os
import json
import html
import logging
import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re
from urllib.parse import urljoin
import concurrent.futures

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DATA_FILE = 'docs/data/posts.json'
MAX_POSTS = 1000

def load_target_sites():
    target_sites_raw = os.getenv('TARGET_SITES')
    if not target_sites_raw:
        logger.error("TARGET_SITES environment variable is missing.")
        return []
    try:
        return json.loads(target_sites_raw)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse TARGET_SITES JSON: {e}")
        return []

def send_telegram_message(token, chat_id, message, session=None):
    if not token or not chat_id or token == 'your_telegram_bot_token_here':
        logger.warning("Telegram token or chat ID is missing or invalid. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        if session:
            response = session.post(url, json=payload, timeout=10)
        else:
            response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Telegram notification sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

def load_existing_posts():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load existing posts: {e}")
        return []

def save_posts(posts):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    try:
        # Sort by date descending
        posts.sort(key=lambda x: x.get('date', ''), reverse=True)
        posts = posts[:MAX_POSTS]

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(posts)} posts to {DATA_FILE}")
    except Exception as e:
        logger.error(f"Failed to save posts: {e}")

def clean_text(text):
    # Remove '새글' if it appears at the end of the title
    cleaned = " ".join(text.split()).strip()
    if cleaned.endswith('새글'):
        cleaned = cleaned[:-2].strip()
    return cleaned

def scrape_site(site_config):
    posts = []
    name = site_config.get('name', 'Unknown')
    url = site_config.get('url')
    base_url = site_config.get('base_url', '')
    row_selector = site_config.get('row_selector')
    title_selector = site_config.get('title_selector')
    link_selector = site_config.get('link_selector')
    date_selector = site_config.get('date_selector')

    if not all([url, row_selector, title_selector, link_selector]):
        logger.warning(f"Incomplete configuration for site: {name}")
        return posts

    logger.info(f"Scraping site: {name} - {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select(row_selector)

        for row in rows:
            # Skip rows if it's a "no data" message
            if row.select_one('td.no_data') or '등록된 게시물이 없습니다' in row.get_text():
                continue

            title_elem = row.select_one(title_selector)
            if not title_elem:
                continue

            title = clean_text(title_elem.get_text())

            link_elem = row.select_one(link_selector)
            link = ""
            if link_elem and link_elem.has_attr('href'):
                href = link_elem['href']

                # Handle javascript links
                if href.startswith('javascript:'):
                    onclick = link_elem.get('onclick', '')
                    onclick_text = onclick if onclick else href
                    match = re.search(r"fn_selectBbsNttView\(['\"](\d+)['\"]\s*,\s*['\"](\d+)['\"]\)", onclick_text)
                    if match:
                        bbsNo, nttNo = match.groups()
                        link = f"{base_url}/portal/selectBbsNttView.do?key=293&bbsNo={bbsNo}&nttNo={nttNo}"
                    else:
                        match2 = re.search(r"fn_selectBbsNttView\('(\d+)'\)", onclick_text)
                        if match2:
                            nttNo = match2.group(1)
                            bbsNo_match = re.search(r"bbsNo=(\d+)", url)
                            bbsNo = bbsNo_match.group(1) if bbsNo_match else '4'
                            key_match = re.search(r"key=(\d+)", url)
                            key = key_match.group(1) if key_match else '293'
                            link = f"{base_url}/portal/selectBbsNttView.do?key={key}&bbsNo={bbsNo}&nttNo={nttNo}"
                        else:
                            logger.warning(f"Unrecognized javascript link: {onclick_text}")
                            continue
                else:
                    # Use urljoin to safely resolve relative URLs
                    link = urljoin(url, href)

            date = ""
            if date_selector:
                date_elem = row.select_one(date_selector)
                if date_elem:
                    date = clean_text(date_elem.get_text())
                    if name == "GeekNews 최근글":
                        match = re.search(r'(\d+시간전|\d+분전|\d+일전|어제|방금)', date)
                        if match:
                            date = match.group(1)

            post_id = link if link else title

            if not date:
                date = datetime.datetime.now().strftime('%Y-%m-%d')

            posts.append({
                "id": post_id,
                "site_name": name,
                "title": title,
                "link": link,
                "date": date,
                "scraped_at": datetime.datetime.now().isoformat()
            })

    except Exception as e:
        logger.error(f"Error scraping {name}: {e}")

    return posts

def main():
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

    target_sites = load_target_sites()
    if not target_sites:
        logger.info("No target sites to scrape. Exiting.")
        return

    existing_posts = load_existing_posts()
    existing_ids = {post['id'] for post in existing_posts}

    new_posts = []

    # Use ThreadPoolExecutor to scrape sites concurrently.
    # This significantly reduces network I/O wait time by running requests in parallel.
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(scrape_site, target_sites)
        for scraped_posts in results:
            for post in scraped_posts:
                if post['id'] not in existing_ids:
                    new_posts.append(post)
                    existing_ids.add(post['id'])

    if new_posts:
        logger.info(f"Found {len(new_posts)} new posts.")
        # ⚡ Bolt: Use requests.Session() to pool connections and avoid the overhead of repeated TCP/TLS handshakes for consecutive requests to the Telegram API.
        with requests.Session() as session:
            for post in reversed(new_posts):
                message = f"<b>[{html.escape(post['site_name'])}]</b>\n{html.escape(post['title'])}\n<a href='{post['link']}'>링크 이동</a>"
                send_telegram_message(telegram_token, telegram_chat_id, message, session=session)

        all_posts = existing_posts + new_posts
        save_posts(all_posts)
    else:
        logger.info("No new posts found.")

if __name__ == "__main__":
    main()
