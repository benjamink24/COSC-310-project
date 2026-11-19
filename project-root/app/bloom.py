import hashlib
import math


class UsernameBloomFilter:

    def __init__(self, expected_users: int, false_positive_rate: float = 0.01):
        """
        Initialize the Bloom filter.
        :param expected_users: Estimated number of usernames to store.
        :param false_positive_rate: Desired false positive probability (e.g., 0.01 for 1%).
        """
        self.expected_users = expected_users
        self.false_positive_rate = false_positive_rate

        # Calculate optimal bit array size (m) and number of hash functions (k)
        self.size = self._get_size(expected_users, false_positive_rate)
        self.hash_count = self._get_hash_count(self.size, expected_users)

        # Use a bytearray for memory efficiency (1 bit per entry via bitwise ops)
        self.bit_array = bytearray(math.ceil(self.size / 8))

    def _get_size(self, n: int, p: float) -> int:
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return int(m)

    def _get_hash_count(self, m: int, n: int) -> int:
        k = (m / n) * math.log(2)
        return max(1, int(k))

    def _hashes(self, username: str):
        """Generate k hash indices using double hashing (SHA-256)."""
        # Normalize username so 'Admin' and 'admin' map to the same bits
        normalized = username.strip().lower().encode("utf-8")
        digest = hashlib.sha256(normalized).digest()

        # Split the 32-byte SHA-256 digest into two 128-bit integers
        h1 = int.from_bytes(digest[:16], "big")
        h2 = int.from_bytes(digest[16:], "big")

        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size

    def add(self, username: str):
        """Add a taken username to the filter."""
        for index in self._hashes(username):
            byte_index = index // 8
            bit_offset = index % 8
            self.bit_array[byte_index] |= 1 << bit_offset

    def might_exist(self, username: str) -> bool:
        """
        Check if a username is likely taken.
        Returns False -> Definitely available (100% certain).
        Returns True  -> Probably taken (check database to confirm).
        """
        for index in self._hashes(username):
            byte_index = index // 8
            bit_offset = index % 8
            if not (self.bit_array[byte_index] & (1 << bit_offset)):
                return False
        return True