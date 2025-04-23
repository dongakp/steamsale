import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 이 줄 꼭 필요

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "steamsale.settings")

import django
django.setup()
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from deals.models import Game, Stats
from collections import Counter


# 데이터프레임 생성
games = Game.objects.all().values()
df = pd.DataFrame(games)

if df.empty:
    print("❌ Game 데이터가 없습니다.")
    exit()

# Stats 초기화
Stats.objects.all().delete()

# -------------------------
# 1. 할인률 분포 (KDE)
# -------------------------
counts, bins, _ = plt.hist(df['discount_rate'], bins=10)
labels = [f"{round(bins[i], 2)}~{round(bins[i+1], 2)}" for i in range(len(bins)-1)]
Stats.objects.create(data={
    "type": "discount_kde",
    "labels": labels,
    "data": counts.tolist()
})
print("✅ 할인률 분포 저장 완료")

# -------------------------
# 2. 태그별 게임 수
# -------------------------
df['tags'] = df['tags'].apply(lambda x: x.split(',') if isinstance(x, str) else [])
tag_counts = Counter(tag for tags in df['tags'] for tag in tags)
top10 = tag_counts.most_common(10)
Stats.objects.create(data={
    "type": "tag",
    "labels": [t[0] for t in top10],
    "data": [t[1] for t in top10]
})
print("✅ 태그 저장 완료")

# -------------------------
# 3. 가성비 TOP 10
# -------------------------
df['value'] = df['review_count'] / df['discounted_price'].replace(0, 1)
top_value = df.sort_values('value', ascending=False).head(10)
Stats.objects.create(data={
    "type": "value",
    "labels": top_value['title'].tolist(),
    "data": top_value['value'].round(2).tolist()
})
print("✅ 가성비 저장 완료")

# -------------------------
# 4. 원가 vs 할인가
# -------------------------
Stats.objects.create(data={
    "type": "price",
    "x": df['original_price'].tolist(),
    "y": df['discounted_price'].tolist()
})
print("✅ 가격 비교 저장 완료")

# -------------------------
# 5. 리뷰 수 vs 할인률 (버블차트용)
# -------------------------
bubble_data = [
    {"x": row['discount_rate'], "y": row['review_count'], "r": max(1, row['original_price'] // 1000)}
    for _, row in df.iterrows()
]
Stats.objects.create(data={
    "type": "bubble",
    "data": bubble_data
})
print("✅ 버블 데이터 저장 완료")


# data = {‘discount_rate’: discount_rate_list, ‘discount_rate_density’:discount_rate_density_list}
# Stats.objects.create(data=data)