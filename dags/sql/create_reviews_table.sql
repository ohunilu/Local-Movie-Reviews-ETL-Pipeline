CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    movie VARCHAR(100),
    rating INT,
    review_text TEXT,
    review_time TIMESTAMP
);
