__test__ = {"doctest": """
Test key validation

>>> u = User()
>>> k = '5fazal'
>>> u.key = k
>>> u.sections = ['b']
>>> valid_key(k)
>>> valid_key(k, 'b')
>>> valid_key(k, post=Post.objects.get(pk=1))
>>> valid_key(k, post=1)
>>> valid_key(k, section='b', post=2)
"""}

