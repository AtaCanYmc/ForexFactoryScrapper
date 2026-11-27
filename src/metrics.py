import threading
from collections import defaultdict

BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)

_lock = threading.Lock()
_requests = defaultdict(int)  # (method, route, status) -> count
_latency = {}  # (method, route) -> [bucket counts..., sum, count]
_counters = defaultdict(int)


def inc(name, n=1):
    with _lock:
        _counters[name] += n


def observe(method, route, status, seconds):
    with _lock:
        _requests[(method, route, str(status))] += 1
        h = _latency.setdefault((method, route), [0] * len(BUCKETS) + [0.0, 0])
        for i, bound in enumerate(BUCKETS):
            if seconds <= bound:
                h[i] += 1
        h[-2] += seconds
        h[-1] += 1


def render():
    """Prometheus text exposition format (v0.0.4)."""
    out = ["# TYPE ffs_http_requests_total counter"]
    with _lock:
        for (m, r, s), n in sorted(_requests.items()):
            out.append(
                f'ffs_http_requests_total{{method="{m}",route="{r}",status="{s}"}} {n}'
            )
        out.append("# TYPE ffs_http_request_duration_seconds histogram")
        for (m, r), h in sorted(_latency.items()):
            lbl = f'method="{m}",route="{r}"'
            for bound, n in zip(BUCKETS, h):
                out.append(
                    f'ffs_http_request_duration_seconds_bucket{{{lbl},le="{bound}"}} {n}'
                )
            out.append(
                f'ffs_http_request_duration_seconds_bucket{{{lbl},le="+Inf"}} {h[-1]}'
            )
            out.append(f"ffs_http_request_duration_seconds_sum{{{lbl}}} {h[-2]:.6f}")
            out.append(f"ffs_http_request_duration_seconds_count{{{lbl}}} {h[-1]}")
        hits, misses = _counters["cache_hits"], _counters["cache_misses"]
        out += [
            "# TYPE ffs_cache_hits_total counter",
            f"ffs_cache_hits_total {hits}",
            "# TYPE ffs_cache_misses_total counter",
            f"ffs_cache_misses_total {misses}",
            "# TYPE ffs_cache_hit_ratio gauge",
            f"ffs_cache_hit_ratio {hits / (hits + misses) if hits + misses else 0:.4f}",
            "# TYPE ffs_rate_limit_rejections_total counter",
            f"ffs_rate_limit_rejections_total {_counters['rate_limited']}",
        ]
    return "\n".join(out) + "\n"
