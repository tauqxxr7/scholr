counters = {
    "provider_generation_success_count": 0,
    "provider_generation_failure_count": 0,
    "fallback_count": 0,
    "cache_hit_count": 0,
}


def increment(key: str):
    if key in counters:
        counters[key] += 1


def get_all() -> dict:
    return dict(counters)
