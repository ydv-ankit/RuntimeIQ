# app/metrics.py

from prometheus_client import Counter, Gauge, Histogram

runs_started = Counter(
    "runtimeiq_runs_started_total",
    "Total number of runs started",
)

runs_completed = Counter(
    "runtimeiq_runs_completed_total",
    "Total number of runs completed",
)

runs_failed = Counter(
    "runtimeiq_runs_failed_total",
    "Total number of runs failed",
)

runs_recovered = Counter(
    "runtimeiq_runs_recovered_total",
    "Total number of runs recovered",
)

active_runs = Gauge(
    "runtimeiq_active_runs",
    "Number of runs currently executing",
    ["worker_id"]
)

run_duration = Histogram(
    "runtimeiq_run_duration_seconds",
    "Run execution duration in seconds",
    buckets=[
        1,
        5,
        10,
        30,
        60,
        120,
        180,
        300,
        600,
    ],
)

queue_depth = Gauge(
    "runtimeiq_queue_depth",
    "Number of runs waiting in the Redis queue",
)