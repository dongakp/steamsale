import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd
import numpy as np
import time
import re
from deals.models import Game

# ------------------- 전처리 함수 정의 -------------------
def clean_discount(s: str) -> int: 
    return int(s.replace('%', '').replace('-', '').strip())

def clean_price(s: str) -> int: 
    return int(s.replace("₩", "").replace(",", "").strip()) if s != "N/A" else 0

def clean_date(s: str):  
    return t.date() if (t := pd.to_datetime(s, errors='coerce')) == t else None

class NoSearchResult(Exception):
    """검색 결과가 없을 때 던지는 예외"""
    pass

# ------------------- 크롤러 메인 함수 -------------------
def crawler(category: str, count: int):
    start = time.time()
    user_agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }

    encoded_category = urllib.parse.quote(category)
    search_url = f"https://store.steampowered.com/search/?sort_by=Reviews_DESC&term={encoded_category}&specials=1&category1=998&ndl=1"

    res = requests.get(search_url, headers=user_agent)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    game_elements = soup.select("a.search_result_row")[:count]
    game_data = []

    def parse_review_summary(html):
        text = BeautifulSoup(html or "", "html.parser").get_text(" ")
        review_pcts = next((int(m.replace(".", "")) if "." not in m else float(m) for m in re.findall(r"([\d\.]+)%", text)), 0)
        review_counts = next((int(m.replace(",", "")) for m in re.findall(r"([\d,]+)\s*user reviews", text)), 0)
        return review_pcts, review_counts

    for game in game_elements:
        title = game.select_one(".title").text.strip()
        link = game["href"]
        final_price_tag = game.select_one(".discount_final_price")
        original_price_tag = game.select_one(".discount_original_price")
        discount_tag = game.select_one(".discount_pct")

        final_price = final_price_tag.text.strip() if final_price_tag else "N/A"
        original_price = original_price_tag.text.strip() if original_price_tag else final_price
        discount_pct = discount_tag.text.strip() if discount_tag else "0%"

        review_tag = game.select_one(".search_review_summary")
        review_summary = review_tag["data-tooltip-html"] if review_tag and review_tag.has_attr("data-tooltip-html") else "No reviews"
        review_pcts, review_counts = parse_review_summary(review_summary)

        game_data.append({
            "title": title,
            "link": link,
            "final_price": final_price,
            "original_price": original_price,
            "discount_pct": discount_pct,
            "review_pct": review_pcts,
            "review_count": review_counts,
        })

    if not game_data:
        raise NoSearchResult("검색 결과가 없습니다.")

    # ------------------- 상세 페이지: 출시일 + 태그 -------------------
    release_dates = []
    tags = []

    for game in game_data:
        resp = requests.get(game["link"], headers=user_agent)
        soup = BeautifulSoup(resp.text, "html.parser")

        date = soup.select_one(".release_date .date")
        release_dates.append(date.get_text(strip=True) if date else "Unknown")

        tags_list = [
            t.get_text(strip=True)
            for t in soup.select(".glance_tags.popular_tags .app_tag")
            if t.get_text(strip=True) != "+"
        ][:4]
        tags.append(",".join(tags_list))

    print(f"크롤링 완료: {time.time() - start:.4f} sec")

    for i, game in enumerate(game_data):
        game["release_date"] = release_dates[i]
        game["tags"] = tags[i]

    df = pd.DataFrame(game_data)
    df["discount_rate"] = df["discount_pct"].apply(clean_discount)
    df["original_price"] = df["original_price"].apply(clean_price)
    df["discounted_price"] = df["final_price"].apply(clean_price)
    df["release_date"] = df["release_date"].apply(clean_date)

    df_final = df[[
        "title", "discount_rate", "original_price", "discounted_price",
        "review_pct", "review_count", "release_date", "tags", "link"
    ]]

    for _, row in df_final.iterrows():
        Game.objects.create(
            title=row['title'],
            discount_rate=row['discount_rate'],
            original_price=row['original_price'],
            discounted_price=row['discounted_price'],
            review_pct=row['review_pct'],
            review_count=row['review_count'],
            release_date=row['release_date'],  # 문자열이면 변환 필요
            tags=row['tags'],
            link=row['link'],
        )
    return df_final
