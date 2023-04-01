def clothes_by_temperature(temperature: float) -> str:
    if temperature <= 5:
        return "패딩, 두꺼운 코트, 목도리, 기모제품"
    if temperature <= 9:
        return "코트, 가죽재킷, 니트, 스카프, 두꺼운 바지"
    if temperature <= 11:
        return "재킷, 트랜치코트, 니트, 면바지, 청바지, 검은색 스타킹"
    if temperature <= 16:
        return "얇은 재킷, 가디건, 간절기 야상, 맨투맨, 니트, 살구색 스타킹"
    if temperature <= 19:
        return "얇은 니트, 얇은 재킷, 가디건, 맨투맨, 면바지, 청바지"
    if temperature <= 22:
        return "긴팔티, 얇은 가디건, 면바지, 청바지"
    if temperature <= 26:
        return "반팔티, 얇은 셔츠, 반바지, 면바지"
    return "민소매티, 반바지, 반팔티, 치마"
