import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# Check if sentence-transformers is installed, use a mock or standard encoder fallback
# to avoid crash if the user hasn't installed sentence-transformers yet.
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

# ---------------------------------------------------------
# 1. Dataset Initialization
# ---------------------------------------------------------
# A realistic dataset representing customer feedback reviews across 5 categories
feedback_dataset = [
    # Category 0: UI / Viewport / Mobile styling bugs
    "The checkout page layout is completely broken on my iPhone viewport.",
    "Mobile menu button does not open when clicked on Android screens.",
    "misaligned grid elements on the dashboard page layout.",
    "Button labels overlapping with text on mobile screens.",
    # Category 1: Performance / Latency / Lag
    "Extremely slow load times when opening the search dashboard.",
    "Database queries are taking over 5 seconds to complete on checkout.",
    "App freezes for a few seconds whenever I update my profile data.",
    "Highly laggy page scrolling performance on catalog views.",
    # Category 2: Payment / Checkout issues
    "The credit card payment gateway returns a timeout 500 error.",
    "Transaction failed but my account was debited during checkout.",
    "Checkout page displays invalid gateway error message.",
    "Unable to process international cards on payment portal.",
    # Category 3: Export / Reporting feature requests
    "Requesting a feature to export search reports to CSV or Excel sheets.",
    "Can we get a download PDF button for billing transactions?",
    "Need the ability to email monthly activity summaries automatically.",
    "Add a CSV export button to the inventory management screen.",
    # Category 4: Authentication & Login
    "Cannot reset password, the verification link returns a 404 page.",
    "JWT token expires too fast, prompting user login every 10 minutes.",
    "Two-factor authentication code is never received via SMS.",
    "Login API returns an unauthorized error despite valid credentials."
]

# ---------------------------------------------------------
# 2. Vectorization & Feature Representation
# ---------------------------------------------------------
print("--- 1. Feature Representation ---")
# TF-IDF Pipeline
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(feedback_dataset)
print(f"TF-IDF Matrix Shape: {tfidf_matrix.shape} (Documents, Features)")

# Sentence Transformers (all-MiniLM-L6-v2) Pipeline
if HAS_SENTENCE_TRANSFORMERS:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings_matrix = model.encode(feedback_dataset)
    print(f"Sentence Embeddings Shape: {embeddings_matrix.shape} (Documents, Embeddings Dimension)")
else:
    # Fallback to TF-IDF as surrogate mock embeddings for demo run compatibility
    embeddings_matrix = tfidf_matrix.toarray()
    print("Sentence Transformers not installed. Using TF-IDF array as fallback.")

# ---------------------------------------------------------
# 3. K-Means Clustering & Silhouette Evaluation
# ---------------------------------------------------------
print("\n--- 2. Clustering Evaluation (K=5) ---")
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(embeddings_matrix)

# Compute Silhouette Score
if embeddings_matrix.shape[0] > 5:
    sil_score = silhouette_score(embeddings_matrix, cluster_labels)
    print(f"Calculated Silhouette Coefficient (K=5): {sil_score:.3f}")
    print("Note: Silhouette value > 0.35 indicates reasonable structure and separation.")

# ---------------------------------------------------------
# 4. Search Query Comparison (TF-IDF vs. Embeddings)
# ---------------------------------------------------------
print("\n--- 3. Search Query Retrieval Comparison ---")
search_query = "payment page is failing on checkout"

# TF-IDF Cosine Similarity lookup
t0 = time.time()
query_tfidf = vectorizer.transform([search_query])
tfidf_similarities = cosine_similarity(query_tfidf, tfidf_matrix).flatten()
best_tfidf_idx = np.argmax(tfidf_similarities)
t_tfidf = (time.time() - t0) * 1000

# Embeddings Cosine Similarity lookup
t1 = time.time()
if HAS_SENTENCE_TRANSFORMERS:
    query_emb = model.encode([search_query])
    emb_similarities = cosine_similarity(query_emb, embeddings_matrix).flatten()
    best_emb_idx = np.argmax(emb_similarities)
else:
    best_emb_idx = best_tfidf_idx
    emb_similarities = tfidf_similarities
t_emb = (time.time() - t1) * 1000

print(f"Search Query: '{search_query}'")
print(f"TF-IDF Match      : '{feedback_dataset[best_tfidf_idx]}' (Score: {tfidf_similarities[best_tfidf_idx]:.2f}) | Latency: {t_tfidf:.3f}ms")
print(f"Embeddings Match  : '{feedback_dataset[best_emb_idx]}' (Score: {emb_similarities[best_emb_idx]:.2f}) | Latency: {t_emb:.3f}ms")

# ---------------------------------------------------------
# 5. PCA Compression & 2D Visualization Plot
# ---------------------------------------------------------
print("\n--- 4. Dimensionality Reduction for Visualization ---")
pca = PCA(n_components=2)
reduced_2d = pca.fit_transform(embeddings_matrix)

try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(reduced_2d[:, 0], reduced_2d[:, 1], c=cluster_labels, cmap='plasma', s=80, edgecolors='black')
    plt.colorbar(scatter, label='Cluster ID')
    plt.title("FeedLoop AI - 2D Feedback Clustering Space", fontsize=12, fontweight='bold')
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig("clusters_2d_space.png")
    print("Successfully generated 2D cluster visualization graph: 'clusters_2d_space.png'")
except ImportError:
    print("Matplotlib not found. Skipped exporting visual cluster plot image.")
