"""Plotly farm visualization with computed paths and search expansion."""
import plotly.graph_objects as go
from .farm import Farm
from .pathfinding import SearchResult

COLORS = {'crop':'#d6e9c5','empty':'#f4f6f1','obstacle':'#7d8986','infected':'#f6c36a'}

def farm_figure(farm: Farm, result: SearchResult | None = None, show_explored: bool = True):
    z = [[{'crop':0,'empty':1,'obstacle':2,'infected':3}[cell] for cell in row] for row in farm.cells]
    fig = go.Figure(go.Heatmap(z=z, x=list(range(1,farm.cols+1)),y=list(range(1,farm.rows+1)),
        zmin=0,zmax=3, colorscale=[[0,'#d6e9c5'],[0.249,'#d6e9c5'],[0.25,'#f4f6f1'],[0.499,'#f4f6f1'],[0.5,'#7d8986'],[0.749,'#7d8986'],[0.75,'#f6c36a'],[1,'#f6c36a']],
        showscale=False, hovertemplate='Row %{y}, Column %{x}<extra></extra>', xgap=1,ygap=1))
    if result and show_explored and result.explored:
        fig.add_trace(go.Scatter(x=[p[1]+1 for p in result.explored],y=[p[0]+1 for p in result.explored],
            mode='markers',name='Explored',marker=dict(size=9,color='#75b7e4',opacity=.5),hoverinfo='skip'))
    if result and result.path:
        fig.add_trace(go.Scatter(x=[p[1]+1 for p in result.path],y=[p[0]+1 for p in result.path],
            mode='lines+markers',name='Calculated path',line=dict(color='#166c45',width=4),marker=dict(size=5,color='#166c45')))
    infected = [(r,c) for r in range(farm.rows) for c in range(farm.cols) if farm.cells[r][c]=='infected']
    if infected:
        fig.add_trace(go.Scatter(x=[c+1 for r,c in infected],y=[r+1 for r,c in infected],
            mode='markers',name='Infected',marker=dict(size=16,color='#cf4d38',symbol='diamond',line=dict(color='white',width=1))))
    fig.add_trace(go.Scatter(x=[farm.rover[1]+1],y=[farm.rover[0]+1],mode='markers+text',name='Rover start',
        text=['R'],textposition='middle center',textfont=dict(color='white',size=10),
        marker=dict(size=22,color='#236cb1',line=dict(color='white',width=2))))
    if result:
        fig.add_trace(go.Scatter(x=[result.goal[1]+1],y=[result.goal[0]+1],mode='markers+text',name='Destination',
            text=['G'],textposition='middle center',textfont=dict(color='white',size=10),
            marker=dict(size=22,color='#9b4cbb',line=dict(color='white',width=2))))
    fig.update_layout(height=max(440,min(780,farm.rows*37)),margin=dict(l=12,r=12,t=18,b=12),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',legend=dict(orientation='h',y=-.14),
        xaxis=dict(title='Column',tickmode='linear',tick0=1,dtick=1,range=[.5,farm.cols+.5],side='top',constrain='domain',showgrid=False,zeroline=False),
        yaxis=dict(title='Row',tickmode='linear',tick0=1,dtick=1,range=[farm.rows+.5,.5],scaleanchor='x',scaleratio=1,showgrid=False,zeroline=False),autosize=True)
    return fig
