# ⛳ Golf Quant: Strokes Gained Predictor

A quantitative golf performance model built using **Markov Chains** to simulate and predict expected scores. This tool allows users to compare their granular performance metrics against **2024-2025 PGA Tour ShotLink benchmarks** and identifies exactly where they are losing strokes.

---

## 🚀 Features

### 1. Comparative Performance Dashboard
- **Average PGA Tour Metrics:** A fixed, unmovable benchmark based on elite professional data.
- **Your Performance:** Interactive sliders to model your own game across every facet of golf.
- **Side-by-Side Visuals:** Perfectly aligned columns with vibrant blue benchmarks and green user-driven metrics.

### 2. Deep Modeling of the Game
- **Off the Tee:** Model Fairway %, Rough %, and Fairway Bunker % tendencies.
- **Approach Play:** Unified modeling for shots from the Fairway, Rough, and Fairway Bunkers.
- **Granular Wedge Game:** Detailed breakdown of performance from three distinct yardage tiers:
    - **50+ Yards**
    - **30-50 Yards**
    - **15-30 Yards**
- **The Chipping Game:** Dedicated logic for "fringe/rough" misses next to the green.
- **Greenside Bunker Game:** Models "Up & Down" potential based on proximity and sand save data.
- **Advanced Putting:** Models Lag Putting (30ft+) leave distribution and Short Putt (3-10ft) conversion rates.

### 3. "Analyze My Game" Engine
Click the **🚀 Analyze My Game** button to run a Comprehensive Strokes Gained Potential analysis. 
- **Impact Ranking:** Identifies which category (e.g., Putting vs. Approach) offers the highest scoring improvement if moved to PGA standards.
- **Statistical Superpowers:** Highlights where you are currently outperforming the pros.
- **Practice Priorities:** Quantifies exactly how many strokes you'd save by closing just 20% of the gap in your weakest area.

---

## 🛠️ Technical Architecture

### The Markov Engine (`backend/markov_golf_engine.py`)
The project models a single golf hole as a **Discrete-Time Markov Chain (DTMC)**. 
- **Absorption State:** The "Hole" acts as an absorbing state.
- **Transient States:** Tee, Fairway, Rough, Fairway Bunker, Greenside Bunker, Wedge Ranges, Fringe, and various Green tiers.
- **The Fundamental Matrix ($N$):** The model calculates expected strokes using the formula $E = (I - Q)^{-1} \cdot \mathbf{1}$, where $Q$ is the sub-matrix of transient states.

### Frontend
- **Streamlit:** Powers the interactive, data-driven UI.
- **Custom CSS:** Injected to ensure horizontal alignment, consistent component heights, and professional branding (PGA Blue vs. User Green).

---

## 📊 Data Sources (2024-2025 PGA Tour)
Benchmarks are derived from **PGA Tour ShotLink** data. Detailed documentation of the probabilities used (GIR rates, proximity to hole, sand save %, etc.) can be found in `PGA_TOUR_STATS_DOCUMENTATION.txt`.

**Key Benchmarks:**
- **PGA 50/50 Putting Mark:** ~8 Feet.
- **PGA Scrambling (Rough/Sand):** ~54-58%.
- **PGA GIR (Fairway):** ~68-72%.

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- `pip` (or `python3 -m pip`)

### 1. Clone the Repository
```bash
git clone https://github.com/brandonge06/Golf-quant-models.git
cd Golf-quant-models/golf-quant-app
```

### 2. Install Dependencies
```bash
python3 -m pip install streamlit numpy pandas
```

### 3. Run the Application
```bash
python3 -m streamlit run app.py
```

---

## 📈 Strokes Gained Logic
The application calculates **Strokes Gained (SG)** as:
$$	ext{SG} = 	ext{Expected Strokes (PGA)} - 	ext{Expected Strokes (User)}$$
- A **Positive SG** indicates you are outperforming the PGA benchmark in that category.
- A **Negative SG** indicates a "stroke leak" where your current stats are costing you shots relative to a pro.

---

## 📂 Project Structure
```text
golf-quant-app/
├── app.py                          # Main Streamlit Application
├── PGA_TOUR_STATS_DOCUMENTATION.txt # Statistical breakdown & sources
├── backend/
│   ├── markov_golf_engine.py       # Core Markov Chain math engine
│   └── main.py                     # (Legacy) FastAPI Backend
└── frontend/                       # (Legacy) React/TypeScript Frontend
```

---

## 🤝 Contributing
Contributions to refine the Markov transitions or add course-specific modeling are welcome. Please ensure any statistical updates are documented with reliable sources.
