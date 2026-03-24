-- drop and recreate
DROP TABLE IF EXISTS traffic_observations CASCADE;

CREATE TABLE traffic_observations (
    id                SERIAL PRIMARY KEY,
    intersection_id   VARCHAR(50),
    timestamp         TIMESTAMP,
    traffic_volume    INTEGER,
    avg_speed         FLOAT,
    count_cars        INTEGER,
    count_trucks      INTEGER,
    count_bikes       INTEGER,
    weather_condition VARCHAR(50),
    temperature       FLOAT,
    humidity          FLOAT,
    accident_reported VARCHAR(10),
    signal_phase      VARCHAR(20)
);

CREATE INDEX idx_timestamp      ON traffic_observations(timestamp);
CREATE INDEX idx_intersection   ON traffic_observations(intersection_id);
CREATE INDEX idx_signal_phase   ON traffic_observations(signal_phase);
