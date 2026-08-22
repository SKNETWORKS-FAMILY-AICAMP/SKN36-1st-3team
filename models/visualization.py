import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


def line_plot(df, x, y, title="시계열 추세"):
    data = (
        df.groupby(x, as_index=False)[y]
        .sum()
        .sort_values(x)
    )

    plt.figure(figsize=(10, 5))
    plt.plot(data[x], data[y], marker="o")

    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)

    # 연도일 경우 정수값만 표시
    if pd.api.types.is_numeric_dtype(data[x]):
        plt.xticks(data[x], data[x].astype(int))

    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    return data


def bar_plot(
    df,
    category,
    value,
    title="항목별 비교",
    top_n=None
):
    data = (
        df.groupby(category, as_index=False)[value]
        .sum()
        .sort_values(value, ascending=False)
    )

    if top_n:
        data = data.head(top_n)

    plt.figure(figsize=(10, 5))
    plt.bar(data[category], data[value])

    plt.title(title)
    plt.xlabel(category)
    plt.ylabel(value)

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.show()

    return data

def heatmap_plot(df, row, column, value, title="히트맵"):
    data = df.pivot_table(
        index=row,
        columns=column,
        values=value,
        aggfunc="sum",
        fill_value=0
    )

    plt.figure(figsize=(12, 6))
    plt.imshow(data, aspect="auto")

    plt.colorbar(label=value)

    plt.xticks(
        range(len(data.columns)),
        data.columns,
        rotation=45
    )

    plt.yticks(
        range(len(data.index)),
        data.index
    )

    plt.title(title)
    plt.xlabel(column)
    plt.ylabel(row)

    plt.tight_layout()
    plt.show()

    return data