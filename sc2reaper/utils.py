def split(a, n):
    """
    Returns a generator with n chunks of list a.
    
    Taken from: https://stackoverflow.com/a/2135920
    """
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))