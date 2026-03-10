import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


df = pd.read_json("Daten.json")
df["Grade"] = df["Grade"].astype(float).round(1)


counts = (
    df.groupby(["Nachklausur", "Course", "Year", "Grade"])
      .size()
      .reset_index(name="Anzahl")
)

courses = sorted(counts["Course"].unique())
grades  = sorted(counts["Grade"].unique())
nks     = ["No", "Yes"]

cmap = LinearSegmentedColormap.from_list(
    "grade_cmap", ["green", "yellow", "red"]
)
gmin, gmax = min(grades), max(grades)
color_map = {g: cmap((g - gmin) / (gmax - gmin)) for g in grades}


years_union_per_course = {
    course: sorted(counts[counts["Course"] == course]["Year"].unique())
    for course in courses
}

fig, axes = plt.subplots(
    len(nks), len(courses),
    figsize=(5 * len(courses), 8),
    sharey=True
)

if len(courses) == 1:
    axes = np.array(axes).reshape(len(nks), 1)

bar_width = 0.8
EPS = 1e-12



for i, nk in enumerate(nks):
    for j, course in enumerate(courses):
        ax = axes[i, j]

        years = years_union_per_course[course]
        x_all = np.arange(len(years))

        sub = counts[
            (counts["Nachklausur"] == nk) &
            (counts["Course"] == course)
        ]

        if sub.empty:
            ax.axis("off")
            continue

        table_present = (
            sub.pivot(index="Year", columns="Grade", values="Anzahl")
               .reindex(columns=grades, fill_value=0)
        )

        proportions_present = table_present.div(
            table_present.sum(axis=1), axis=0
        ).fillna(0)



        proportions = pd.DataFrame(0.0, index=years, columns=grades)
        proportions.loc[proportions_present.index] = proportions_present

        has_data = proportions.sum(axis=1).values > 0
        x = x_all[has_data]
        years_drawn = np.array(years)[has_data]

        bottom = np.zeros(len(x))

        for g in grades:
            vals = proportions.loc[years_drawn, g].values
            color = color_map[g]

            bars = ax.bar(
                x,
                vals,
                bottom=bottom,
                width=bar_width,
                color=color
            )


            r, gg, b, _ = color
            luminance = 0.2126*r + 0.7152*gg + 0.0722*b
            text_color = "white" if luminance < 0.5 else "black"

            for rect in bars:
                h = rect.get_height()
                if h > EPS:
                    ax.text(
                        rect.get_x() + rect.get_width() / 2,
                        rect.get_y() + h / 2,
                        f"{g:.1f}",
                        ha="center",
                        va="center",
                        fontsize=7,
                        color=text_color,
                        clip_on=True
                    )

            bottom += vals


        ax.set_xlim(-0.5, len(years) - 0.5)
        ax.set_ylim(0, 1)

        ax.set_xticks(x)
        ax.set_xticklabels(years_drawn)

        ax.set_ylabel("Anteil Studenten")
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
        ax.tick_params(axis="y", labelleft=True)


        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.set_title(f"{course} – {'Normalklausur' if nk == 'No' else 'Nachklausur'}")


handles = [plt.Rectangle((0, 0), 1, 1, color=color_map[g]) for g in grades]
labels  = [f"{g:.1f}" for g in grades]

fig.legend(
    handles,
    labels,
    title="Noten",
    loc="lower center",
    ncol=min(len(grades), 10)
)

fig.suptitle(
    "Relative Notenverteilung nach Jahr, Kurs und Nachklausur",
    fontsize=16
)

plt.tight_layout(rect=[0, 0.08, 1, 0.94])
plt.show()
