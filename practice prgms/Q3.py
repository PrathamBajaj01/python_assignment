data = [12, 24, 35, 24, 88, 120, 155, 88, 120, 155]

s = set()
result = []

for item in data:
    if item not in s:
        s.add(item)
        result.append(item)

print(result)
