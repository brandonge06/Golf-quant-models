import streamlit as st
import numpy as np
import os
import sys

# Ensure backend logic is accessible
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from markov_golf_engine import GolfHole

st.set_page_config(page_title="Strokes Gained: You vs PGA Tour Pros", layout="wide")

# --- Constants & Defaults ---
GROUPS = {
    'tee': ['tee_fairway', 'tee_rough', 'tee_bunker'],
    'fw': ['fw_green_short', 'fw_green_lag', 'fw_fringe', 'fw_wedge_50', 'fw_bunker'],
    'rough': ['rough_green_short', 'rough_green_lag', 'rough_fringe', 'rough_wedge_50', 'rough_bunker'],
    'fb': ['fb_green_short', 'fb_green_lag', 'fb_fringe', 'fb_wedge_50', 'fb_bunker', 'fb_stay_in'],
    'wedge_50': ['w50_green_short', 'w50_green_lag', 'w50_fringe', 'w50_wedge_30', 'w50_bunker'],
    'wedge_30': ['w30_green_short', 'w30_green_lag', 'w30_fringe', 'w30_wedge_15', 'w30_bunker'],
    'wedge_15': ['w15_green_short', 'w15_green_lag', 'w15_fringe', 'w15_tapin', 'w15_bunker'],
    'chip': ['chip_tapin', 'chip_short', 'chip_lag'],
    'sand': ['sand_green_short', 'sand_green_lag', 'sand_fringe', 'sand_bunker', 'sand_rough'],
}

DESCRIPTIONS = {
    'tee_fairway': 'Fairway %', 'tee_rough': 'Rough %', 'tee_bunker': 'Fairway Bunker %',
    'fw_green_short': 'Green Short (3-10ft) %', 'fw_green_lag': 'Green Lag (30ft+) %', 'fw_fringe': 'Missed Green (Chipping) %', 'fw_wedge_50': 'Wedge Range (50+ yds) %', 'fw_bunker': 'Greenside Bunker %',
    'rough_green_short': 'Green Short (3-10ft) %', 'rough_green_lag': 'Green Lag (30ft+) %', 'rough_fringe': 'Missed Green (Chipping) %', 'rough_wedge_50': 'Wedge Range (50+ yds) %', 'rough_bunker': 'Greenside Bunker %',
    'fb_green_short': 'Green Short (3-10ft) %', 'fb_green_lag': 'Green Lag (30ft+) %', 'fb_fringe': 'Missed Green (Chipping) %', 'fb_wedge_50': 'Wedge Range (50+ yds) %', 'fb_bunker': 'Greenside Bunker %', 'fb_stay_in': 'Stay in Fairway Bunker %',
    'w50_green_short': 'Green Short (3-10ft) %', 'w50_green_lag': 'Green Lag (30ft+) %', 'w50_fringe': 'Missed Green (Chipping) %', 'w50_wedge_30': 'Wedge Range (30-50 yds) %', 'w50_bunker': 'Greenside Bunker %',
    'w30_green_short': 'Green Short (3-10ft) %', 'w30_green_lag': 'Green Lag (30ft+) %', 'w30_fringe': 'Missed Green (Chipping) %', 'w30_wedge_15': 'Wedge Range (15-30 yds) %', 'w30_bunker': 'Greenside Bunker %',
    'w15_green_short': 'Green Short (3-10ft) %', 'w15_green_lag': 'Green Lag (30ft+) %', 'w15_fringe': 'Missed Green (Chipping) %', 'w15_tapin': 'Tap-in Range (<3ft) %', 'w15_bunker': 'Greenside Bunker %',
    'chip_tapin': 'Chip to Tap-in (<3ft) %', 'chip_short': 'Chip to Short (3-10ft) %', 'chip_lag': 'Chip to Green Lag (30ft+) %',
    'sand_green_short': 'Green Short (3-10ft) %', 'sand_green_lag': 'Green Lag (30ft+) %', 'sand_fringe': 'Missed Green (Chipping) %', 'sand_bunker': 'Stay in Bunker %', 'sand_rough': 'Escape to Rough %',
    'putt_lag_make': 'Lag Make (30ft+) %', 'putt_lag_to_tapin': 'Lag to Tap-in (<3ft) %', 'putt_lag_to_short': 'Lag to Short (3-10ft) %', 'putt_short_make': 'Short Putt Make (3-10ft) %'
}

DEFAULT_PRO = {
    'tee_fairway': 0.61, 'tee_rough': 0.35, 'tee_bunker': 0.04,
    'fw_green_short': 0.35, 'fw_green_lag': 0.40, 'fw_fringe': 0.20, 'fw_wedge_50': 0.03, 'fw_bunker': 0.02,
    'rough_green_short': 0.20, 'rough_green_lag': 0.28, 'rough_fringe': 0.22, 'rough_wedge_50': 0.25, 'rough_bunker': 0.05,
    'fb_green_short': 0.18, 'fb_green_lag': 0.30, 'fb_fringe': 0.30, 'fb_wedge_50': 0.15, 'fb_bunker': 0.05, 'fb_stay_in': 0.02,
    'w50_green_short': 0.40, 'w50_green_lag': 0.45, 'w50_fringe': 0.10, 'w50_wedge_30': 0.03, 'w50_bunker': 0.02,
    'w30_green_short': 0.55, 'w30_green_lag': 0.30, 'w30_fringe': 0.05, 'w30_wedge_15': 0.05, 'w30_bunker': 0.05,
    'w15_green_short': 0.70, 'w15_green_lag': 0.10, 'w15_fringe': 0.10, 'w15_tapin': 0.08, 'w15_bunker': 0.02,
    'chip_tapin': 0.25, 'chip_short': 0.65, 'chip_lag': 0.10,
    'sand_green_short': 0.68, 'sand_green_lag': 0.20, 'sand_fringe': 0.02, 'sand_bunker': 0.02, 'sand_rough': 0.08,
    'putt_lag_make': 0.07, 'putt_lag_to_tapin': 0.80, 'putt_lag_to_short': 0.13, 'putt_short_make': 0.88
}

DEFAULT_USER = {
    'tee_fairway': 0.40, 'tee_rough': 0.50, 'tee_bunker': 0.10,
    'fw_green_short': 0.10, 'fw_green_lag': 0.20, 'fw_fringe': 0.30, 'fw_wedge_50': 0.20, 'fw_bunker': 0.20,
    'rough_green_short': 0.05, 'rough_green_lag': 0.10, 'rough_fringe': 0.30, 'rough_wedge_50': 0.35, 'rough_bunker': 0.20,
    'fb_green_short': 0.05, 'fb_green_lag': 0.10, 'fb_fringe': 0.30, 'fb_wedge_50': 0.40, 'fb_bunker': 0.10, 'fb_stay_in': 0.05,
    'w50_green_short': 0.15, 'w50_green_lag': 0.35, 'w50_fringe': 0.20, 'w50_wedge_30': 0.15, 'w50_bunker': 0.15,
    'w30_green_short': 0.20, 'w30_green_lag': 0.40, 'w30_fringe': 0.20, 'w30_wedge_15': 0.10, 'w30_bunker': 0.10,
    'w15_green_short': 0.35, 'w15_green_lag': 0.35, 'w15_fringe': 0.10, 'w15_tapin': 0.10, 'w15_bunker': 0.10,
    'chip_tapin': 0.10, 'chip_short': 0.50, 'chip_lag': 0.40,
    'sand_green_short': 0.25, 'sand_green_lag': 0.25, 'sand_fringe': 0.10, 'sand_bunker': 0.30, 'sand_rough': 0.10,
    'putt_lag_make': 0.02, 'putt_lag_to_tapin': 0.40, 'putt_lag_to_short': 0.58, 'putt_short_make': 0.75
}

# --- State ---
if 'user_stats' not in st.session_state:
    st.session_state.user_stats = DEFAULT_USER.copy()
    for k, v in DEFAULT_USER.items(): st.session_state[f"user_slider_{k}"] = float(v * 100)

def on_user_slider_change(key):
    new_val = st.session_state[f"user_slider_{key}"] / 100.0
    group_key = next((g for g, keys in GROUPS.items() if key in keys), None)
    if group_key:
        others = [k for k in GROUPS[group_key] if k != key]
        remaining = 1.0 - new_val; current_o_sum = sum(st.session_state.user_stats[k] for k in others)
        if remaining <= 0:
            for k in others: st.session_state.user_stats[k] = 0.0
        elif current_o_sum > 0.001:
            for k in others: st.session_state.user_stats[k] = (st.session_state.user_stats[k] / current_o_sum) * remaining
        else:
            def_o_sum = sum(DEFAULT_USER[k] for k in others)
            for k in others: st.session_state.user_stats[k] = (DEFAULT_USER[k]/def_o_sum if def_o_sum>0 else 1/len(others)) * remaining
        st.session_state.user_stats[key] = new_val
        for k in others: st.session_state[f"user_slider_{k}"] = float(st.session_state.user_stats[k] * 100)
    else: st.session_state.user_stats[key] = new_val

def calculate_score(stats):
    try:
        states = ['Tee', 'Fairway', 'Rough', 'Wedge_50', 'Wedge_30', 'Wedge_15', 'Bunker_FW', 'Bunker_GS', 'Green_Fringe', 'Green_Lag', 'Green_Short', 'Green_TapIn', 'Hole']
        s = {state: i for i, state in enumerate(states)}
        P = np.zeros((len(states), len(states))); P[s['Hole'], s['Hole']] = 1.0
        P[s['Tee'], s['Fairway']] = stats['tee_fairway']; P[s['Tee'], s['Rough']] = stats['tee_rough']; P[s['Tee'], s['Bunker_FW']] = stats['tee_bunker']
        for st_n, pr in [('Fairway', 'fw_'), ('Rough', 'rough_')]:
            P[s[st_n], s['Green_Short']] = stats[f'{pr}green_short']; P[s[st_n], s['Green_Lag']] = stats[f'{pr}green_lag']; P[s[st_n], s['Green_Fringe']] = stats[f'{pr}fringe']; P[s[st_n], s['Wedge_50']] = stats[f'{pr}wedge_50']; P[s[st_n], s['Bunker_GS']] = stats[f'{pr}bunker']
        P[s['Bunker_FW'], s['Green_Short']] = stats['fb_green_short']; P[s['Bunker_FW'], s['Green_Lag']] = stats['fb_green_lag']; P[s['Bunker_FW'], s['Green_Fringe']] = stats['fb_fringe']; P[s['Bunker_FW'], s['Wedge_50']] = stats['fb_wedge_50']; P[s['Bunker_FW'], s['Bunker_GS']] = stats['fb_bunker']; P[s['Bunker_FW'], s['Bunker_FW']] = stats['fb_stay_in']
        P[s['Wedge_50'], s['Green_Short']] = stats['w50_green_short']; P[s['Wedge_50'], s['Green_Lag']] = stats['w50_green_lag']; P[s['Wedge_50'], s['Green_Fringe']] = stats['w50_fringe']; P[s['Wedge_50'], s['Wedge_30']] = stats['w50_wedge_30']; P[s['Wedge_50'], s['Bunker_GS']] = stats['w50_bunker']
        P[s['Wedge_30'], s['Green_Short']] = stats['w30_green_short']; P[s['Wedge_30'], s['Green_Lag']] = stats['w30_green_lag']; P[s['Wedge_30'], s['Green_Fringe']] = stats['w30_fringe']; P[s['Wedge_30'], s['Wedge_15']] = stats['w30_wedge_15']; P[s['Wedge_30'], s['Bunker_GS']] = stats['w30_bunker']
        P[s['Wedge_15'], s['Green_Short']] = stats['w15_green_short']; P[s['Wedge_15'], s['Green_Lag']] = stats['w15_green_lag']; P[s['Wedge_15'], s['Green_Fringe']] = stats['w15_fringe']; P[s['Wedge_15'], s['Green_TapIn']] = stats['w15_tapin']; P[s['Wedge_15'], s['Bunker_GS']] = stats['w15_bunker']
        P[s['Green_Fringe'], s['Green_TapIn']] = stats['chip_tapin']; P[s['Green_Fringe'], s['Green_Short']] = stats['chip_short']; P[s['Green_Fringe'], s['Green_Lag']] = stats['chip_lag']
        P[s['Bunker_GS'], s['Green_Short']] = stats['sand_green_short']; P[s['Bunker_GS'], s['Green_Lag']] = stats['sand_green_lag']; P[s['Bunker_GS'], s['Green_Fringe']] = stats['sand_fringe']; P[s['Bunker_GS'], s['Bunker_GS']] = stats['sand_bunker']; P[s['Bunker_GS'], s['Rough']] = stats['sand_rough']
        P[s['Green_Lag'], s['Hole']] = stats['putt_lag_make']; P[s['Green_Lag'], s['Green_TapIn']] = stats['putt_lag_to_tapin']; P[s['Green_Lag'], s['Green_Short']] = stats['putt_lag_to_short']
        P[s['Green_Short'], s['Hole']] = stats['putt_short_make']; P[s['Green_Short'], s['Green_TapIn']] = 1.0 - stats['putt_short_make']
        P[s['Green_TapIn'], s['Hole']] = 0.99; P[s['Green_TapIn'], s['Green_TapIn']] = 0.01
        for i in range(len(states)):
            if i != s['Hole']:
                row_sum = P[i].sum()
                if row_sum > 0: P[i] /= row_sum
        return GolfHole(states, P).calculate_expected_steps('Tee')
    except Exception: return 0.0

# --- Helper Rendering ---
def pga_s(key):
    val = float(DEFAULT_PRO.get(key, 0.88) * 100)
    st.slider(DESCRIPTIONS[key], 0.0, 100.0, val, key=f"p_s_{key}", disabled=True)

def user_s(key):
    st.slider(DESCRIPTIONS[key], 0.0, 100.0, key=f"user_slider_{key}", on_change=on_user_slider_change, args=(key,))

def render_col_content(is_pga):
    draw = pga_s if is_pga else user_s
    with st.expander("Off the Tee", expanded=True):
        for k in GROUPS['tee']: draw(k)
    with st.expander("Approach Play", expanded=True):
        with st.expander("From Fairway", expanded=True):
            for k in GROUPS['fw']: draw(k)
        with st.expander("From Rough", expanded=True):
            for k in GROUPS['rough']: draw(k)
        with st.expander("From Fairway Bunker", expanded=True):
            for k in GROUPS['fb']: draw(k)
    with st.expander("Wedge Game", expanded=True):
        with st.expander("50+ Yards", expanded=True):
            for k in GROUPS['wedge_50']: draw(k)
        with st.expander("30-50 Yards", expanded=True):
            for k in GROUPS['wedge_30']: draw(k)
        with st.expander("15-30 Yards", expanded=True):
            for k in GROUPS['wedge_15']: draw(k)
        with st.expander("Chipping Game", expanded=True):
            for k in GROUPS['chip']: draw(k)
    with st.expander("Greenside Bunker Game", expanded=True):
        for k in GROUPS['sand']: draw(k)
    with st.expander("Putting", expanded=True):
        for k in ['putt_lag_make', 'putt_lag_to_tapin', 'putt_lag_to_short', 'putt_short_make']: draw(k)

# --- App ---
st.title("⛳ Strokes Gained: You vs PGA Tour Pros")
st.markdown("---")
pga_score, user_score = calculate_score(DEFAULT_PRO), calculate_score(st.session_state.user_stats)
c1, c2 = st.columns(2)
with c1:
    st.markdown("### Average PGA Tour Metrics")
    st.markdown(f"<h1 style='color: #2563eb; margin-top: -20px;'>{pga_score:.2f}</h1>", unsafe_allow_html=True)
    render_col_content(True)
with c2:
    st.markdown("### Your Performance")
    st.markdown(f"<h1 style='color: #16a34a; margin-top: -20px;'>{user_score:.2f}</h1>", unsafe_allow_html=True)
    render_col_content(False)

st.markdown("---")
st.markdown(f"<div style='text-align: center; padding: 20px; background: #111827; border-radius: 50px; color: white;'><span style='font-size: 14px; text-transform: uppercase; letter-spacing: 2px; color: #9ca3af;'>Your Strokes Gained</span><br/><span style='font-size: 48px; font-weight: 900;'>{pga_score - user_score:.2f}</span></div>", unsafe_allow_html=True)

if st.button("🚀 Analyze My Game", use_container_width=True):
    st.markdown("### 📊 Comprehensive Performance Analysis")
    cats = {"Off the Tee": GROUPS['tee'], "Approach Play": GROUPS['fw'] + GROUPS['rough'] + GROUPS['fb'], "Wedge Game": GROUPS['wedge_50'] + GROUPS['wedge_30'] + GROUPS['wedge_15'] + GROUPS['chip'], "Greenside Bunkers": GROUPS['sand'], "Putting": ['putt_lag_make', 'putt_lag_to_tapin', 'putt_lag_to_short', 'putt_short_make']}
    pots = []
    for name, keys in cats.items():
        stats = st.session_state.user_stats.copy()
        for k in keys: stats[k] = DEFAULT_PRO.get(k, 0.88)
        gain = user_score - calculate_score(stats)
        pots.append((name, gain))
    pots.sort(key=lambda x: x[1], reverse=True)
    ca, cb = st.columns([2, 1])
    with ca:
        for i, (name, gain) in enumerate(pots):
            is_out = gain < 0; abs_gain = abs(gain); color = "#16a34a" if is_out else "#dc2626" if i == 0 else "#2563eb"
            label = f"Gaining <b style='color: {color}'>{abs_gain:.2f} strokes</b> over PGA average." if is_out else f"Potential to gain <b style='color: {color}'>{abs_gain:.2f} strokes</b> by matching PGA average."
            st.markdown(f'<div style="background: white; padding: 15px; border-radius: 10px; border-left: 5px solid {color}; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"><span style="font-weight: 800; font-size: 18px;">{i+1}. {name}</span><br/><span style="color: #6b7280; font-size: 14px;">{label}</span></div>', unsafe_allow_html=True)
    with cb:
        top_l, top_s = pots[0], pots[-1]
        if top_s[1] < 0: st.success(f"**Elite Skill:** You are outperforming the PGA average in **{top_s[0]}**.")
        else: st.success(f"**Best Consistency:** Your **{top_s[0]}** is your most reliable category.")
        if top_l[1] > 0:
            st.error(f"**Biggest Opportunity:** Focus your practice on **{top_l[0]}**.")
            st.info(f"**Goal:** Closing just 20% of this gap saves **{top_l[1] * 0.2:.2f} strokes** per hole.")
    st.balloons()
