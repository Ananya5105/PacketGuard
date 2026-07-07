# PacketGuard

**A machine-learning network intrusion detection dashboard**, built on the NSL-KDD benchmark dataset. Upload traffic data and get real-time attack classification, model comparison, explainability, and unsupervised anomaly detection — all in one dashboard.

> Mini Project — B.Tech Computer Science (Cybersecurity Track)

---

## What it does

Intrusion detection is usually taught as a taxonomy — signature-based vs. anomaly-based, DoS vs. Probe vs. R2L vs. U2R — without ever training a classifier on real labelled attack traffic and watching it succeed or fail on unseen data. PacketGuard closes that gap:

1. Upload a CSV of network traffic in NSL-KDD format (41 features, no header row).
2. A trained classifier labels every flow as **Normal**, **DoS**, **Probe**, **R2L**, or **U2R**.
3. Results render as an interactive dashboard — risk gauge, category breakdown, per-class confidence — instead of a printed accuracy number.
4. A parallel **unsupervised anomaly detector** (Isolation Forest) flags statistically abnormal traffic independent of the classifier, demonstrating the anomaly-based vs. signature-based IDS paradigms side by side on the same data.
5. Every prediction can be explained via feature importance, and every model that was tried during development is benchmarked openly rather than only shipping the winner.

## Features

- **Live classification** — upload traffic, get instant category breakdown with confidence scores and severity ratings
- **Multi-model comparison** — Random Forest, Decision Tree, SMOTE-balanced variants, and a voting ensemble benchmarked side by side on accuracy, precision, recall, F1, and R2L recall, with interactive charts
- **Explainability** — see exactly which traffic features the model relies on most for a given prediction
- **Anomaly detection** — an Isolation Forest catches statistically abnormal traffic the classifier was never trained to name
- **Attack category reference** — plain-language docs page explaining what DoS/Probe/R2L/U2R actually mean

## Tech stack

| Layer | Tools |
|---|---|
| Model training | Python, pandas, scikit-learn, imbalanced-learn (SMOTE) |
| Serving | Flask |
| Frontend | HTML/CSS (vanilla), Chart.js |
| Dataset | NSL-KDD (`KDDTrain+.txt` / `KDDTest+.txt`) |
| Deployment | Render (or any WSGI-compatible host) |

## Project structure

```
packetguard/
├── app.py                      # Flask app — routes + inference endpoints
├── models/
│   ├── preprocessor.joblib     # ColumnTransformer (OneHotEncoder + StandardScaler)
│   ├── dt_model.joblib         # Best classifier — Decision Tree + SMOTE
│   ├── label_encoder.joblib    # Maps model output → category name
│   └── iso_forest.joblib       # Isolation Forest for anomaly detection
├── templates/
│   ├── landing.html            # Marketing/intro page
│   ├── index.html              # Dashboard — upload, classify, explain, detect anomalies
│   ├── compare.html            # Model comparison page with live charts
│   ├── about.html               # Project write-up + key findings
│   └── docs.html                # Usage guide + attack category glossary
└── notebooks/
    └── baseline_tor_project_.ipynb   # Training notebook — preprocessing, model training, evaluation
```

## Getting started

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd packetguard
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install flask pandas scikit-learn joblib imbalanced-learn
```

### 2. Get the dataset and train the models

Download NSL-KDD (`KDDTrain+.txt`, `KDDTest+.txt`) and run through `notebooks/baseline_tor_project_.ipynb`. This will:

- Build a `ColumnTransformer` (one-hot encode `protocol_type`/`service`/`flag`, scale the 38 numeric features)
- Map raw attack labels to the 5 standard categories (Normal, DoS, Probe, R2L, U2R)
- Train and compare Random Forest, SMOTE-balanced Random Forest (+ GridSearch), Decision Tree (+ SMOTE), tuned Decision Tree, and a RF+DT voting ensemble
- Save the best-performing pipeline to `models/`

You'll also need to separately train and save an `IsolationForest` on the same preprocessed features as `models/iso_forest.joblib` for the anomaly-detection endpoint.

### 3. Run the app

```bash
python app.py
```

Visit `http://localhost:5000` for the landing page, or `/dashboard` to go straight to the classifier.

## Model results

| Model | Accuracy | Precision | Recall | F1 | R2L Recall |
|---|---|---|---|---|---|
| Random Forest (baseline) | 74.41% | 79.96% | 74.41% | 69.87% | 2% |
| RF + SMOTE + GridSearch | 74.01% | 80.37% | 74.01% | 69.65% | 3% |
| **Decision Tree + SMOTE ★** | **76.65%** | 77.00% | 77.00% | 74.00% | **12%** |
| DT + SMOTE + GridSearch | 74.43% | 79.00% | 74.43% | 71.00% | 8% |
| RF + DT Voting Ensemble | 76.27% | 80.00% | 76.27% | 71.00% | 0% |

**Best result:** Decision Tree + SMOTE, deployed as the production model.

**Key finding:** R2L and U2R recall stays low (2–12%) across every model tested, even after SMOTE oversampling and hyperparameter tuning. Feature-importance analysis shows models lean on traffic-volume features (byte counts, connection counts) rather than the login/content features (`num_failed_logins`, `root_shell`, `num_compromised`) that R2L attacks actually depend on — pointing to a data-level generalization ceiling rather than a tuning problem, since `KDDTest+` intentionally includes attack subtypes absent from training data.

## API reference

| Route | Method | Description |
|---|---|---|
| `/` | GET | Landing page |
| `/dashboard` | GET | Upload + live classification dashboard |
| `/compare` | GET | Model comparison page with charts |
| `/about` | GET | Project write-up |
| `/docs` | GET | Usage guide + attack category glossary |
| `/predict` | POST | Upload a CSV, get per-row predictions + confidence |
| `/explain` | GET | Top 8 features by importance for the current model |
| `/upload` | POST | Validate a CSV has the expected 41 columns |
| `/compare-models` | GET | Benchmark table for all models tried during development |
| `/anomaly-check` | POST | Upload a CSV, get Isolation Forest anomaly flags |

`/predict`, `/upload`, and `/anomaly-check` expect a CSV with **41 columns, no header row**, in NSL-KDD feature order.

## Known limitations

- R2L/U2R detection is weak across every model tried (see above) — a known limitation of NSL-KDD rather than something a smarter model alone would fix.
- The classifier only recognizes the 5 broad categories, not specific attack subtypes.
- Anomaly detection (Isolation Forest) and the supervised classifier run independently; their outputs aren't currently fused into a single confidence score.

## Future scope

- Raw `.pcap` → flow-feature extraction (via Scapy), so raw captures — not just pre-cleaned CSVs — can be classified
- Deep-learning classifier (LSTM/CNN over flow sequences) as a comparison point against the classical ML baseline
- Streaming-replay simulation mode to mimic a live SOC monitoring feed
- Scan-history persistence (SQLite) and automated PDF/CSV incident reports
- Automated testing (pytest) + CI with an accuracy-regression check on every push

## References

- Tavallaee, M., Bagheri, E., Lu, W., Ghorbani, A. — *A Detailed Analysis of the KDD CUP 99 Data Set* (basis for NSL-KDD), 2009.
- scikit-learn documentation — Ensemble methods and Isolation Forest.
- Lundberg, S. M., Lee, S.-I. — *A Unified Approach to Interpreting Model Predictions* (SHAP), NeurIPS 2017.
