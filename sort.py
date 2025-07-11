def radix_sort_depth(arr):
    if not arr:
        return []

    normalized = [
        (x if isinstance(x, int) else x[0], i if isinstance(x, int) else x[1])
        for i, x in enumerate(arr)
    ]

    max_val = max(normalized, key=lambda x: x[0])[0]
    exp = 1

    output = normalized[:]

    while max_val // exp > 0:
        buckets = [[] for _ in range(10)]

        for num in output:
            index = (num[0] // exp) % 10
            buckets[index].append(num)

        output = []
        for i in reversed(range(10)):
            output.extend(buckets[i])

        exp *= 10

    return output
