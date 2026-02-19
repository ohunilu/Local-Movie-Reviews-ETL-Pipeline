CREATE TABLE IF NOT EXISTS daily_stats AS
SELECT movie, AVG(rating) as avg_rating, COUNT(*) as review_count
FROM reviews
GROUP BY movie;
