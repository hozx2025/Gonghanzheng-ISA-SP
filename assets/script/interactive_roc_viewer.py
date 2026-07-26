"""
interactive_roc_viewer.py
读取 ROC_Comparison_Data.csv，生成交互式 ROC 对比图。
- 独立运行时：matplotlib 窗口 + 复选框
- Quarto 环境中：返回 Plotly 交互式图表
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
import plotly.graph_objects as go
import plotly.io as pio

# =========================================================================
# 与原始脚本一致的颜色常量
# =========================================================================
VISUAL_COLORS = {
    'PRIMARY_MODEL_COLOR': 'darkred',
    'REFERENCE_LINE_STYLE': "#333333",
}

# 图例顺序及对应颜色（与 regenerate_roc_comparison.py 中 SINGLE_MODAL_ORDER 一致）
CURVE_CONFIG = [
    # (索引, 标签关键字,           颜色,           线型,  线宽, alpha, 是填充)
    (0, 'Fusion',                 'darkred',       '-',   2.0,  1.0,   False),
    (1, 'Fusion 95% CI',          'darkred',       None,  0,    0.15,  True),
    (2, 'Infrared thermography',  'tab:blue',      '-',   1.0,  0.8,   False),
    (3, 'Tongue and pulse diagnosis', 'tab:orange','-',   1.0,  0.8,   False),
    (4, 'Clinical baseline',      'tab:green',     '-',   1.0,  0.8,   False),
    (5, 'Physical and chemical examination', (242/255, 60/255, 60/255), '-', 1.0, 0.8, False),
    (6, 'Random Guess',           VISUAL_COLORS['REFERENCE_LINE_STYLE'], '--', 1.0, 0.8, False),
]


# =========================================================================
# 从 CSV 读取数据
# =========================================================================
def load_data(csv_path):
    """读取 ROC_Comparison_Data.csv，返回绘图所需的所有数组。"""
    df = pd.read_csv(csv_path)

    # --- Fusion ---
    fusion_df = df[df['Curve'] == 'Fusion'].copy()
    if fusion_df.empty:
        raise ValueError("No 'Fusion' curve data found in CSV.")

    mean_fpr  = fusion_df['FPR'].astype(float).values
    mean_tpr  = fusion_df['TPR'].astype(float).values
    tpr_lower = fusion_df['TPR_Lower'].astype(float).values
    tpr_upper = fusion_df['TPR_Upper'].astype(float).values

    auc_mean     = float(fusion_df.iloc[0]['AUC'])
    auc_ci_lower = float(fusion_df.iloc[0]['AUC_CI_Lower'])
    auc_ci_upper = float(fusion_df.iloc[0]['AUC_CI_Upper'])

    # --- 单模态 ---
    single_curves = {}
    for curve_name in df['Curve'].unique():
        if curve_name == 'Fusion':
            continue
        sub = df[df['Curve'] == curve_name]
        single_curves[curve_name] = {
            'fpr': sub['FPR'].astype(float).values,
            'tpr': sub['TPR'].astype(float).values,
            'auc': float(sub.iloc[0]['AUC']),
        }

    return (mean_fpr, mean_tpr, tpr_lower, tpr_upper,
            auc_mean, auc_ci_lower, auc_ci_upper, single_curves)


# =========================================================================
# 构建绘图 + 复选框
# =========================================================================
def build_plot(csv_path):
    """返回 fig, ax, artists（7个图形对象）, labels（7个标签）。"""

    (mean_fpr, mean_tpr, tpr_lower, tpr_upper,
     auc_mean, auc_ci_lower, auc_ci_upper, single_curves) = load_data(csv_path)

    fig, ax = plt.subplots(figsize=(9, 8))
    plt.subplots_adjust(bottom=0.28)  # 为复选框留空间

    artists = []   # 7 个元素，与 CURVE_CONFIG 一一对应
    labels  = []   # 7 个完整图例文本

    # ---- 0. Fusion 主线 ----
    cfg = CURVE_CONFIG[0]
    line_fusion, = ax.plot(mean_fpr, mean_tpr,
                           color=cfg[2], lw=cfg[4], alpha=cfg[5],
                           label=f'Fusion (AUC={auc_mean:.3f} '
                                 f'[{auc_ci_lower:.3f}-{auc_ci_upper:.3f}])')
    artists.append(line_fusion)
    labels.append(line_fusion.get_label())

    # ---- 1. Fusion 95% CI (fill_between) ----
    cfg = CURVE_CONFIG[1]
    ci_fill = ax.fill_between(mean_fpr, tpr_lower, tpr_upper,
                              color=cfg[2], alpha=cfg[5],
                              label='Fusion 95% CI')
    artists.append(ci_fill)
    labels.append('Fusion 95% CI')

    # ---- 2–5. 单模态 ----
    single_order = [
        'Infrared thermography',
        'Tongue and pulse diagnosis',
        'Clinical baseline',
        'Physical and chemical examination',
    ]
    for idx, display_name in enumerate(single_order):
        cfg = CURVE_CONFIG[2 + idx]
        sd = single_curves.get(display_name)
        if sd is not None:
            line, = ax.plot(sd['fpr'], sd['tpr'],
                           color=cfg[2], lw=cfg[4], alpha=cfg[5],
                           label=f'{display_name} (AUC={sd["auc"]:.3f})')
            artists.append(line)
            labels.append(line.get_label())
        else:
            artists.append(None)
            labels.append(f'{display_name} (N/A)')

    # ---- 6. Random Guess ----
    cfg = CURVE_CONFIG[6]
    line_rg, = ax.plot([0, 1], [0, 1],
                       color=cfg[2], linestyle=cfg[3],
                       lw=cfg[4], alpha=cfg[5],
                       label='Random Guess')
    artists.append(line_rg)
    labels.append('Random Guess')

    # ---- 轴格式（与原始完全一致） ----
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.01])
    ax.set_xlabel('False Positive Rate (1 - Specificity)')
    ax.set_ylabel('True Positive Rate (Sensitivity)')
    ax.set_title('ROC: Fusion (with 95% CI) vs Single-modality')
    ax.legend(loc='lower right')
    ax.grid(alpha=0.25)

    return fig, ax, artists, labels


# =========================================================================
# Plotly HTML 导出（用于嵌入 Quarto / 网页）
# =========================================================================
# 颜色映射（tab 系列展开为 hex，与 CURVE_CONFIG 一一对应）
PLOTLY_COLORS = {
    'Fusion':        'darkred',
    'Fusion 95% CI': 'rgba(139,0,0,0.15)',
    'Infrared thermography':            '#1f77b4',
    'Tongue and pulse diagnosis':       '#ff7f0e',
    'Clinical baseline':                '#2ca02c',
    'Physical and chemical examination':'rgb(242,60,60)',
    'Random Guess':                     '#333333',
}


def create_plotly_figure(csv_path):
    """
    读取 CSV，返回 Plotly Figure 对象。
    图例点击即可切换曲线显隐。

    Returns
    -------
    go.Figure
    """
    (mean_fpr, mean_tpr, tpr_lower, tpr_upper,
     auc_mean, auc_ci_lower, auc_ci_upper, single_curves) = load_data(csv_path)

    fig = go.Figure()

    # ── 1. Fusion 95% CI 带（先画在底层） ──
    fig.add_trace(go.Scatter(
        x=np.concatenate([mean_fpr, mean_fpr[::-1]]),
        y=np.concatenate([tpr_upper, tpr_lower[::-1]]),
        fill='toself',
        fillcolor='rgba(139,0,0,0.15)',
        line=dict(width=0),
        name='Fusion 95% CI',
        showlegend=True,
        legendgroup='fusion',
    ))

    # ── 2. Fusion 主线 ──
    fig.add_trace(go.Scatter(
        x=mean_fpr, y=mean_tpr,
        mode='lines',
        line=dict(color='darkred', width=3),
        name=f'Fusion (AUC={auc_mean:.3f} [{auc_ci_lower:.3f}-{auc_ci_upper:.3f}])',
        legendgroup='fusion',
    ))

    # ── 3–6. 单模态 ──
    single_order = [
        'Infrared thermography',
        'Tongue and pulse diagnosis',
        'Clinical baseline',
        'Physical and chemical examination',
    ]
    for name in single_order:
        sd = single_curves.get(name)
        if sd is None:
            continue
        fig.add_trace(go.Scatter(
            x=sd['fpr'], y=sd['tpr'],
            mode='lines',
            line=dict(color=PLOTLY_COLORS[name], width=1.5),
            name=f'{name} (AUC={sd["auc"]:.3f})',
        ))

    # ── 7. Random Guess ──
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        line=dict(color='#333333', width=1.5, dash='dash'),
        name='Random Guess',
    ))

    # ── 布局 ──
    fig.update_layout(
        xaxis_title='False Positive Rate (1 - Specificity)',
        yaxis_title='True Positive Rate (Sensitivity)',
        xaxis=dict(range=[-0.01, 1.01]),
        yaxis=dict(range=[-0.01, 1.01], scaleanchor='x', scaleratio=1),
        legend=dict(x=0.55, y=0.15, bgcolor='rgba(255,255,255,0.85)'),
        template='plotly_white',
        hovermode='closest',
        autosize=True,
        height=700,
    )

    return fig


def export_plotly_html(csv_path, output_html):
    """
    读取 CSV，生成交互式 Plotly 图表并保存为自包含 HTML。
    图例点击即可切换曲线显隐。
    """
    fig = create_plotly_figure(csv_path)
    fig.write_html(output_html, include_plotlyjs='cdn', full_html=True)
    print(f"Plotly interactive HTML saved to: {output_html}")
    return output_html


# =========================================================================
# 环境检测 & 自动执行入口
# =========================================================================
def _is_notebook():
    """检测是否在 Jupyter / Quarto / IPython 环境中运行。"""
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except ImportError:
        return False


# ---- 自动定位 CSV 文件 ----
_CSV_CANDIDATES = [
    'assets/data/ROC_Comparison_Data_new.csv',                               # Quarto 项目根
    os.path.join('训练结果', '20251129_192458_loss稳定',
                 'figures', 'ROC_Comparison_Data_new.csv'),
    os.path.join('训练结果', '20251129_192458_loss稳定',
                 'figures', 'ROC_Comparison_Data.csv'),
]
_csv_path = next((c for c in _CSV_CANDIDATES if os.path.exists(c)), None)
if _csv_path is None:
    raise FileNotFoundError(
        "CSV not found. Tried:\n  " + "\n  ".join(_CSV_CANDIDATES))

print(f"Loading: {_csv_path}")

# ---- 根据运行环境选择输出方式 ----
if _is_notebook():
    # Quarto / Jupyter: 显示 Plotly 交互式图表（图例点击切换显隐）
    from IPython.display import display as _ipython_display
    _plotly_fig = create_plotly_figure(_csv_path)
    _ipython_display(_plotly_fig)
else:
    # 独立 .py 运行: matplotlib 窗口 + 复选框
    fig, ax, artists, labels = build_plot(_csv_path)

    valid_indices = [i for i, a in enumerate(artists) if a is not None]
    valid_artists = [artists[i] for i in valid_indices]
    valid_labels  = [labels[i]  for i in valid_indices]

    short_labels = []
    for lbl in valid_labels:
        short_labels.append(lbl.split(' (AUC=')[0] if ' (AUC=' in lbl else lbl)

    check_ax = plt.axes([0.12, 0.04, 0.78, 0.18])
    check = CheckButtons(check_ax, short_labels, [True] * len(valid_labels))

    def toggle_visibility(label_text):
        idx = short_labels.index(label_text)
        valid_artists[idx].set_visible(not valid_artists[idx].get_visible())
        fig.canvas.draw_idle()

    check.on_clicked(toggle_visibility)
    plt.show()