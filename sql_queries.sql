-- 1. Overall class balance
SELECT toxic, COUNT(*) AS comments, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM comments
GROUP BY toxic;

-- 2. Average comment length by class
SELECT toxic, ROUND(AVG(char_length), 1) AS avg_characters, MAX(char_length) AS max_characters
FROM comments
GROUP BY toxic;

-- 3. Longest comments
SELECT comment_id, toxic, char_length, substr(comment_text, 1, 180) AS preview
FROM comments
ORDER BY char_length DESC
LIMIT 10;

-- 4. Experiment leaderboard
SELECT model_name, vectorizer, roc_auc, f1, precision, recall, trained_at
FROM model_runs
ORDER BY roc_auc DESC, f1 DESC;

-- 5. Confusion matrix cells for each model
SELECT r.model_name, p.actual, p.predicted, COUNT(*) AS observations
FROM predictions p
JOIN model_runs r ON r.run_id = p.run_id
GROUP BY r.model_name, p.actual, p.predicted
ORDER BY r.model_name, p.actual, p.predicted;

-- 6. Highest-confidence false positives
SELECT r.model_name, p.probability, c.char_length, substr(c.comment_text, 1, 220) AS preview
FROM predictions p
JOIN comments c ON c.comment_id = p.comment_id
JOIN model_runs r ON r.run_id = p.run_id
WHERE p.actual = 0 AND p.predicted = 1
ORDER BY p.probability DESC
LIMIT 15;

-- 7. Highest-confidence false negatives
SELECT r.model_name, p.probability, c.char_length, substr(c.comment_text, 1, 220) AS preview
FROM predictions p
JOIN comments c ON c.comment_id = p.comment_id
JOIN model_runs r ON r.run_id = p.run_id
WHERE p.actual = 1 AND p.predicted = 0
ORDER BY p.probability ASC
LIMIT 15;

-- 8. Per-model ranking with a CTE and window function
WITH ranked AS (
  SELECT model_name, roc_auc, f1,
         RANK() OVER (ORDER BY roc_auc DESC, f1 DESC) AS model_rank
  FROM model_runs
)
SELECT model_rank, model_name, ROUND(roc_auc, 4) AS roc_auc, ROUND(f1, 4) AS f1
FROM ranked
ORDER BY model_rank;

