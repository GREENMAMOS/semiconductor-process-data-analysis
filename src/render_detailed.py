"""Regenerate detailed figures from public aggregate CSVs: python -m src.render_detailed."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def render(root=None):
    root=Path(root) if root else Path(__file__).resolve().parents[1]
    data=root/'data'; images=root/'images'; images.mkdir(exist_ok=True)
    plt.style.use('seaborn-v0_8-whitegrid')
    def save(fig,name):
        fig.tight_layout(); fig.savefig(images/name,dpi=170,bbox_inches='tight'); plt.close(fig)
    sensor=pd.read_csv(data/'process_sensor_summary.csv')
    # Excel STDEV(B5:D33,C4): Run1/Run3 time>=3 and Run2 time>=2.
    pooled=sensor[((sensor.run=='Run2') & (sensor.process_time>=2)) | ((sensor.run!='Run2') & (sensor.process_time>=3))].si2h6_flow.std(ddof=1)
    fig,axs=plt.subplots(1,2,figsize=(12,4.3))
    for ax,width,title in zip(axs,[2,3*pooled],['Target ±1% (illustrative)','Excel reference: target ±3s (pooled)']):
        for run,g in sensor[sensor.process_time>3].groupby('run'):
            ax.plot(g.process_time,g.si2h6_flow,label=run,lw=1.7)
        ax.axhspan(200-width,200+width,color='#2563eb',alpha=.07)
        for y in [200-width,200+width]: ax.axhline(y,c='#dc2626',ls='--',lw=1)
        ax.axhline(200,c='gray',ls=':'); ax.set(title=title,xlabel='Process time (s)',ylabel='Si2H6 flow (sccm)'); ax.legend()
    save(fig,'sensor_reference_bands.png')
    c=pd.read_csv(data/'condition_evaluation.csv')
    labels=c.recipe.str.replace('FT0524_','',regex=False)
    labels=[f'Pre ({i+1})' if x=='Pre' else x for i,x in enumerate(labels)]
    fig,ax=plt.subplots(figsize=(12,5.5)); x=np.arange(len(c))
    ax.axhspan(2800,3600,color='#16a34a',alpha=.09,label='Initial spec: 3,200 Å ± 400 Å')
    ax.errorbar(x,c.average_thickness,yerr=np.array([c.average_thickness-c.min_thickness,c.max_thickness-c.average_thickness]),fmt='o',ms=4,capsize=3,color='#64748b',label='Summary AVG with MIN–MAX')
    selected=c.recipe=='FT0524_run23'; ax.scatter(x[selected],c.average_thickness[selected],s=100,c='#2563eb',zorder=4,label='Run23 (45 / 49 measured points)')
    ax.axhline(3200,c='#16a34a',ls='--'); ax.set_xticks(x,labels,rotation=65,ha='right'); ax.set(ylabel='Thickness (Å)',title='Recipe comparison against the initial specification'); ax.legend(fontsize=8)
    save(fig,'initial_spec_comparison.png')
    p=pd.read_csv(data/'wafer_location_error_summary.csv')
    fig,axs=plt.subplots(1,2,figsize=(12,5))
    axs[0].bar(p.point,p.mean_absolute_deviation,color=['#dc2626' if i==49 else '#60a5fa' for i in p.point]); axs[0].set(xlabel='Measurement point',ylabel='Mean absolute deviation (Å)',title='Available-value mean per wafer; 23–25 wafers per point')
    sc=axs[1].scatter(p.x_mm,p.y_mm,c=p.mean_absolute_deviation,s=120,cmap='YlOrRd',edgecolor='white')
    for row in p.itertuples(): axs[1].text(row.x_mm,row.y_mm,str(row.point),ha='center',va='center',fontsize=6)
    axs[1].add_patch(plt.Circle((0,0),150,fill=False,color='gray',lw=1)); axs[1].set_aspect('equal'); axs[1].set(xlabel='x (mm)',ylabel='y (mm)',title='Point 49: 420.22 Å (24 valid wafers)'); fig.colorbar(sc,ax=axs[1],label='Mean absolute deviation (Å)',shrink=.8)
    save(fig,'wafer_location_deviation.png')
    r=pd.read_csv(data/'parameter_comparison.csv'); fig,axs=plt.subplots(1,3,figsize=(13,4.3))
    for temp,g in r[(r.power==300)&(r.si2h6_flow==175)].groupby('temperature'):
        g=g.sort_values('time_sec')
        for ax,col,label in zip(axs,['average_thickness','dep_rate_a_per_sec','uniformity_pct'],['AVG thickness (Å)','Deposition rate (Å/s)','Uniformity (%)']):
            ax.plot(g.time_sec,g[col],marker='o',label=f'{temp} °C'); ax.set(xlabel='Time (s)',ylabel=label); ax.legend()
    fig.suptitle('175 sccm / 300 W: source-summary comparison',fontsize=12)
    save(fig,'time_temperature_comparison.png')


if __name__=='__main__': render()
