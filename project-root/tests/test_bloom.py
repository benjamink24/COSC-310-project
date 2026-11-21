import math

import pytest

from app.bloom import UsernameBloomFilter


@pytest.fixture
def bloom():
    return UsernameBloomFilter(expected_users=1000, false_positive_rate=0.01)


# --- Initialization / sizing -------------------------------------------------


def test_init_stores_parameters(bloom):
    assert bloom.expected_users == 1000
    assert bloom.false_positive_rate == 0.01


def test_init_calculates_expected_size_and_hash_count(bloom):
    # m = -(n * ln p) / (ln 2)^2, k = (m / n) * ln 2
    expected_size = int(-(1000 * math.log(0.01)) / (math.log(2) ** 2))
    assert bloom.size == expected_size
    assert bloom.hash_count == max(1, int((expected_size / 1000) * math.log(2)))


def test_init_bit_array_is_zeroed_and_sized_in_bytes(bloom):
    assert len(bloom.bit_array) == math.ceil(bloom.size / 8)
    assert not any(bloom.bit_array)


def test_lower_false_positive_rate_uses_more_bits_and_hashes():
    loose = UsernameBloomFilter(1000, 0.1)
    strict = UsernameBloomFilter(1000, 0.001)
    assert strict.size > loose.size
    assert strict.hash_count > loose.hash_count


def test_more_expected_users_uses_more_bits():
    small = UsernameBloomFilter(100, 0.01)
    large = UsernameBloomFilter(10000, 0.01)
    assert large.size > small.size


def test_hash_count_is_at_least_one():
    tiny = UsernameBloomFilter(expected_users=1, false_positive_rate=0.99)
    assert tiny.hash_count >= 1


# --- add / might_exist -------------------------------------------------------


def test_empty_filter_reports_nothing_exists(bloom):
    assert bloom.might_exist("alice") is False
    assert bloom.might_exist("bob") is False


def test_added_username_might_exist(bloom):
    bloom.add("alice")
    assert bloom.might_exist("alice") is True


def test_add_sets_bits_in_array(bloom):
    bloom.add("alice")
    assert any(bloom.bit_array)


def test_adding_same_username_twice_is_idempotent(bloom):
    bloom.add("alice")
    snapshot = bytes(bloom.bit_array)
    bloom.add("alice")
    assert bytes(bloom.bit_array) == snapshot


def test_no_false_negatives(bloom):
    usernames = [f"user_{i}" for i in range(1000)]
    for name in usernames:
        bloom.add(name)
    assert all(bloom.might_exist(name) for name in usernames)


def test_unrelated_username_is_available_in_sparse_filter(bloom):
    bloom.add("alice")
    assert bloom.might_exist("definitely_not_added_xyz") is False


# --- Normalization -----------------------------------------------------------


def test_check_is_case_insensitive(bloom):
    bloom.add("Admin")
    assert bloom.might_exist("admin") is True
    assert bloom.might_exist("ADMIN") is True


def test_add_is_case_insensitive(bloom):
    bloom.add("ADMIN")
    assert bloom.might_exist("admin") is True


def test_surrounding_whitespace_is_ignored(bloom):
    bloom.add("  alice  ")
    assert bloom.might_exist("alice") is True
    assert bloom.might_exist("\talice\n") is True


def test_inner_whitespace_is_significant(bloom):
    bloom.add("al ice")
    assert bloom.might_exist("alice") is False


def test_unicode_usernames_are_supported(bloom):
    bloom.add("josé")
    bloom.add("用户")
    assert bloom.might_exist("josé") is True
    assert bloom.might_exist("JOSÉ") is True
    assert bloom.might_exist("用户") is True


# --- Hashing -----------------------------------------------------------------


def test_hashes_yield_hash_count_indices(bloom):
    indices = list(bloom._hashes("alice"))
    assert len(indices) == bloom.hash_count


def test_hash_indices_are_within_bit_array_bounds(bloom):
    for name in ["alice", "bob", "x", "a" * 500, "josé"]:
        for index in bloom._hashes(name):
            assert 0 <= index < bloom.size


def test_hashes_are_deterministic(bloom):
    assert list(bloom._hashes("alice")) == list(bloom._hashes("alice"))


def test_hashes_are_deterministic_across_instances():
    a = UsernameBloomFilter(1000, 0.01)
    b = UsernameBloomFilter(1000, 0.01)
    assert list(a._hashes("alice")) == list(b._hashes("alice"))


def test_hashes_normalize_input(bloom):
    assert list(bloom._hashes("Alice ")) == list(bloom._hashes("alice"))


def test_different_usernames_produce_different_indices(bloom):
    assert list(bloom._hashes("alice")) != list(bloom._hashes("bob"))


# --- clear -------------------------------------------------------------------


def test_clear_resets_filter(bloom):
    bloom.add("alice")
    bloom.add("bob")
    bloom.clear()
    assert not any(bloom.bit_array)
    assert bloom.might_exist("alice") is False
    assert bloom.might_exist("bob") is False


def test_clear_preserves_size_and_hash_count(bloom):
    size, hash_count, length = bloom.size, bloom.hash_count, len(bloom.bit_array)
    bloom.add("alice")
    bloom.clear()
    assert bloom.size == size
    assert bloom.hash_count == hash_count
    assert len(bloom.bit_array) == length


def test_filter_is_usable_after_clear(bloom):
    bloom.add("alice")
    bloom.clear()
    bloom.add("carol")
    assert bloom.might_exist("carol") is True


# --- False positive rate -----------------------------------------------------


def test_false_positive_rate_is_near_configured_target():
    n = 1000
    target = 0.01
    bloom = UsernameBloomFilter(expected_users=n, false_positive_rate=target)

    for i in range(n):
        bloom.add(f"present_{i}")

    trials = 10000
    false_positives = sum(
        bloom.might_exist(f"absent_{i}") for i in range(trials)
    )
    observed = false_positives / trials

    # Allow generous headroom (3x) so the test is stable but still catches
    # a broken hashing scheme.
    assert observed <= target * 3