"""Reusable, uncluttered farm maps for search, missions and rover simulation."""
from __future__ import annotations

import plotly.graph_objects as go
from .farm import Farm
from .pathfinding import SearchResult

COLORS = {
    'crop': '#d9ecd7',
    'empty': '#f2f7f2',
    'obstacle': '#647b70',
    'infected': '#fce4bc',
}
SEVERITY_COLOR = {'Low':'#dab14c', 'Medium':'#e28a3f', 'High':'#d7524c'}


def farm_figure(farm: Farm, result: SearchResult | None = None, show_explored: bool = True):
    cell_ids = {'crop':0, 'empty':1, 'obstacle':2, 'infected':3}
    z = [[cell_ids[cell] for cell in row] for row in farm.cells]
    cell_hover = [
        [f'Row {r+1} · Col {c+1}<br>{cell.title()}' for c, cell in enumerate(row)]
        for r, row in enumerate(farm.cells)
    ]
    # Discrete colors, fixed map bounds and integer-only ticks avoid the stray
    # negative values/huge whitespace visible in the original Plotly layout.
    fig = go.Figure(go.Heatmap(
        z=z,
        x=list(range(1, farm.cols+1)),
        y=list(range(1, farm.rows+1)),
        zmin=0, zmax=3,
        colorscale=[
            [0.0000, COLORS['crop']], [0.2499, COLORS['crop']],
            [0.2500, COLORS['empty']], [0.4999, COLORS['empty']],
            [0.5000, COLORS['obstacle']], [0.7499, COLORS['obstacle']],
            [0.7500, COLORS['infected']], [1.0000, COLORS['infected']],
        ],
        showscale=False, text=cell_hover,
        hovertemplate='%{text}<extra></extra>',
        xgap=2, ygap=2,
    ))

    if result and show_explored and result.explored:
        fig.add_trace(go.Scatter(
            x=[p[1]+1 for p in result.explored],
            y=[p[0]+1 for p in result.explored],
            mode='markers', name='Explored cells',
            marker=dict(size=8, color='#7aaac9', opacity=.46),
            hovertemplate='Explored: Row %{y}, Col %{x}<extra></extra>',
        ))
    if result and result.path:
        fig.add_trace(go.Scatter(
            x=[p[1]+1 for p in result.path],
            y=[p[0]+1 for p in result.path],
            mode='lines+markers', name='Calculated path',
            line=dict(color='#167a4a', width=4),
            marker=dict(size=5, color='#167a4a'),
            hovertemplate='Route: Row %{y}, Col %{x}<extra></extra>',
        ))

    for severity in ('High','Medium','Low'):
        infected = [(r,c) for r in range(farm.rows) for c in range(farm.cols)
                    if farm.cells[r][c] == 'infected'
                    and farm.severities.get(farm.key(r,c),'Medium') == severity]
        if infected:
            fig.add_trace(go.Scatter(
                x=[c+1 for r,c in infected], y=[r+1 for r,c in infected],
                mode='markers', name=f'{severity} severity',
                marker=dict(size=16,color=SEVERITY_COLOR[severity],symbol='diamond',
                            line=dict(color='white',width=1.6)),
                hovertemplate=f'{severity} severity<br>Row %{{y}}, Col %{{x}}<extra></extra>',
            ))

    fig.add_trace(go.Scatter(
        x=[farm.rover[1]+1], y=[farm.rover[0]+1], mode='markers+text',
        name='Rover start', text=['R'],textposition='middle center',
        textfont=dict(color='white',size=10,family='Arial Black'),
        marker=dict(size=24,color='#2e78a8',line=dict(color='white',width=2)),
        hovertemplate='Rover start: Row %{y}, Col %{x}<extra></extra>',
    ))
    if result:
        fig.add_trace(go.Scatter(
            x=[result.goal[1]+1], y=[result.goal[0]+1],
            mode='markers+text', name='Destination',
            text=['G'],textposition='middle center',
            textfont=dict(color='white',size=10,family='Arial Black'),
            marker=dict(size=24,color='#9359b6',line=dict(color='white',width=2)),
            hovertemplate='Destination: Row %{y}, Col %{x}<extra></extra>',
        ))

    def nice_ticks(total: int):
        increment = 1 if total <= 16 else 2 if total <= 24 else 3
        ticks = list(range(1,total+1,increment))
        return ticks if ticks[-1] == total else ticks + [total]

    fig.update_layout(
        height=max(425, min(660, int(farm.rows*34)+115)),
        margin=dict(l=16,r=16,t=12,b=74),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#ffffff',
        font=dict(family='Arial, sans-serif',size=12,color='#335744'),
        legend=dict(orientation='h', y=-.21, x=0, yanchor='top', xanchor='left',
                    bgcolor='rgba(0,0,0,0)',font=dict(size=10)),
        hoverlabel=dict(bgcolor='white',font=dict(color='#18442d')),
        xaxis=dict(
            title=None,side='top',tickmode='array',tickvals=nice_ticks(farm.cols),
            range=[0.5, farm.cols+0.5],fixedrange=True,
            showgrid=False,showline=False,zeroline=False,
            tickfont=dict(size=10,color='#63836f'),
        ),
        yaxis=dict(
            title=None,tickmode='array',tickvals=nice_ticks(farm.rows),
            range=[farm.rows+0.5,0.5],fixedrange=True,
            showgrid=False,showline=False,zeroline=False,
            tickfont=dict(size=10,color='#63836f'),
            # Do not use scaleanchor here. It stretches axis bounds in wide
            # columns and previously exposed unwanted negative ticks.
        ),
    )
    return fig
