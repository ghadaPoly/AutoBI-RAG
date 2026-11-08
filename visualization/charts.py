import plotly.express as px


def create_bar_chart(df, x_column, y_column):
    fig = px.bar(
        df,
        x=x_column,
        y=y_column,
        title=f"{y_column} par {x_column}"
    )

    return fig


def create_line_chart(df, x_column, y_column):
    fig = px.line(
        df,
        x=x_column,
        y=y_column,
        title=f"Évolution de {y_column}"
    )

    return fig