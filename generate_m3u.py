import os
import requests

API_URL = os.environ.get("API_URL")
API_KEY = os.environ.get("API_KEY")
OUTPUT_FILE = "playlist.m3u"

if not API_URL:
    raise ValueError("API_URL secret set kora hoyni!")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "API-KEY": API_KEY or ""
}

def clean_text(text):
    if not text:
        return ""
    return str(text).replace("\n", " ").replace("\r", "").strip()

def build_m3u():
    response = requests.get(API_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    lines = ["#EXTM3U"]
    count = 0

    def add_channel(ch, group_name="Live TV"):
        nonlocal count
        stream_url = clean_text(ch.get("stream_url"))
        if not stream_url:
            return

        tv_id = clean_text(ch.get("live_tv_id"))
        tv_name = clean_text(ch.get("tv_name") or "Unknown Channel")
        logo = clean_text(ch.get("thumbnail_url") or ch.get("poster_url"))
        group = clean_text(group_name)

        extinf = f'#EXTINF:-1 tvg-id="{tv_id}" tvg-logo="{logo}" group-title="{group}",{tv_name}'
        lines.append(extinf)
        lines.append(stream_url)
        count += 1

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "channels" in item and isinstance(item["channels"], list):
                cat_name = item.get("title") or item.get("category_name") or "Live TV"
                for ch in item["channels"]:
                    add_channel(ch, cat_name)
            elif isinstance(item, dict) and "stream_url" in item:
                add_channel(item, "Live TV")
    elif isinstance(data, dict):
        channels = data.get("channels") or data.get("data") or []
        for ch in channels:
            add_channel(ch, "Live TV")

    if count == 0:
        raise ValueError("Kono channel pawa jayni! API response check koro.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Total {count} channels added to {OUTPUT_FILE}")

if __name__ == "__main__":
    build_m3u()
