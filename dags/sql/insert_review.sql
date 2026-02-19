INSERT INTO reviews (movie, rating, review_text, review_time)
VALUES (%s, %s, %s, to_timestamp(%s))
ON CONFLICT DO NOTHING;
