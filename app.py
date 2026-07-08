from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib

app = Flask(__name__)

preprocessor = joblib.load("models/preprocessor.joblib")
model = joblib.load("models/dt_model.joblib")
label_encoder = joblib.load("models/label_encoder.joblib")

categorical_cols = ["protocol_type", "service", "flag"]
numeric_cols = [
    "duration", "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent",
    "hot", "num_failed_logins", "logged_in", "num_compromised", "root_shell",
    "su_attempted", "num_root", "num_file_creations", "num_shells",
    "num_access_files", "num_outbound_cmds", "is_host_login", "is_guest_login",
    "count", "srv_count", "serror_rate", "srv_serror_rate", "rerror_rate",
    "srv_rerror_rate", "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate",
    "dst_host_count", "dst_host_srv_count", "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
    "dst_host_srv_serror_rate", "dst_host_rerror_rate", "dst_host_srv_rerror_rate",
]

feature_cols = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins",
    "logged_in", "num_compromised", "root_shell", "su_attempted",
    "num_root", "num_file_creations", "num_shells", "num_access_files",
    "num_outbound_cmds", "is_host_login", "is_guest_login", "count",
    "srv_count", "serror_rate", "srv_serror_rate", "rerror_rate",
    "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate",
]

@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


@app.route("/compare")
def compare():
    return render_template("compare.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/docs")
def docs():
    return render_template("docs.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files["file"]
        df = pd.read_csv(file, header=None)
        df.columns = feature_cols

        X_raw = df[categorical_cols + numeric_cols]
        X_transformed = preprocessor.transform(X_raw)

        preds = model.predict(X_transformed)
        probs = model.predict_proba(X_transformed)
        confidences = probs.max(axis=1)

        labels = label_encoder.inverse_transform(preds)

        return jsonify({
            "predictions": labels.tolist(),
            "confidences": confidences.tolist()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route("/explain")
def explain():
    try:
        feature_names = preprocessor.get_feature_names_out()
        importances = model.feature_importances_

        top_idx = importances.argsort()[::-1][:8]
        top_features = [
            {"feature": feature_names[i], "importance": float(importances[i])}
            for i in top_idx
        ]

        return jsonify({"top_features": top_features})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["file"]
        df = pd.read_csv(file, header=None)

        if df.shape[1] != 41:
            return jsonify({"error": f"Expected 41 columns, got {df.shape[1]}"}), 400

        return jsonify({"status": "valid", "rows": len(df), "columns": df.shape[1]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    



@app.route("/compare-models")
def compare_models():
    comparison = [
        {"method": "Random Forest (baseline)", "accuracy": 0.7441, "precision": 0.7996, "recall": 0.7441, "f1": 0.6987, "r2l_recall": 0.02},
        {"method": "RF + SMOTE + GridSearch", "accuracy": 0.7401, "precision": 0.8037, "recall": 0.7401, "f1": 0.6965, "r2l_recall": 0.03},
        {"method": "Decision Tree + SMOTE", "accuracy": 0.7989, "precision": 0.80, "recall": 0.80, "f1": 0.77, "r2l_recall": 0.12},
        {"method": "DT + SMOTE + GridSearch", "accuracy": 0.7443, "precision": 0.79, "recall": 0.7443, "f1": 0.71, "r2l_recall": 0.08},
        {"method": "RF + DT Voting Ensemble", "accuracy": 0.7627, "precision": 0.80, "recall": 0.7627, "f1": 0.71, "r2l_recall": 0.00},
    ]
    return jsonify(comparison)


iso_forest = joblib.load("models/iso_forest.joblib")

@app.route("/anomaly-check", methods=["POST"])
def anomaly_check():
    try:
        file = request.files["file"]
        df = pd.read_csv(file, header=None)
        df.columns = feature_cols

        X_raw = df[categorical_cols + numeric_cols]
        X_transformed = preprocessor.transform(X_raw)

        iso_preds = iso_forest.predict(X_transformed)
        is_anomaly = (iso_preds == -1)

        return jsonify({
            "total": len(is_anomaly),
            "anomalies_flagged": int(is_anomaly.sum()),
            "flags": is_anomaly.tolist()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run()