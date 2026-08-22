import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# 1. DB 불러오기
# ============================================================

with sqlite3.connect("database/policy.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM education_reservation",
        conn
    )

df["edu_date"] = pd.to_datetime(df["edu_date"])
df["capacity"] = pd.to_numeric(df["capacity"])


# ============================================================
# 2. 월 컬럼 생성
# ============================================================

df["month"] = (
    df["edu_date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)


# ============================================================
# 3. 월별 전체 교육 정원
# ============================================================

monthly = (
    df.groupby("month", as_index=False)["capacity"]
    .sum()
)

plt.figure(figsize=(11, 5))

plt.plot(
    monthly["month"],
    monthly["capacity"],
    marker="o"
)

plt.title("월별 고령운전자 교통안전교육 정원")
plt.xlabel("월")
plt.ylabel("교육 정원")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# ============================================================
# 4. 과정별 월별 추세
#    의무교육 vs 권장교육
# ============================================================

course_month = (
    df.groupby(
        ["month", "course_name"],
        as_index=False
    )["capacity"]
    .sum()
)

plt.figure(figsize=(11, 5))

for course in course_month["course_name"].unique():

    temp = course_month[
        course_month["course_name"] == course
    ]

    plt.plot(
        temp["month"],
        temp["capacity"],
        marker="o",
        label=course
    )

plt.title("월별 고령운전자 교육 과정별 정원")
plt.xlabel("월")
plt.ylabel("교육 정원")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# ============================================================
# 5. 교육장별 월별 추세
# ============================================================

branch_month = (
    df.groupby(
        ["month", "branch_name"],
        as_index=False
    )["capacity"]
    .sum()
)

plt.figure(figsize=(13, 6))

for branch in branch_month["branch_name"].unique():

    temp = branch_month[
        branch_month["branch_name"] == branch
    ]

    plt.plot(
        temp["month"],
        temp["capacity"],
        label=branch
    )

plt.title("교육장별 월별 교육 정원 추세")
plt.xlabel("월")
plt.ylabel("교육 정원")

plt.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# ============================================================
# 6. 월별 평균 교육 정원
# ============================================================

monthly_avg = (
    df.groupby("month", as_index=False)["capacity"]
    .mean()
)

plt.figure(figsize=(11, 5))

plt.plot(
    monthly_avg["month"],
    monthly_avg["capacity"],
    marker="o"
)

plt.title("월별 평균 교육 정원")
plt.xlabel("월")
plt.ylabel("평균 정원")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# ============================================================
# 7. 결과 출력
# ============================================================

print("\n===== 월별 전체 교육 정원 =====")
print(monthly)

print("\n===== 월별 과정별 교육 정원 =====")
print(course_month)