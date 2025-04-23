import matplotlib
matplotlib.use('Agg')  # ✅ Use a non-interactive backend (safe for servers)
import os
import django
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib import font_manager, rc
from collections import Counter
from wordcloud import WordCloud

# ---------------- Django 설정 초기화 ----------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "steamsale.settings")
django.setup()

# ---------------- Django 모델 불러오기 ----------------
from deals.models import Game

# ---------------- DB에서 데이터 불러오기 ----------------
qs = Game.objects.all().values()
df = pd.DataFrame(qs)

# ---------------- 한글 폰트 설정 ----------------
malgun = [f.fname for f in font_manager.fontManager.ttflist if 'Malgun Gothic' in f.name]
if malgun:
    font_manager.fontManager.addfont(malgun[0])
    rc('font', family='Malgun Gothic')
rc('axes', unicode_minus=False)

# ---------------- 시각화 ----------------
if not df.empty:
    # 할인율 KDE
    df['discount_rate'].plot(kind='kde')
    plt.xlim(0, 100)
    plt.xticks(np.arange(0, 101, 10))
    plt.xlabel('할인율 (%)')
    plt.ylabel('밀도')
    plt.title('할인율 분포 & 밀도 곡선')
    plt.tight_layout()
    plt.savefig("static/images/discount_chart.png")
    plt.clf()

    # 리뷰 수 vs 할인율 버블 차트
    sizes = (df['original_price'] / 200) * 5
    plt.figure(figsize=(8, 6))
    plt.scatter(
        df['discount_rate'],
        df['review_count'],
        s=sizes,
        alpha=0.6,
        edgecolor='black',
    )
    plt.xlabel('할인율 (%)')
    plt.ylabel('리뷰 수')
    plt.title('리뷰 수 vs 할인율 (버블 크기: 원가 × 5)')
    plt.tight_layout()
    plt.savefig("static/images/bouble_chart.png")
    plt.clf()

    # 워드 클라우드
    all_tag = sum([tag_str.split(",") for tag_str in df["tags"] if isinstance(tag_str, str)], [])
    tag_counts = Counter(all_tag)
    wc = WordCloud(
        font_path=malgun[0] if malgun else None,
        width=800, height=400,
        background_color='white'
    )
    wc.generate_from_frequencies(tag_counts)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('WordCloud')
    plt.tight_layout()
    plt.savefig("static/images/word_cloud.png")
    plt.clf()

    print("✅ 모든 시각화 이미지 저장 완료!")
else:
    print("데이터가 없습니다. 시각화를 건너뜁니다.")


# ---------------- 차트 데이터----------------
def generate_chart_data():
    from deals.models import Game
    import pandas as pd

    qs = Game.objects.all().values()
    df = pd.DataFrame(qs)

    if df.empty:
        return {"labels": [], "data": []}

    top_games = df.sort_values(by="review_count", ascending=False).head(10)

    return {
        "labels": top_games["title"].tolist(),
        "data": top_games["review_count"].tolist()
    }


