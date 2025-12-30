import pandas as pd
import plotly.express as px


df = pd.read_csv("battle_sim_results.csv", index_col=0)
# positive = attackers survive/win
# negative = defenders survive/win
df['net_advantage'] = (df['A'] - df['AL']) - (df['D'] - df['DL'])
df['net_damage'] = df['AL'] - df['DL']
agg = (
    df
    .groupby(["A", "D"])
    .agg(
        attacker_lost_mean=("AL", "mean"),
        defender_lost_mean=("DL", "mean"),
        net_advantage_mean=("net_advantage", "mean"),
        net_damage_mean=("net_damage", "mean"),
    )
    .reset_index()
)


def pivot(metric):
    return agg.pivot(index="A", columns="D", values=metric)


def plot_attacker_heatmap(name='attacker_heatmap'):
    fig = px.imshow(
        pivot("attacker_lost_mean"),
        text_auto=".2f",
        color_continuous_scale="Reds",
        labels=dict(x="Defender Dice", y="Attacker Dice", color="Avg Attacker Lost"),
        title="Expected Attacker Losses",
        origin='lower',
    )
    fig.write_html(f'{name}.html')


def plot_defender_heatmap(name='defender_heatmap'):

    fig = px.imshow(
        pivot("defender_lost_mean"),
        text_auto=".2f",
        color_continuous_scale="Blues",
        labels=dict(x="Defender Dice", y="Attacker Dice", color="Avg Defender Lost"),
        title="Expected Defender Losses",
        origin='lower',
    )
    fig.write_html(f'{name}.html')


def plot_net_advantage_heatmap(name='net_advantage_heatmap'):
    fig = px.imshow(
        pivot("net_advantage_mean"),
        text_auto=".2f",
        color_continuous_scale="RdBu",
        labels=dict(x="Defender Dice", y="Attacker Dice", color="Net Advantage"),
        title="Net Advantage (Surviving Attackers − Surviving Defenders)",
        zmin=-max(abs(agg["net_advantage_mean"])),
        zmax=max(abs(agg["net_advantage_mean"])),
        origin='lower',
    )
    fig.write_html(f'{name}.html')


def plot_net_damage_heatmap(name='net_damage_heatmap'):
    fig = px.imshow(
        pivot("net_damage_mean"),
        text_auto=".2f",
        color_continuous_scale="RdBu",
        labels=dict(x="Defender Dice", y="Attacker Dice", color="Net Damage"),
        title="Net Damage (Attackers Lost − Defenders Lost)",
        origin='lower',
    )
    fig.write_html(f'{name}.html')


def plot_losses_histogram_matrix(name='loss_matrix'):
    mdf = df.melt(
        id_vars=['A', 'D'],
        value_vars=['AL', 'DL', 'B'],
        var_name='var',
        value_name='value',
    )
    fig = px.histogram(
        mdf,
        barmode='group',
        x='value',
        color='var',
        facet_row='A',
        facet_col='D',
        labels=dict(x="Defender Dice", y="Attacker Dice", color="Variable"),
        title='Distribution of Simulated Loss Matrix over # Attacker/Defender Dice',
    )
    fig.write_html(f'{name}.html')


if __name__ == '__main__':
    plot_attacker_heatmap()
    plot_defender_heatmap()
    plot_net_advantage_heatmap()
    plot_net_damage_heatmap()
    plot_losses_histogram_matrix()
