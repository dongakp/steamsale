import os
import sys
import django
import numpy as np
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Django 프로젝트 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django 설정 초기화
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "steamsale.settings")
django.setup()

from deals.models import Game


def get_visualization_data():
    qs = Game.objects.all().values()
    df = pd.DataFrame(qs)

    if df.empty:
        return {
            "discount_distribution": [],
            "review_vs_discount": [],
            "release_discount_scatter": [],
            "monthly_release_spline": {"x": [], "y": []},
            "wordcloud_data": {}
        }

    # 1. 할인율 분포
    discount_hist, bin_edges = np.histogram(df["discount_rate"], bins=10, range=(0, 100))
    discount_distribution = [
        {
            "range": f"{int(bin_edges[i])}-{int(bin_edges[i+1])}",
            "count": int(discount_hist[i])
        }
        for i in range(len(discount_hist))
    ]

    # 2. 리뷰 수 vs 할인율
    review_vs_discount = [
        {
            "discount_rate": int(row["discount_rate"]),
            "review_count": int(row["review_count"]),
            "original_price": int(row["original_price"]),
        }
        for _, row in df.iterrows()
    ]

    # 3. 출시일 vs 할인율
    valid_release = df[df['release_date'].notnull()]
    release_discount_scatter = [
        {
            "release_date": row["release_date"].isoformat() if hasattr(row["release_date"], "isoformat") else str(row["release_date"]),
            "discount_rate": int(row["discount_rate"])
        }
        for _, row in valid_release.iterrows()
    ]

    # 4. 월별 출시 수 (보간 없이)
    df_month = valid_release.copy()
    df_month['month'] = pd.to_datetime(df_month['release_date'], errors='coerce').dt.month
    monthly_counts = df_month['month'].value_counts().sort_index()
    x_full = list(range(1, 13))
    y_full = [monthly_counts.get(i, 0) for i in x_full]

    monthly_release_spline = {
        "x": [int(i) for i in x_full],
        "y": [int(i) for i in y_full]
    }

    # 5. 태그 워드클라우드용 데이터
    all_tags = sum(
        [tag_str.split(",") for tag_str in df["tags"] if isinstance(tag_str, str)],
        []
    )
    tag_counts = dict(Counter(all_tags))

    return {
        "discount_distribution": discount_distribution,
        "review_vs_discount": review_vs_discount,
        "release_discount_scatter": release_discount_scatter,
        "monthly_release_spline": monthly_release_spline,
        "wordcloud_data": tag_counts
    }


def save_wordcloud(tag_counts):
    if not tag_counts:
        print("[!] 워드클라우드 생성을 위한 태그 데이터가 없습니다.")
        return

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white'
    ).generate_from_frequencies(tag_counts)

    output_dir = os.path.join("static", "images")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "word_cloud.png")
    wordcloud.to_file(output_path)
    print(f"[✅] 워드클라우드 저장 완료 → {output_path}")


if __name__ == "__main__":
    data = get_visualization_data()
    from pprint import pprint
    pprint(data)
    save_wordcloud(data["wordcloud_data"])

