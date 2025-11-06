import numpy as np
import sys
from sklearn.mixture import GaussianMixture

def findPhyLRange(txt: str, random_seed: int = 42) -> tuple:
    """
    Uses the Gaussian Mixture Model (GMM) algorithm to fit the character counts of OCR text 
    into a mixture of two normal distributions.

    Assumptions:
    1. The data is a mixture of 2 normal distributions.
    2. Physical lines: high mean, low variance.
    3. Semantic lines: low mean, high variance.

    Parameters:
    txt (str): The input string containing the OCR text.
    random_seed (int): Ensures that the GMM results are consistent (reproducible) across runs.

    Returns:
    tuple: (min_range, max_range), representing the character count range of physical lines.
    """
    
    char_counts = []
    
    lines = txt.splitlines()
    for line in lines:
        count = len(line)
        if count > 0:
            char_counts.append(count)

    if len(char_counts) < 2:
        print("Error: Not enough data points (fewer than 2) for GMM fitting.")
        return (None, None)

    # GMM requires a 2D array [n_samples, n_features]
    # Our 1D data needs to be reshaped
    counts_array_1d = np.array(char_counts)
    counts_array_2d = counts_array_1d.reshape(-1, 1)

    # --- Step 2: Initialize GMM ---
    # To help GMM converge correctly, we manually initialize the means of the two clusters.
    # Assume "semantic lines" are around the 25th percentile and "physical lines" are around the 75th percentile.
    # This is a more robust initialization than K-Means.
    q25 = np.percentile(counts_array_1d, 25)
    q75 = np.percentile(counts_array_1d, 75)
    
    # Avoid q25 and q75 being exactly the same
    if q25 == q75:
            q25 = np.min(counts_array_1d)
            q75 = np.max(counts_array_1d)
            if q25 == q75: # Still the same, meaning all data points are identical
                return (int(q25), int(q75))

    # The 'means_init' parameter for GMM
    initial_means = np.array([q25, q75]).reshape(-1, 1)

    # Create the model
    # n_components=2: Find two distributions
    # means_init=...: Provide initial guesses
    # random_state=...: Ensure reproducible results
    gmm = GaussianMixture(n_components=2, 
                            means_init=initial_means, 
                            random_state=random_seed)

    # --- Step 3: Fit the model ---
    gmm.fit(counts_array_2d)

    # --- Step 4: Identify the "physical line" cluster ---
    # gmm.means_ is a 2D array, e.g., [[28.5], [69.1]]
    # .flatten() converts it to 1D, e.g., [28.5, 69.1]
    cluster_means = gmm.means_.flatten()
    
    # The physical line cluster is the one with the higher mean
    # np.argmax returns the index of the maximum value (0 or 1)
    physical_cluster_index = np.argmax(cluster_means)
    
    # (Optional) Check if the standard deviation matches the assumption
    # variances = gmm.covariances_.flatten()
    # physical_std = np.sqrt(variances[physical_cluster_index])
    # print(f"Physical Cluster: Mean={cluster_means[physical_cluster_index]:.1f}, StdDev={physical_std:.1f}")

    # --- Step 5: Predict and filter ---
    # Let GMM make a "hard prediction" for all data points
    # (i.e., determine which cluster each point is most likely to belong to)
    predictions = gmm.predict(counts_array_2d)

    # Filter out all original data points predicted as "physical lines"
    physical_line_counts = counts_array_1d[predictions == physical_cluster_index]

    if physical_line_counts.size == 0:
        print(f"Error: GMM fitting succeeded, but no points were classified as 'physical lines'.")
        return (None, None)

    # --- Step 6: Output the result ---
    min_range = int(np.min(physical_line_counts))
    max_range = int(np.max(physical_line_counts))

    return (min_range, max_range)


