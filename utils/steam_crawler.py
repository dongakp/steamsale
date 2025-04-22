import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd
import numpy as np
import time
import re
from deals.models import Game

def crawler(category = "",count = 50):
    user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"}

    res = requests.get("https://store.steampowered.com/robots.txt", user_agent)

    # 전처리 함수 정의의
    def clean_discount(s): 
        return int(s.replace('%', '').replace('-', '').strip())

    def clean_price(s): 
        return int(s.replace("₩", "").replace(",", "").strip()) if s != "N/A" else 0

    def clean_date(s:str):  
        return t.date() if (t := pd.to_datetime(s, errors='coerce')) == t else None

    def parse_review_summary(html):
        text = BeautifulSoup(html or "", "html.parser").get_text(" ")
        review_pcts = next(
            (int(m.replace(".", "")) if "." not in m else float(m)
            for m in re.findall(r"([\d\.]+)%", text)),
            None
        )
        review_counts = next(
            (int(m.replace(",", ""))
            for m in re.findall(r"([\d,]+)\s*user reviews", text)),
            None
        )
        return review_pcts, review_counts

        # ---------------- 검색 결과 크롤링 (BeautifulSoup) ----------------
    start = time.time()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }

    encoded_category = urllib.parse.quote(category)
    search_url = f"https://store.steampowered.com/search/?sort_by=Reviews_DESC&term={encoded_category}&specials=1&category1=998&ndl=1"

    res = requests.get(search_url, headers=headers)
    res.raise_for_status() # 요청 실패하면 바로 에러처리
    soup = BeautifulSoup(res.text, "html.parser")

    game_elements = soup.select("a.search_result_row")[:count]
    game_data = []

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
        review_pcts, review_counts = parse_review_summary(review_summary) #review_summary에서 긍정적 평가, 리뷰수를 추출

        game_data.append({
            "title":          title,
            "link":           link,
            "final_price":    final_price,
            "original_price": original_price,
            "discount_pct":   discount_pct,
            "review_pct":     review_pcts,
            "review_count":   review_counts,
        })
    # ---------------- 상세 페이지 크롤링 (출시일 + 태그) ----------------
    release_dates = []
    tags = []

    for game in game_data:
        resp = requests.get(game["link"], headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")

        #출시일
        date = soup.select_one(".release_date .date")
        release_dates.append(date.get_text(strip=True) if date else "Unknown")

        # 태그 (최대 4개)
        tags_list = [
            t.get_text(strip=True)
            for t in soup.select(".glance_tags.popular_tags .app_tag")
            if t.get_text(strip=True) != "+"
        ][:4]
        tags.append(",".join(tags_list))
        

    print(f"크롤링 완료: {time.time() - start:.4f} sec")

    # ------------------- DataFrame 생성 및 병합 -------------------
    for i, game in enumerate(game_data):
        game["release_date"] = release_dates[i]
        game["tags"]         = tags[i]

    df = pd.DataFrame(game_data)

    df["discount_rate"] = df["discount_pct"].apply(clean_discount)
    df["original_price"] = df["original_price"].apply(clean_price)
    df["discounted_price"] = df["final_price"].apply(clean_price)
    df["release_date"] = df["release_date"].apply(clean_date)

    # 최종 정리할 컬럼
    df_final = df[["title", "discount_rate", "original_price", "discounted_price", "review_pct", "review_count", "release_date", "tags", "link"]]

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
    return None