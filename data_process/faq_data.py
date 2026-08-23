import pandas as pd


def traffic_faq_data(
    file_path: str = "data/FAQ/고령운전자 및 교통안전 관련 FAQ.xlsx"
) -> pd.DataFrame:

    # 파일 읽기
    if file_path.endswith(".csv"):
        df = pd.read_csv(
            file_path,
            encoding="cp949",
            header=None
        )
    else:
        df = pd.read_excel(
            file_path,
            header=None
        )

    # 실제 FAQ 데이터 추출
    faq_df = df.iloc[
        2:,
        [0, 1, 2, 3, 4]
    ].copy()

    # 컬럼명 통일
    faq_df.columns = [
        "no",
        "category",
        "question",
        "answer",
        "source_url"
    ]

    # 문자열 정리
    string_cols = [
        "category",
        "question",
        "answer",
        "source_url"
    ]

    for col in string_cols:
        faq_df[col] = (
            faq_df[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # 질문 번호 정리
    faq_df["no"] = pd.to_numeric(
        faq_df["no"],
        errors="coerce"
    )

    faq_df = faq_df.dropna(
        subset=["no"]
    ).copy()

    faq_df["no"] = (
        faq_df["no"]
        .astype(int)
    )

    # 질문이 없는 행 제거
    faq_df = faq_df[
        faq_df["question"] != ""
    ].copy()

    return faq_df.reset_index(drop=True)


if __name__ == "__main__":
    df = traffic_faq_data()

    print(df.head())
    print(df.shape)
    print(df.columns.tolist())